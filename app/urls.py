
import sqlite3

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from connection import get_connection


router = APIRouter()



# --------------------------------------------------
# 1. AUTHENTICATION
# --------------------------------------------------

def get_current_user(
    authorization: str = Header(default=None)
):
    print("Authorization received:", authorization)
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )

    scheme, separator, token = authorization.partition(" ")

    if not separator or scheme.lower() != "bearer" or not token.strip():
        raise HTTPException(
            status_code=401,
            detail="Invalid bearer token format"
        )

    token = token.strip()

    conn = get_connection()

    try:
        user = conn.execute(
            """
            SELECT
                api_tokens.user,
                api_tokens.merchant_id,
                merchants.name AS merchant_name
            FROM api_tokens
            LEFT JOIN merchants
                ON api_tokens.merchant_id = merchants.id
            WHERE api_tokens.token = ?
            """,
            (token,)
        ).fetchone()

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid bearer token"
            )

        return {
            "user": user["user"],
            "merchant_id": user["merchant_id"],
            "merchant": (
                {
                    "id": user["merchant_id"],
                    "name": user["merchant_name"]
                }
                if user["merchant_id"] else None
            )
        }

    finally:
        conn.close()


# --------------------------------------------------
# 2. REQUEST SCHEMA
# --------------------------------------------------

class OrderAction(BaseModel):
    id: str = Field(min_length=1)


# --------------------------------------------------
# 3. AUTH ME
# --------------------------------------------------

@router.get("/auth/me")
def auth_me(
    current_user: dict = Depends(get_current_user)
):
    return {
        "user": current_user["user"],
        "merchant": current_user["merchant"]
    }


# --------------------------------------------------
# 4. LIST ORDERS
# --------------------------------------------------

@router.get("/orders")
def get_orders(
    status: str = None,
    current_user: dict = Depends(get_current_user)
):
    merchant_id = current_user["merchant_id"]

    # A valid token without a merchant has no store access.
    if merchant_id is None:
        return []

    allowed_statuses = {
        "PLACED", "PAID", "SHIPPED",
        "DELIVERED", "CANCELLED", "REFUNDED"
    }

    if status is not None:
        status = status.upper()

        if status not in allowed_statuses:
            raise HTTPException(
                status_code=400,
                detail="Invalid order status"
            )

    conn = get_connection()

    try:
        if status:
            rows = conn.execute(
                """
                SELECT * FROM orders
                WHERE merchant = ? AND status = ?
                ORDER BY placed_at DESC
                """,
                (merchant_id, status)
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM orders
                WHERE merchant = ?
                ORDER BY placed_at DESC
                """,
                (merchant_id,)
            ).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# --------------------------------------------------
# 5. LEGACY ORDER LOOKUP
# --------------------------------------------------

@router.get("/orders/lookup")
def lookup_order(
    id: str,
    current_user: dict = Depends(get_current_user)
):
    merchant_id = current_user["merchant_id"]

    conn = get_connection()

    try:
        order = None

        if merchant_id is not None:
            order = conn.execute(
                """
                SELECT * FROM orders
                WHERE id = ? AND merchant = ?
                """,
                (id, merchant_id)
            ).fetchone()

        # IMPORTANT:
        # Always return HTTP 200 for lookup failures.
        if order is None:
            return {
                "status": False,
                "message": "Order not found"
            }

        return {
            "status": True,
            "data": dict(order)
        }

    finally:
        conn.close()


# --------------------------------------------------
# 6. REFUND ORDER
# --------------------------------------------------

@router.post("/orders/refund")
def refund_order(
    action: OrderAction,
    current_user: dict = Depends(get_current_user)
):
    merchant_id = current_user["merchant_id"]

    if merchant_id is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    conn = get_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")

        order = conn.execute(
            """
            SELECT * FROM orders
            WHERE id = ? AND merchant = ?
            """,
            (action.id, merchant_id)
        ).fetchone()

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order["status"] not in (
            "PAID", "SHIPPED", "DELIVERED"
        ):
            raise HTTPException(
                status_code=409,
                detail=f"Cannot refund an order with status {order['status']}"
            )

        conn.execute(
            """
            UPDATE orders
            SET status = 'REFUNDED'
            WHERE id = ? AND merchant = ?
            """,
            (action.id, merchant_id)
        )

        conn.commit()

        return {
            "status": True,
            "message": "Order refunded successfully",
            "order_id": action.id
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


# --------------------------------------------------
# 7. CANCEL ORDER
# --------------------------------------------------

@router.post("/orders/cancel")
def cancel_order(
    action: OrderAction,
    current_user: dict = Depends(get_current_user)
):
    merchant_id = current_user["merchant_id"]

    if merchant_id is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    conn = get_connection()

    try:
        conn.execute("BEGIN IMMEDIATE")

        order = conn.execute(
            """
            SELECT * FROM orders
            WHERE id = ? AND merchant = ?
            """,
            (action.id, merchant_id)
        ).fetchone()

        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )

        if order["status"] not in ("PLACED", "PAID"):
            raise HTTPException(
                status_code=409,
                detail=f"Cannot cancel an order with status {order['status']}"
            )

        conn.execute(
            """
            UPDATE orders
            SET status = 'CANCELLED'
            WHERE id = ? AND merchant = ?
            """,
            (action.id, merchant_id)
        )

        conn.commit()

        return {
            "status": True,
            "message": "Order cancelled successfully",
            "order_id": action.id
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

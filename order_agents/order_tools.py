
import os
import httpx

from fastapi import Header

from langgraph.types import interrupt

from dotenv import load_dotenv

load_dotenv()

STORE_API_BASE_URL = os.getenv(
    "STORE_API_BASE_URL",
    "http://127.0.0.1:8000"
)


class StoreAPIError(Exception):
    pass


async def call_store_api(
    method: str,
    endpoint: str,
    authorization: str,
    params=None,
    json_body=None
):
    """
    Communicate with the existing ShopHub Store API.
    """

    if not authorization:
        raise StoreAPIError(
            "Authorization token is missing."
        )

    headers = {
        "Authorization": authorization
    }

    async with httpx.AsyncClient(timeout=30.0) as client:

        try:
            response = await client.request(
                method=method,
                url=f"{STORE_API_BASE_URL}{endpoint}",
                headers=headers,
                params=params,
                json=json_body
            )

        except httpx.RequestError as exc:
            raise StoreAPIError(
                f"Could not connect to Store API: {str(exc)}"
            )

    try:
        data = response.json()
    except ValueError:
        data = {
            "message": response.text
        }

    # Check HTTP-level failure.
    if response.status_code >= 400:

        if isinstance(data, dict):
            message = (
                data.get("detail")
                or data.get("message")
                or "Store API request failed."
            )
        else:
            message = "Store API request failed."

        raise StoreAPIError(
            f"HTTP {response.status_code}: {message}"
        )

    # IMPORTANT:
    # HTTP 200 does not always mean business success.
    if isinstance(data, dict) and data.get("status") is False:

        message = data.get(
            "message",
            "The Store API operation failed."
        )

        raise StoreAPIError(message)

    return data


async def get_orders(
    authorization: str,
    status: str = None
):
    
    params = {}

    if status:
        params["status"] = status

    return await call_store_api(
        method="GET",
        endpoint="/orders",
        authorization=authorization,
        params=params
    )


async def lookup_order(
    authorization: str,
    order_id: str
):
    return await call_store_api(
        method="GET",
        endpoint="/orders/lookup",
        authorization=authorization,
        params={
            "id": order_id
        }
    )


async def refund_order(
    authorization: str,
    order_id: str
):
    decision = interrupt({
        "type": "refund_approval",
        "order_id": order_id,
        "message": "Waiting for merchant approval"
    })

    if decision != "approve":
        return "Refund rejected by merchant."
    
    return await call_store_api(
        method="POST",
        endpoint="/orders/refund",
        authorization=authorization,
        json_body={
            "id": order_id
        }
    )


async def cancel_order(
    authorization: str,
    order_id: str
):
    return await call_store_api(
        method="POST",
        endpoint="/orders/cancel",
        authorization=authorization,
        json_body={
            "id": order_id
        }
    )

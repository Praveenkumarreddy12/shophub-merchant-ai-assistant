
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .order_tools import (
    get_orders,
    lookup_order,
    refund_order,
    cancel_order,
    StoreAPIError
)


app = FastAPI(
    title="ShopHub Orders Agent",
    version="1.0.0"
)


CARD_PATH = (
    Path(__file__).parent / "agent_card.json"
)


class JSONRPCRequest(BaseModel):
    jsonrpc: str
    method: str
    params: dict[str, Any] = {}
    id: str | int | None


@app.get("/health")
def health():
    return {
        "status": "running",
        "agent": "ShopHub Orders Agent"
    }


@app.get("/agent-card.json")
def get_agent_card():

    with open(CARD_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


@app.post("/rpc")
async def rpc_endpoint(request: JSONRPCRequest):

    # Validate JSON-RPC version.
    if request.jsonrpc != "2.0":
        return JSONResponse(
            status_code=200,
            content={
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid JSON-RPC version."
                },
                "id": request.id
            }
        )

    params = request.params

    # The orchestrator forwards the original
    # Authorization header through JSON-RPC params.
    authorization = params.get("authorization")

    if not authorization:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32001,
                "message": "Authorization header is required."
            },
            "id": request.id
        }

    try:

        if request.method == "get_orders":

            result = await get_orders(
                authorization=authorization,
                status=params.get("status")
            )

        elif request.method == "lookup_order":

            order_id = params.get("order_id")

            if not order_id:
                raise ValueError("order_id is required.")

            result = await lookup_order(
                authorization=authorization,
                order_id=str(order_id)
            )

        elif request.method == "refund_order":

            order_id = params.get("order_id")

            if not order_id:
                raise ValueError("order_id is required.")

            result = await refund_order(
                authorization=authorization,
                order_id=str(order_id)
            )

        elif request.method == "cancel_order":

            order_id = params.get("order_id")

            if not order_id:
                raise ValueError("order_id is required.")

            result = await cancel_order(
                authorization=authorization,
                order_id=str(order_id)
            )

        else:

            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": "Method not found."
                },
                "id": request.id
            }

        return {
            "jsonrpc": "2.0",
            "result": {
                "status": True,
                "data": result
            },
            "id": request.id
        }

    except StoreAPIError as exc:

        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": str(exc)
            },
            "id": request.id
        }

    except ValueError as exc:

        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,
                "message": str(exc)
            },
            "id": request.id
        }

    except Exception as exc:

        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal agent error: {str(exc)}"
            },
            "id": request.id
        }


import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool

from langchain.agents import create_agent

from orchestrator.a2a_client import A2AClient


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

AGENT_CARD_URL = os.getenv(
    "ORDERS_AGENT_CARD_URL",
    "http://127.0.0.1:8001/agent-card.json"
)


SYSTEM_PROMPT = """
You are ShopHub Merchant AI Assistant.

You help merchants manage their store orders.

You have access to remote order tools.

HUMAN APPROVAL RULES:

1. Never execute refund_order directly.
2. Never execute cancel_order directly.
3. First collect order details:
   - Order ID
   - Merchant
   - Action
   - Amount

4. Create an approval proposal.

5. Wait for explicit human approval.

6. If approved, execute the requested tool.

7. If rejected, do not execute the tool.

8. Never assume approval from the user's original request.

IMPORTANT RULES:

1. Use the appropriate tool when the user asks about orders.
2. Never invent order details.
3. Never claim an operation succeeded unless the tool confirms success.
4. If a tool returns an error, explain the actual error clearly.
5. If an order is not found, tell the user that the order was not found.
6. If authentication fails, ask the user to verify their credentials.
7. Do not expose authorization tokens.
8. Explain tool failures in simple language.
9. For order refunds and cancellations, use the appropriate tool.
10. Answer conversational questions directly when no tool is needed.

Always give useful, clear answers.
"""


def build_agent(
    authorization: str,
    checkpointer
):
    """
    Build a LangGraph agent with remote A2A tools.

    The authorization token is captured in the tool
    closures and is not exposed as an LLM tool argument.
    """

    a2a_client = A2AClient(
        agent_card_url=AGENT_CARD_URL
    )

    async def remote_call(method, params):

        return await a2a_client.call_agent(
            method=method,
            params={
                **params,
                "authorization": authorization
            }
        )

    @tool
    async def get_orders(status: str = "") -> str:
        """
        Retrieve the authenticated merchant's orders.

        Optional status values include PLACED,
        SHIPPED, DELIVERED and CANCELLED.
        """

        result = await remote_call(
            "get_orders",
            {
                "status": status or None
            }
        )

        return str(result)

    @tool
    async def lookup_order(order_id: str) -> str:
        """
        Find a particular order using its order ID.
        """

        result = await remote_call(
            "lookup_order",
            {
                "order_id": order_id
            }
        )

        return str(result)

    @tool
    async def refund_order(order_id: str) -> str:
        """
        Request a refund for an eligible order.
        """

        result = await remote_call(
            "refund_order",
            {
                "order_id": order_id
            }
        )

        return str(result)

    @tool
    async def cancel_order(order_id: str) -> str:
        """
        Cancel an eligible order.
        """

        result = await remote_call(
            "cancel_order",
            {
                "order_id": order_id
            }
        )

        return str(result)

    tools = [
        get_orders,
        lookup_order,
        refund_order,
        cancel_order
    ]

    llm = ChatGroq(
        model=GROQ_MODEL,
        temperature=0,
        api_key=GROQ_API_KEY,
        streaming=True
    )

    graph = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )

    return graph

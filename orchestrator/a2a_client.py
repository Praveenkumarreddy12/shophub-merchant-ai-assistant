
import httpx


class A2AClient:

    def __init__(self, agent_card_url: str):
        self.agent_card_url = agent_card_url
        self.agent_card = None

    async def discover_agent(self):
        """
        Discover the remote agent using its agent card.
        """

        async with httpx.AsyncClient(timeout=15.0) as client:

            response = await client.get(
                self.agent_card_url
            )

            response.raise_for_status()

            self.agent_card = response.json()

        return self.agent_card

    async def call_agent(
        self,
        method: str,
        params: dict
    ):
        """
        Send a JSON-RPC 2.0 request to the discovered agent.
        """

        if not self.agent_card:
            await self.discover_agent()

        endpoint = self.agent_card["url"]

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }

        async with httpx.AsyncClient(timeout=40.0) as client:

            response = await client.post(
                endpoint,
                json=payload
            )

            response.raise_for_status()

            rpc_response = response.json()

        if rpc_response.get("error"):

            error = rpc_response["error"]

            raise RuntimeError(
                error.get(
                    "message",
                    "Remote agent operation failed."
                )
            )

        result = rpc_response.get("result")

        if not isinstance(result, dict):
            raise RuntimeError(
                "Invalid JSON-RPC response from Orders Agent."
            )

        # Second-level validation:
        # JSON-RPC success must also contain business success.
        if result.get("status") is False:
            raise RuntimeError(
                result.get(
                    "message",
                    "Orders operation failed."
                )
            )

        return result.get("data")


import os
import json

from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse

from pydantic import BaseModel

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from orchestrator.agent import build_agent


load_dotenv()


DB_PATH = os.getenv(
    "ORCHESTRATOR_DB_PATH",
    "data/conversations.db"
)


def sse_event(event_name: str, data: dict):
    """
    Format a Server-Sent Event.
    """

    return (
        f"event: {event_name}\n"
        f"data: {json.dumps(data, default=str)}\n\n"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Ensure database directory exists.
    Path(DB_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Keep the SQLite connection alive
    # throughout the application lifetime.
    async with AsyncSqliteSaver.from_conn_string(
        DB_PATH
    ) as checkpointer:

        await checkpointer.setup()

        app.state.checkpointer = checkpointer

        yield


app = FastAPI(
    title="ShopHub AI Orchestrator",
    version="1.0.0",
    lifespan=lifespan
)


class ChatRequest(BaseModel):

    message: str

    thread_id: str


@app.get("/health")
def health():

    return {
        "status": "running",
        "agent": "ShopHub LangGraph Orchestrator",
        "persistence": "SQLite"
    }


def extract_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, dict):

                if item.get("type") == "text":
                    parts.append(item.get("text", ""))

        return "".join(parts)

    return ""


@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    authorization: str | None = Header(default=None)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required."
        )

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    if not request.thread_id.strip():
        raise HTTPException(
            status_code=400,
            detail="thread_id cannot be empty."
        )

    # Build agent with the user's authorization.
    agent = build_agent(
        authorization=authorization,
        checkpointer=app.state.checkpointer
    )

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    async def generate_events():

        try:

            # Stream LangGraph execution events.
            async for event in agent.astream_events(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": request.message
                        }
                    ]
                },
                config=config,
                version="v2"
            ):

                event_type = event.get("event")

                event_name = event.get("name", "")

                event_data = event.get("data", {})

                # Tool started.
                if event_type == "on_tool_start":

                    yield sse_event(
                        "tool_started",
                        {
                            "tool": event_name
                        }
                    )

                # Tool completed.
                elif event_type == "on_tool_end":

                    yield sse_event(
                        "tool_finished",
                        {
                            "tool": event_name,
                            "success": True
                        }
                    )

                # Tool failed.
                elif event_type == "on_tool_error":

                    yield sse_event(
                        "tool_finished",
                        {
                            "tool": event_name,
                            "success": False,
                            "error": str(
                                event_data.get("error", "Tool failed")
                            )
                        }
                    )

                # Stream LLM tokens.
                elif event_type == "on_chat_model_stream":

                    chunk = event_data.get("chunk")

                    if chunk:

                        content = extract_text(
                            chunk.content
                        )

                        if content:

                            yield sse_event(
                                "token",
                                {
                                    "content": content
                                }
                            )

            yield sse_event(
                "done",
                {
                    "thread_id": request.thread_id,
                    "message": "Response completed."
                }
            )

        except Exception as exc:

            yield sse_event(
                "error",
                {
                    "message": str(exc)
                }
            )

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

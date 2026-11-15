
import requests
import json


ORCHESTRATOR_URL = (
    "http://127.0.0.1:8002/chat/stream"
)


def chat(message, thread_id, token):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/event-stream"
    }

    payload = {
        "message": message,
        "thread_id": thread_id
    }

    print("\nUser:", message)
    print("\nAssistant:\n")

    try:

        with requests.post(
            ORCHESTRATOR_URL,
            headers=headers,
            json=payload,
            stream=True,
            timeout=(10, 180)
        ) as response:

            response.raise_for_status()

            current_event = None

            for line in response.iter_lines(
                decode_unicode=True
            ):

                if not line:
                    continue

                if line.startswith("event:"):

                    current_event = line.split(
                        ":", 1
                    )[1].strip()

                elif line.startswith("data:"):

                    raw_data = line.split(
                        ":", 1
                    )[1].strip()

                    data = json.loads(raw_data)

                    if current_event == "tool_started":

                        print(
                            "\n[TOOL STARTED]",
                            data["tool"]
                        )

                    elif current_event == "tool_finished":

                        print(
                            "\n[TOOL FINISHED]",
                            data
                        )

                    elif current_event == "token":

                        print(
                            data["content"],
                            end="",
                            flush=True
                        )

                    elif current_event == "done":

                        print(
                            "\n\n[COMPLETED]",
                            data
                        )

                    elif current_event == "error":

                        print(
                            "\n[ERROR]",
                            data["message"]
                        )

    except requests.RequestException as exc:

        print("Connection error:", exc)


if __name__ == "__main__":

    TOKEN = "fashion_token_123"

    THREAD_ID = "merchant_001_chat_01"

    print("ShopHub AI Assistant")

    while True:

        message = input(
            "\nYou: "
        ).strip()

        if message.lower() in [
            "exit",
            "quit"
        ]:
            break

        if not message:
            continue

        chat(
            message=message,
            thread_id=THREAD_ID,
            token=TOKEN
        )

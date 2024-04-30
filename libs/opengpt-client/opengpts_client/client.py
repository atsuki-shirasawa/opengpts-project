"""OpenGPTs Client"""

import json
import mimetypes
import uuid
from io import BytesIO
from pathlib import Path
from typing import Any, Generator, Optional

import orjson
import requests
from requests.exceptions import HTTPError

from opengpts_client.schema import (
    Assistant,
    Message,
    Thread,
    ThreadHistory,
    ThreadMessages,
)

DEFAULT_TIMEOUT = 10
CHAT_TIMEOUT = 30
INGEST_TIMEOUT = 60


class OpenGPTsClient:
    """OpenGPTs Client"""

    def __init__(
        self,
        url: str = "http://localhost:8100",
        opengpts_user_id: Optional[str] = None,
    ) -> None:
        """コンストラクタ

        Args:
            url (str, optional): url. Defaults to "http://localhost:8100".
            opengpts_user_id (str, optional): \
                opengpts_user_id. Defaults to "None".
        """
        self.url = url
        self.opengpts_user_id = opengpts_user_id or str(uuid.uuid4())

    @property
    def headers(self) -> dict[str, str]:
        """Request headers

        Returns:
            dict[str, str]: Request headers
        """
        return {
            "Content-Type": "application/json",
            "Cookie": f"opengpts_user_id={self.opengpts_user_id}",
        }

    def health(self) -> dict:
        """Health check

        Returns:
            dict: {'status': 'ok'}
        """
        response = requests.get(
            url=f"{self.url}/health",
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT,
        )
        return dict(response.json())

    def ingest_retrivers_files(
        self,
        files: list[Path],
        assistant_id: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[list[str]] = None,
    ) -> dict:
        """Ingest files

        Args:
            files (list[Path]): filepath list
            assistant_id (str): assistant id
            chunk_size (int, optional): chunk size. Defaults to 1000.
            chunk_overlap (int, optional): chunk overlap size. Defaults to 200.
            separators (Optional[list[str]], optional): \
                chunk separators. Defaults to None.
        """
        request_files = [
            (
                "files",
                (
                    file.name,
                    BytesIO(file.read_bytes()),
                    mimetypes.guess_type(file)[0],
                ),
            )
            for file in files
        ]
        payload = {
            "config": json.dumps(
                {
                    "configurable": {
                        "assistant_id": assistant_id,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                        "separators": separators,
                    },
                },
            ),
        }

        response = requests.post(
            url=f"{self.url}/ingest",
            headers={
                "accept": "application/json",
            },
            data=payload,
            files=request_files,
            timeout=INGEST_TIMEOUT,
        )

        return {"status": response.status_code}

    def get_assistant_list(self) -> list[Assistant]:
        """List all assistants for the current user.

        Returns:
            list[Assistant]: assistant list
        """
        response = requests.get(
            url=f"{self.url}/assistants/",
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT,
        )
        return [Assistant(**res) for res in response.json()]

    def get_public_assistant_list(self, assistant_id: str) -> list[Assistant]:
        """List all public assistants.

        Args:
            assistant_id (str): assistant id

        Returns:
            list[Assistant]: public assistant list
        """
        response = requests.get(
            url=f"{self.url}/assistants/public/",
            headers=self.headers,
            params={"shared_id": assistant_id},
            timeout=DEFAULT_TIMEOUT,
        )
        return [Assistant(**res) for res in response.json()]

    def get_assistant(self, assistant_id: str) -> Assistant:
        """Get an assistant by ID.

        Args:
            assistant_id (str): assistant id

        Returns:
            Assistant: assistant info
        """
        response = requests.get(
            url=f"{self.url}/assistants/{assistant_id}",
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT,
        )
        return Assistant(**response.json())

    def delete_assistant(self, assistant_id: str):
        """_summary_

        Args:
            assistant_id (str): _description_
        """
        pass

    def creat_assistant(
        self,
        name: str,
        config: dict,
        public: bool = False,
    ) -> Assistant:
        """Create an assistant.

        Args:
            name (str): assistant name
            config (dict): config TODO
            public (bool, optional): is public. Defaults to False.

        Returns:
            Assistant: _description_
        """
        response = requests.post(
            url=f"{self.url}/assistants",
            headers=self.headers,
            json={
                "name": name,
                "config": config,
                "public": public,
            },
            timeout=DEFAULT_TIMEOUT,
        )
        return Assistant(**response.json())

    def get_thread_list(self) -> list[Thread]:
        """List all threads for the current user

        Returns:
            list[Thread]: all threads
        """
        response = requests.get(
            url=f"{self.url}/threads/",
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT,
        )
        return [Thread(**res) for res in response.json()]

    def get_thread(self, thread_id: str) -> Thread:
        """Get a thread by ID.

        Args:
            thread_id (str): thread id

        Returns:
            Thread: thread info
        """
        response = requests.get(
            url=f"{self.url}/threads/{thread_id}",
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT,
        )
        return Thread(**response.json())

    def get_messages(self, thread_id: str) -> ThreadMessages:
        """Get all messages for a thread.

        Args:
            thread_id (str): thread id

        Returns:
            ThreadMessages: Thred Messages
        """
        response = requests.get(
            url=f"{self.url}/threads/{thread_id}/messages",
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT,
        )
        return ThreadMessages(**response.json())

    def get_thread_history(self, thread_id: str) -> list[ThreadHistory]:
        """Get all past states for a thread.

        Args:
            thread_id (str): thread id

        Returns:
            list[ThreadHistory]: thread history
        """
        response = requests.get(
            url=f"{self.url}/threads/{thread_id}/history",
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT,
        )
        return [ThreadHistory(**res) for res in response.json()]

    def create_thread(self, name: str, assistant_id: str) -> Thread:
        """Create a thread.

        Args:
            name (str): thread name
            assistant_id (str): assistant id

        Returns:
            Thread: thread info
        """
        response = requests.post(
            url=f"{self.url}/threads",
            headers=self.headers,
            json={
                "name": name,
                "assistant_id": assistant_id,
            },
            timeout=DEFAULT_TIMEOUT,
        )
        return Thread(**response.json())

    def run(
        self,
        assistant_id: str,
        thread_id: str,
        messages: list[Message],
    ) -> str:
        """Create run

        Args:
            assistant_id (str): assisntant id
            thread_id (str): thread id
            messages (list[Message]): input message list

        Returns:
            dict: _description_
        """
        response = requests.post(
            f"{self.url}/runs",
            headers=self.headers,
            json={
                "input": [m.to_request_params() for m in messages],
                "assistant_id": assistant_id,
                "thread_id": thread_id,
            },
            stream=True,
            timeout=CHAT_TIMEOUT,
        )

        return str(response.text())

    def run_stream(
        self,
        assistant_id: str,
        thread_id: str,
        messages: list[Message],
    ) -> Generator[list[Message], Any, None]:
        """Creat Run stream

        Args:
            assistant_id (str): assisntant id
            thread_id (str): thread id
            messages (list[Message]): input message list

        Raises:
            HTTPError: _description_

        Yields:
            Generator[list[Massage], Any, None]: _description_
        """
        response = requests.post(
            f"{self.url}/runs/stream",
            headers=self.headers,
            json={
                "input": [m.to_request_params() for m in messages],
                "assistant_id": assistant_id,
                "thread_id": thread_id,
            },
            stream=True,
            timeout=CHAT_TIMEOUT,
        )
        event_type = None
        for msg in response.iter_lines(chunk_size=None, decode_unicode=True):
            if msg.strip():
                event, data = msg.split(":", 1)

                if event.strip() == "event":
                    event_type = data.strip()

                if event_type == "metadata" and event.strip() == "data":
                    _ = orjson.loads(data.strip())["run_id"]
                elif event_type == "data" and event.strip() == "data":
                    stream_messages = orjson.loads(data.strip())
                    yield [Message(**m) for m in stream_messages]
                elif event_type == "error" and event.strip() == "data":
                    # messages = orjson.loads(data.strip())
                    raise HTTPError(orjson.loads(data.strip()))

    def run_and_get_messages(
        self,
        assistant_id: str,
        thread_id: str,
        messages: list[Message],
    ) -> list[Message]:
        """Create Run and get response messages

        Args:
            assistant_id (str): assisntant id
            thread_id (str): thread id
            messages (list[Message]): input message list

        Returns:
            list[Message]: all thread messages
        """
        response = self.run_stream(
            assistant_id=assistant_id,
            thread_id=thread_id,
            messages=messages,
        )
        stream_responses = [res for res in response]
        return stream_responses[-1]

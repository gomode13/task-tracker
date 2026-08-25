from uuid import uuid4

import httpx
from time import time

from app.config import settings
from app.llm import prompts


class GigaChatClient:
    def __init__(self) -> None:
        self.access_token: str | None = None
        self.expires_at: int | None = None

    def _is_token_valid(self) -> bool:
        if self.access_token is None or self.expires_at is None:
            return False
        if self.expires_at / 1000 - 60 < time():
            return False
        return True

    async def _fetch_access_token(self) -> None:
        async with httpx.AsyncClient(verify=settings.GIGACHAT_CA_CERT_FILE) as client:
            response = await client.post(
                url="https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "RqUID": str(uuid4()),
                    "Authorization": f"Basic {settings.GIGACHAT_AUTH_KEY}",
                },
                data={"scope": "GIGACHAT_API_PERS"},
            )
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.expires_at = token_data["expires_at"]

    async def _ensure_access_token(self) -> None:
        if not self._is_token_valid():
            await self._fetch_access_token()

    async def generate_summary(self, completed_titles: list[str], pending_titles: list[str]) -> str:
        await self._ensure_access_token()
        user_message = (
            f"Выполненные задачи:\n{"\n".join(completed_titles)}\nНевыполненные задачи:\n{"\n".join(pending_titles)}"
        )
        async with httpx.AsyncClient(verify=settings.GIGACHAT_CA_CERT_FILE) as client:
            response = await client.post(
                url="https://api.giga.chat/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {self.access_token}",
                },
                json={
                    "model": "GigaChat-2",
                    "messages": [
                        {"role": "system", "content": prompts.DAILY_REPORT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_message},
                    ],
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]

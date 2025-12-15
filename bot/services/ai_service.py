import aiohttp
import logging
from typing import Optional

from bot.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Сервис для взаимодействия с DeepSeek API."""

    def __init__(self):
        self.base_url = settings.DEEPSEEK_BASE_URL.rstrip("/")
        self.api_key = settings.DEEPSEEK_API_KEY
        self.model = settings.DEEPSEEK_MODEL

    async def get_answer(self, user_question: str) -> str:
        """
        Получить ответ от ИИ-ассистента на вопрос пользователя.

        Args:
            user_question: Вопрос пользователя

        Returns:
            Ответ ИИ или сообщение об ошибке
        """
        if not self.api_key:
            return "⚠️ API ключ не настроен. Пожалуйста, настройте DEEPSEEK_API_KEY в .env файле."

        system_prompt = (
            "You are a wise, polite Islamic assistant based on Quran and Sunnah. "
            "Your role is to provide accurate Islamic knowledge with scholarly references. "
            "Always be respectful, humble, and compassionate in your responses. "
            "Format your answers using Markdown: use **bold** for key points, "
            "quote sources in blockquotes (`>`), and end with 'Allah knows best' when appropriate. "
            "Keep responses concise but informative, and avoid giving personal opinions."
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("choices", [{}])[0].get("message", {}).get("content", "❌ Не удалось получить ответ.")
                    else:
                        error_text = await response.text()
                        logger.error(f"DeepSeek API error: {response.status} - {error_text}")
                        return f"⚠️ Ошибка API (код {response.status}). Попробуйте позже."

        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            return "⚠️ Ошибка соединения с ИИ-сервисом. Проверьте интернет-соединение."
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "⚠️ Внутренняя ошибка сервиса. Попробуйте позже."

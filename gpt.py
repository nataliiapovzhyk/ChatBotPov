from openai import OpenAI, AsyncOpenAI
import httpx as httpx

import logging

from telegram.ext import ContextTypes

from credentials import config


class ChatGptService:
    client: AsyncOpenAI = None

    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    def __init__(self, token):
        #token = "sk-proj-" + token[:3:-1] if token.startswith('gpt:') else token
        self.client = AsyncOpenAI(api_key=token)


    def _get_message_list(self, context: ContextTypes.DEFAULT_TYPE) -> list:
        if "message_list" not in context.user_data:
            context.user_data["message_list"] = []
        return context.user_data["message_list"]

    async def send_message_list(self, context: ContextTypes.DEFAULT_TYPE) -> str:

        self.logger.info("надсилаємо запит")
        message_list = self._get_message_list(context)

        completion = await self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=message_list,
            max_tokens=3000,
            temperature=0.9,
        )

        message = completion.choices[0].message

        message_list.append({
            "role": "assistant",
            "content": message.content
        })
        return message.content

    def set_prompt(self,context: ContextTypes.DEFAULT_TYPE, prompt_text: str) -> None:
        context.user_data["message_list"] = [
            {"role": "system", "content": prompt_text}
        ]

    async def add_message(self, context: ContextTypes.DEFAULT_TYPE, message_text: str) -> str:
        message_list = self._get_message_list(context)
        message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list(context)

    async def send_question(self, context: ContextTypes.DEFAULT_TYPE, prompt_text: str, message_text: str) -> str:
        context.user_data["message_list"] = [
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": message_text}
        ]
        return await self.send_message_list(context)

chat_gpt = ChatGptService(config.ChatGPT_TOKEN)



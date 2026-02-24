import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from tools import get_my_ip_location, get_weather_by_city

load_dotenv()


class SimpleAgent:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing. Please set it in .env.")

        self.chat_history: list[HumanMessage | AIMessage] = []
        self.max_history_turns = 6
        tools = [get_my_ip_location, get_weather_by_city]
        llm = ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=0)
        self.agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=(
                "你是一个简洁、可靠的中文助手。"
                "当用户询问 IP、定位或天气时，优先调用工具再回答。"
                "当工具返回结果后，用自然中文总结。"
            ),
        )

    def clear_history(self) -> None:
        self.chat_history = []

    def run(self, user_input: str) -> str:
        result = self.agent.invoke(
            {
                "messages": [
                    *self.chat_history,
                    HumanMessage(content=user_input),
                ]
            }
        )
        reply = ""
        for message in reversed(result.get("messages", [])):
            if isinstance(message, AIMessage):
                reply = message.text if hasattr(message, "text") else str(message.content)
                break

        self.chat_history.append(HumanMessage(content=user_input))
        self.chat_history.append(AIMessage(content=reply))

        max_messages = self.max_history_turns * 2
        if len(self.chat_history) > max_messages:
            self.chat_history = self.chat_history[-max_messages:]

        return reply

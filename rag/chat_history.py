from langchain.schema import HumanMessage, AIMessage
from db.supabase import db_client


class SupabaseChatMessageHistory:
    def __init__(self, session_id: str):
        self.db = db_client
        self.session_id = self.db.save_chat_session(session_id)

    def add_user_message(self, message: str):
        self.db.save_chat_message(
            session_id=self.session_id,
            role="human",
            content=message,
        )

    def add_ai_message(self, message: str):
        self.db.save_chat_message(
            session_id=self.session_id,
            role="ai",
            content=message,
        )

    def clear(self):
        self.db.delete_chat_message(self.session_id)

    def messages(self):
        response = self.db.get_chat_messages(self.session_id)

        result = []
        for msg in response:
            if msg["role"] == "human":
                result.append(HumanMessage(content=msg["content"]))
            else:
                result.append(AIMessage(content=msg["content"]))

        return result

    def raw_messages(self):
        messages = self.messages()
        result = []
        for msg in messages:
            if hasattr(msg, "type") and hasattr(msg, "content"):
                # It's a LangChain message object
                role = "human" if msg.type == "human" else "ai"
                result.append(
                    {
                        "role": role,
                        "content": msg.content,
                        "session_id": getattr(msg, "session_id", self.session_id),
                    }
                )
            else:
                # Assume it's already a dictionary
                result.append(msg)
        return result

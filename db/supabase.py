"""
Supabase client for PagePal application.
Handles database connections and operations.
"""

from typing import Any, Dict, Optional, List
from supabase import Client, create_client

from config import config
from utils.logger import logger


class SupabaseClient:
    """Supabase client for database operations."""

    def __init__(self):
        """Initialize Supabase client."""
        self.client: Optional[Client] = None  # type: ignore
        self.initialize()

    def initialize(self) -> None:
        """Initialize the Supabase client with configuration settings."""
        try:
            self.client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    def save_chat_message(
        self, session_id: int, role: str, content: str
    ) -> Dict[str, Any]:
        try:
            result = (
                self.client.table("blogforge_chat_messages")
                .insert({"session_id": session_id, "role": role, "content": content})
                .execute()
            )

            logger.info(f"Saved chat message for session {session_id}")
            return result.data[0]
        except Exception as e:
            logger.error(f"Failed to save chat messages: {e}")
            raise

    def delete_chat_message(self, session_id: int) -> Dict[str, Any]:
        try:
            response = (
                self.client.table("blogforge_chat_messages")
                .delete()
                .eq("session_id", session_id)
                .execute()
            )

            logger.info(f"Deleted chat message for session {session_id}")

            return response.data[0]
        except Exception as e:
            logger.error(f"Failed to delete chat messages: {e}")
            raise

    def get_chat_messages(self, session_id: int) -> List[Dict[str, Any]]:
        try:
            response = (
                self.client.table("blogforge_chat_messages")
                .select("role,content,created_at")
                .eq("session_id", session_id)
                .order("created_at")
                .execute()
            )

            logger.info(
                f"Fetched {len(response.data)} chat messages for session {session_id}"
            )

            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch chat messages: {e}")
            raise

    def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = (
                self.client.table("blogforge_chat_sessions")
                .select("id")
                .eq("session_id", session_id)
                .execute()
            )

            if response.data:
                logger.info(f"Fetched chat session for session {session_id}")
                return response.data[0]
            else:
                logger.info(f"No chat session found for session {session_id}")
                return None
        except Exception as e:
            logger.error(f"Failed to fetch chat session: {e}")
            raise

    def save_chat_session(self, session_id: str) -> int:
        try:
            existing_session = (
                self.client.table("blogforge_chat_sessions")
                .select("id")
                .eq("session_id", session_id)
                .execute()
            )

            if existing_session.data:
                result = existing_session.data[0]["id"]
            else:
                result = (
                    self.client.table("blogforge_chat_sessions")
                    .insert(
                        {
                            "session_id": session_id,
                        }
                    )
                    .execute()
                    .data[0]["id"]
                )

            logger.info(f"Saved chat session for session {session_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to save chat session: {e}")
            raise

    def get_crawled_website_information_by_urls(
        self, urls: List[str]
    ) -> List[Dict[str, Any]]:
        try:
            response = (
                self.client.table("blogforge_crawled_websites")
                .select("url, title, description, content, published_time, images")
                .in_("url", urls)
                .execute()
            )

            logger.info(f"Fetched crawled website information for URLs {urls}")

            return response.data
        except Exception as e:
            logger.error(f"Failed to fetch crawled website information: {e}")
            raise

    def save_crawled_websites(
        self, records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        try:
            # Perform batch insertion
            response = (
                self.client.table("blogforge_crawled_websites")
                .insert(records)
                .execute()
            )

            # Log the URLs of the inserted records
            inserted_urls = [record["url"] for record in records]
            logger.info(f"Saved crawled website information with URLs: {inserted_urls}")

            return response.data
        except Exception as e:
            logger.error(f"Failed to save crawled website information: {e}")
            raise

    def save_trending_keywords(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Inserts multiple keywords into the 'blogforge_trending_keywords' table.

        Args:
            keywords (List[str]): A list of keyword strings to insert.

        Returns:
            List[int]: A list of IDs representing the inserted or existing keywords.
        """
        try:
            # Prepare records for upsert
            records = [{"keyword": keyword} for keyword in keywords]

            # Perform batch upsert
            response = (
                self.client.table("blogforge_trending_keywords")
                .upsert(records, on_conflict="keyword")
                .execute()
            )

            # Log the inserted keywords
            logger.info(f"Saved trending keywords: {keywords}")

            return response.data
        except Exception as e:
            logger.error(f"Failed to save trending keywords: {e}")
            raise

    def save_trending_keyword_crawled_websites(
        self, records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        try:
            # Perform batch upsert
            response = (
                self.client.table("blogforge_trending_keyword_crawled_websites")
                .upsert(
                    records,
                    on_conflict="blogforge_trending_keyword_id, blogforge_crawled_website_id",
                )
                .execute()
            )

            # Log the inserted keywords
            logger.info("Saved trending keyword crawled website information")

            return response.data
        except Exception as e:
            logger.error(
                f"Failed to save trending keyword crawled website information: {e}"
            )
            raise


# Create a singleton instance for easy importing
db_client = SupabaseClient()

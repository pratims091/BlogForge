from typing import Dict
from typing import Any, List, Tuple
from tools.search import search_for_blog_posts
from crawler.crawler import crawl_search_results
from crawler.processor import chunk_documents, process_crawl_results
from db.vector_store import vector_store_manager
from rag.chains import (
    create_streaming_qa_chain,
    stream_qa_chain,
)
from rag.prompts import get_forge_blog_prompt
from db.supabase import db_client
import asyncio
import uuid
from pprint import pprint
from utils.helpers import format_sources_text


class BlogForge:
    def __init__(self, keywords: list[str], session_id: str):
        self.keywords = list(set(keyword.strip().lower() for keyword in keywords))
        self.session_id = session_id
        self.db = db_client

    async def forge(self) -> Tuple[str, List[Dict[str, Any]]]:
        search_results = await search_for_blog_posts(keywords=self.keywords, limit=7)
        crawl_results = await crawl_search_results(search_results)

        documents = process_crawl_results(results=crawl_results)

        # Chunk documents
        chunked_documents = chunk_documents(documents)

        # Create vector store
        vector_store_manager.create_vector_store(
            documents=chunked_documents, vector_store_id=self.session_id
        )

        retriever = vector_store_manager.get_retriever(vector_store_id=self.session_id)

        streaming_qa_chain, history = create_streaming_qa_chain(
            retriever, session_id=self.session_id
        )

        message = get_forge_blog_prompt(topics=self.keywords, version="V2")

        result, message_history = await stream_qa_chain(
            chain=streaming_qa_chain,
            question=message,
            history=history,
            modified_human_message=", ".join(self.keywords),
        )

        answer = result.get("answer", "")
        if not answer and "result" in result:
            answer = result["result"]

        source_documents = result.get("source_documents", [])

        # Add sources to the answer
        sources_text = format_sources_text(source_documents)
        if sources_text:
            answer += sources_text

        return answer, message_history

    async def chat(self, query: str) -> Tuple[str, List[Dict[str, Any]]]:
        session_exists = self.db.get_chat_session(session_id=self.session_id)
        if not session_exists:
            return "", []

        retriever = vector_store_manager.get_retriever(vector_store_id=self.session_id)

        streaming_qa_chain, history = create_streaming_qa_chain(
            retriever, session_id=self.session_id
        )

        result, message_history = await stream_qa_chain(
            chain=streaming_qa_chain,
            question=query,
            history=history,
        )

        answer = result.get("answer", "")
        if not answer and "result" in result:
            answer = result["result"]

        source_documents = result.get("source_documents", [])

        # Add sources to the answer
        sources_text = format_sources_text(source_documents)
        if sources_text:
            answer += sources_text

        return answer, message_history


if __name__ == "__main__":
    bf = BlogForge(keywords=["MCP servers"], session_id=str(uuid.uuid4()))
    res = asyncio.run(bf.forge())

    pprint(res)

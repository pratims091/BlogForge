"""
Content processing for BlogForge application.
Processes crawled content into documents.
"""

from typing import Any, Dict, List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from utils.logger import logger


def process_crawl_results(results: List[Dict[str, Any]]) -> List[Document]:
    """
    Process crawl results into documents.

    Args:
        results: List of crawl results

    Returns:
        List[Document]: List of processed documents
    """
    try:
        documents = []

        for r in results:
            keyword = r["keyword"]
            result = r["result"]

            # Get the URL and content
            page_url = result.get("url", "")
            content = result.get("content", "")

            if not content:
                logger.warning(f"Skipping empty content for URL: {page_url}")
                continue

            # Create document with metadata
            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": page_url,
                        "title": result.get("title", ""),
                        "description": result.get("description", ""),
                        "keyword": keyword,
                    },
                )
            )

        logger.info(f"Processed {len(documents)} documents from crawl results")
        return documents
    except Exception as e:
        logger.error(f"Failed to process crawl results: {e}")
        raise


def chunk_documents(documents: List[Document], **kwargs) -> List[Document]:
    """
    Chunk documents into smaller pieces.

    Args:
        documents: List of documents to chunk
        **kwargs: Additional kwargs for the text splitter

    Returns:
        List[Document]: List of chunked documents
    """
    try:
        # Default chunk settings
        chunk_size = kwargs.get("chunk_size", 500)
        chunk_overlap = kwargs.get("chunk_overlap", 50)
        separators = kwargs.get(
            "separators",
            [
                "\n#{1,6} ",
                "```\n",
                "\n\\*\\*\\*+\n",
                "\n---+\n",
                "\n___+\n",
                "\n\n",
                "\n",
                " ",
                "",
            ],
        )

        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            add_start_index=True,  # If `True`, includes chunk's start index in metadata
            strip_whitespace=True,  # If `True`, strips whitespace from the start and end of every document
            separators=separators,
        )

        # Split documents
        chunked_documents = text_splitter.split_documents(documents)

        logger.info(
            f"Chunked {len(documents)} documents into {len(chunked_documents)} chunks"
        )
        return chunked_documents
    except Exception as e:
        logger.error(f"Failed to chunk documents: {e}")
        raise

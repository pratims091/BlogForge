import asyncio
import datetime
import json
from typing import Any, Dict, List, Optional
from tools.crawl4ai import crawl, poll_crawl_result
from tools.jina import Jina
from utils.logger import logger
from config import config
from db.supabase import db_client


async def crawler_crawl4ai(
    urls: List[str], timeout: int = config.CRAWL_TIMEOUT
) -> List[Dict[str, Any]]:
    # Configure the crawler to use the Docker container endpoint
    # Note: When running within Docker, we use the service name
    # When running locally outside Docker, we use localhost
    crawler_host = config.CRAWL4AI_HOST
    # Initiate crawling
    task_id = crawl(urls=urls, host=crawler_host)
    logger.info(f"Crawling initiated with task ID: {task_id}")

    crawl_results = []

    # Define async timeout
    async def wait_for_results():
        # Poll for results
        return poll_crawl_result(task_id, host=crawler_host, interval=5)

    results = await asyncio.wait_for(
        asyncio.create_task(wait_for_results()), timeout=timeout
    )

    for result in results:
        crawl_results.append(
            {
                "url": result.url,
                "title": result.get("metadata", {}).get("title", ""),
                "description": result.get("metadata", {}).get("description", ""),
                "content": result.get("extracted_content")
                or result.get("markdown")
                or result.get("cleaned_html"),
                "published_time": None,
                "images": json.dumps(result.get("media", {}).get("images", [])),
            }
        )

    return crawl_results


async def crawler_jina(
    urls: List[str], timeout: int = config.CRAWL_TIMEOUT
) -> List[Dict[str, Any]]:
    jina = Jina(urls=urls, timeout=timeout)
    results = await jina.run()

    crawl_results = []
    for crawl_result in results:
        if "url" in crawl_result:
            published_time = crawl_result.get("publishedTime", None)
            if published_time:
                try:
                    published_time = (
                        datetime.datetime.fromisoformat(published_time)
                        .astimezone(datetime.timezone.utc)
                        .isoformat()
                    )
                except ValueError:
                    published_time = None

            crawl_results.append(
                {
                    "url": crawl_result["url"],
                    "title": crawl_result.get("title", ""),
                    "description": crawl_result.get("description", ""),
                    "content": crawl_result.get("content", ""),
                    "published_time": published_time,
                    "images": json.dumps(crawl_result.get("images", [])),
                }
            )
    return crawl_results


async def crawl_search_results(
    search_results: List[Dict[str, Any]], timeout: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Crawl a URL and get the results.

    Args:
        url: The URL to crawl
        timeout: Timeout in seconds (optional)

    Returns:
        List[Dict[str, Any]]: The crawl results
    """
    if timeout is None:
        timeout = config.CRAWL_TIMEOUT

    try:
        urls = [res["url"] for res in search_results]
        logger.info(f"Starting crawl for {len(urls)} URLs")

        existing = db_client.get_crawled_website_information_by_urls(urls)
        crawl_results = []
        existing_urls = {item["url"] for item in existing}

        for url in urls[:]:
            if url in existing_urls:
                crawl_results.append(
                    next(item for item in existing if item["url"] == url)
                )
                urls.remove(url)

        if not urls:
            return [
                {
                    "keyword": item["keyword"],
                    "result": next(
                        res for res in crawl_results if res["url"] == item["url"]
                    ),
                }
                for item in search_results
            ]

        results = []

        if config.CRAWLER_PROVIDER == "JINA":
            crawl_results = await crawler_jina(urls, timeout)
        else:
            crawl_results = await crawler_crawl4ai(urls, timeout)

        logger.info(
            f"Crawling completed for URL: {urls}, got {len(crawl_results)} results"
        )
        url_to_crawl_results = {item["url"]: item for item in crawl_results}

        for item in search_results:
            url = item["url"]
            if url in urls:
                result = url_to_crawl_results.get(url, "")
                if result:
                    results.append({"keyword": item["keyword"], "result": result})
        # Remove results that are already existing
        new_crawl_results = [
            result for result in crawl_results if result["url"] not in existing_urls
        ]
        if new_crawl_results:
            db_client.save_crawled_websites(records=new_crawl_results)

        return results
    except Exception as e:
        logger.error(f"Error during crawling: {str(e)}")
        raise

from typing import Dict, Any, List
from googlesearch import search
from config import config
from utils.logger import logger
from db.supabase import db_client


def perform_search(keyword: str, limit: int, advanced: bool) -> List[Any]:
    return search(
        keyword + " blog posts intitle:blog inurl:blog",
        num_results=limit,
        lang="en",
        region="eu",
        unique=True,
        advanced=advanced,
        sleep_interval=5,
        ssl_verify=False,
    )


def process_results(
    results: List[Any],
    keyword: str,
    search_results: List[Dict[str, Any]],
    advanced: bool,
) -> None:
    for res in results:
        if advanced:
            search_results.append(
                {
                    "keyword": keyword,
                    "title": res.title,
                    "url": res.url,
                    "description": res.description,
                }
            )
        else:
            search_results.append(
                {
                    "keyword": keyword,
                    "url": res,
                }
            )


def update_search_results_with_ids(
    search_results: List[Dict[str, Any]], saved_keywords: List[Dict[str, Any]]
) -> None:
    for result in search_results:
        for saved_keyword in saved_keywords:
            if result["keyword"] == saved_keyword["keyword"]:
                result["keyword_id"] = saved_keyword["id"]


async def search_for_blog_posts(
    keywords: List[str], limit: int = config.MAX_SEARCH_RESULTS, advanced: bool = False
) -> List[Dict[str, Any]]:
    search_results = []
    successful_keywords = []

    for keyword in keywords:
        try:
            results = perform_search(keyword, limit, advanced)
            process_results(results, keyword, search_results, advanced)
            successful_keywords.append(keyword)
        except Exception as e:
            logger.error(f"Failed to search for keyword '{keyword}': {e}")

    if successful_keywords:
        saved_keywords = db_client.save_trending_keywords(successful_keywords)
        update_search_results_with_ids(search_results, saved_keywords)

    logger.info(
        f"Successfully searched Google for {len(successful_keywords)} out of {len(keywords)} keywords"
    )
    return search_results

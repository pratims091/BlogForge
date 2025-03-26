from typing import List
import requests
from utils.logger import logger
import time
from config import config

headers = {"Authorization": f"Bearer {config.CRAWL4AI_API_TOKEN}"}


def crawl(urls: List[str], host: str) -> str:
    """
    Sends a POST request to the crawling API with the provided URLs and returns the task ID if the response is successful.

    Args:
        urls (List[str]): A list of URLs to be crawled.

    Returns:
        str: The task ID if the response status is 200, otherwise an error message.
    """

    response = requests.post(
        f"{host}/crawl",
        headers=headers,
        json={
            "urls": urls,
            "priority": 1,
            "crawler_params": {
                "simulate_user": True,
                "magic": True,
                "override_navigator": True,
                "user_agent_mode": "random",
                "headers": {
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xhtml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                },
                "verbose": True,
                "page_timeout": 30000,
                "remove_overlay_elements": True,
                "deep_crawl_strategy": {
                    "type": "best_first",
                    "max_depth": 3,
                    "max_pages": 50,
                    "url_scorer": {
                        "type": "keyword_relevance",
                        "keywords": [
                            "tutorial",
                            "guide",
                            "documentation",
                            "product",
                            "blog",
                            "article",
                            "overview",
                            "features",
                        ],
                    },
                },
                "content_scorer": {
                    "type": "keyword_relevance",
                    "keywords": [
                        "tutorial",
                        "guide",
                        "documentation",
                        "product",
                        "blog",
                        "article",
                        "overview",
                        "features",
                    ],
                    "min_score_threshold": 0.5,
                },
                "content_filters": {
                    "include_tags": ["p", "article", "section", "div"],
                    "exclude_tags": ["script", "style", "nav", "footer", "header"],
                    "min_text_length": 100,
                },
            },
            "extra": {
                "bypass_cache": True,
                "check_robots_txt": True,
                "error_handling": {
                    "max_retries": 2,
                    "retry_delay": 5000,
                    "skip_errors": ["404", "403", "500", "timeout"],
                },
            },
        },
    )

    if response.status_code == 200:
        res = response.json()
        return res.get("task_id", "No task_id found in response")
    else:
        logger.error(f"Error: Received status code {response.status_code}")
        response.raise_for_status()


def poll_crawl_result(task_id: str, host: str, interval: int = 5):
    """
    Polls the status of a crawling task at regular intervals until it is completed or failed.

    Args:
        task_id (str): The unique identifier of the crawling task.
        host (str): The host URL where the task status can be queried.
        interval (int, optional): The time interval (in seconds) between each poll. Defaults to 5 seconds.

    Returns:
        dict: The results of the completed task if the task is successful.

    Raises:
        RuntimeError: If the task fails.
    """
    status_url = f"{host}/task/{task_id}"
    while True:
        logger.debug(f"Polling task status at {status_url}")

        response = requests.get(status_url, headers=headers)
        res = response.json()
        status = res.get("status")

        logger.debug(f"Task {task_id} status: {status}")
        if status == "completed":
            logger.info(f"Task {task_id} completed successfully")
            return res.get("results")
        elif status == "failed":
            logger.error(f"Task {task_id} failed")
            raise RuntimeError(f"Task {task_id} failed.")
        time.sleep(interval)

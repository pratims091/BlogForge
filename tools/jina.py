from typing import Any, Dict
from config import config
from utils.logger import logger

import asyncio
import aiohttp
from typing import List


class Jina:
    def __init__(self, urls: List[str], max_concurrent: int = 3, timeout: int = 10):
        self.urls = urls
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.api_key = config.JINA_API_KEY
        self.base_url = "https://r.jina.ai/"
        self.timeout = timeout
        logger.info(
            f"Initialized Jina with {len(urls)} URLs, max_concurrent={max_concurrent}, timeout={timeout}"
        )

    async def fetch(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        async with self.semaphore:
            jina_url = f"{self.base_url}{url}"
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "X-Timeout": str(self.timeout),
                "X-With-Generated-Alt": "true",
                "X-With-Images-Summary": "true",
            }
            logger.debug(f"Fetching URL: {jina_url}")
            try:
                async with session.get(url=jina_url, headers=headers) as response:
                    if response.status == 200:
                        json_data = await response.json()
                        logger.debug(
                            f"Successfully fetched data: {json_data} from {jina_url}"
                        )
                        return json_data.get("data", {})
                    else:
                        logger.warning(
                            f"Failed to fetch {jina_url}, status code: {response.status}"
                        )
                        return {}
            except Exception as e:
                logger.error(f"Exception occurred while fetching {jina_url}: {e}")
                return {}

    async def crawl(self) -> List[Dict[str, Any]]:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for url in self.urls:
                tasks.append(self.fetch(session, url))
            results = await asyncio.gather(*tasks)
            return results

    async def run(self) -> List[Dict[str, Any]]:
        logger.info("Running Jina crawler")
        results = await self.crawl()
        logger.info("Jina crawler finished")
        return results

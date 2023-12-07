import asyncio
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

import aiohttp
from loguru import logger
from selenium import webdriver

from models import RequestPageData

DOWNLOAD_RETRY: int = 2
DOWNLOAD_RETRY_TIMEOUT: int = 5

class Downloader(ABC):

    def __init__(self, retry: int = None, retry_timeout: int = None):
        self.retry: int = retry if retry else DOWNLOAD_RETRY
        self.retry_timeout: int = retry_timeout if retry_timeout else DOWNLOAD_RETRY_TIMEOUT

    @abstractmethod
    async def download_html(self, page: RequestPageData) -> str | None:
        raise NotImplementedError("Метод должен быть переопределен в подклассе")


class StaticDownloader(Downloader):
    """Управление загрузкой со server rendered ресурсов"""

    def __init__(self, retry: int = None, retry_timeout: int = None):
        super().__init__(retry=retry, retry_timeout=retry_timeout)
        self.session: aiohttp.ClientSession | None = None

    async def _fetch_html(self, url: str, params: str | None = None) -> str | None:
        """
        Загружает текст страницы
        :param url:
        :param params:
        :param retry:
        :return:
        """
        while self.retry > 0:
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status != 200:
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"Недопустимый статус запроса на {url} {response.status}",
                        )
                    return await response.text()
            except Exception as e:
                logger.warning(f'Невозможно выполнить запрос  {url}: {e}. Осталось попыток: {self.retry}')
                await asyncio.sleep(self.retry_timeout)
                self.retry -= 1
                logger.warning(f'Не удалось загрузить {url}') if self.retry == 0 else None

    async def download_html(self, page: RequestPageData) -> str | None:
        """Загружает HTML по url и headers из пользовательского объекта RequestPageData"""
        self.session = aiohttp.ClientSession()
        try:
            page_html = await self._fetch_html(page.url, params=page.request_params)
            return page_html
        finally:
            await self.session.close()


class DynamicDownloader(Downloader):
    """Управление загрузкой с client rendered ресурсов"""

    def __init__(self, retry: int = None, retry_timeout: int = None):
        super().__init__(retry=retry, retry_timeout=retry_timeout)
        self.driver: webdriver = None

    async def _fetch_html(self, url: str) -> str | None:
        """Загружает текст страницы"""
        loop = asyncio.get_event_loop()

        def fetch_sync():
            while self.retry > 0:
                try:
                    self.driver.get(url)
                    time.sleep(5)
                    res = self.driver.page_source
                    return res
                except Exception as e:
                    logger.warning(f'Невозможно выполнить запрос  {url}: {e}. Осталось попыток: {self.retry}')
                    time.sleep(self.retry_timeout)
                    self.retry -= 1

        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, fetch_sync )

    async def download_html(self, page: RequestPageData) -> str | None:
        """Загружает HTML по url из пользовательского объекта RequestPageData"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-infobars')
        self.driver = webdriver.Chrome(options=options)
        try:
            page_html = await self._fetch_html(page.url)
            return page_html
        finally:
            self.driver.quit() if self.driver else None

#
# async def main():
#     start_time = time.time()
#
#     page = RequestPageData.from_url("https://procapitalist.ru/obyavleniya/ishchu-proizvoditelej-uslugi-po-poshivu-5")
#     dynamic_page = RequestPageData.from_url("https://youdo.com/tasks-all-opened-all")
#
#     static_downloader = StaticDownloader()
#     static_page_html = await static_downloader.download_html(page)
#
#     dynamic_downloader = DynamicDownloader()
#     dynamic_page_html = await dynamic_downloader.download_html(dynamic_page)
#     print(dynamic_page_html)
#
#     elapsed_time = time.time() - start_time
#     print(f"Total time: {elapsed_time} seconds")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())

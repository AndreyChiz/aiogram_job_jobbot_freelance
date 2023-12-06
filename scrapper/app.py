import asyncio
from typing import Coroutine

from config import SCRAPPER_SETTINGS
from downloader import Downloader
from models import RequestPageData
from parser import Parser


class Scrapper:
    def __init__(self, url: str, downloader: Downloader, parser: Parser):
        self.request_data: RequestPageData = RequestPageData.from_url(url)
        self.downloader: Downloader = downloader()
        self.parser: Parser = parser()
        print(self.request_data)

    async def get_new_data(self):
        page_text = await self.downloader.download_html(self.request_data)
        result = await self.parser.parse_data(page_text)
        return result
        # raise NotImplementedError("Метод должен быть переопределен в подклассе")


class Program:
    def __init__(self, sites_settings: dict = SCRAPPER_SETTINGS):
        self.sites_settings: dict = sites_settings
        self.tasks: list[Coroutine] = []

    async def _create_tasks(self):
        for site, settings in self.sites_settings.items():
            self.tasks.append(
                Scrapper(
                    settings['url'],
                    settings['downloader'],
                    settings['parser']
                ).get_new_data()
            )

    async def update_data(self):
        await self._create_tasks()
        result = await asyncio.gather(*self.tasks)
        print(result)



if __name__ == "__main__":
    program = Program(SCRAPPER_SETTINGS)

    asyncio.run(program.update_data())

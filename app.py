import asyncio
from typing import Coroutine

from config import SITES_SETTINGS
from downloader import Downloader
from models import RequestPageData
from parser import Parser


class Scrapper:
    def __init__(self, url: str, downloader: Downloader, parser: Parser):
        self.request_data: RequestPageData = RequestPageData.from_url(url)
        self.downloader: Downloader = downloader
        self.parser: Parser = parser

    async def get_new_data(self):
        raise NotImplementedError("Метод должен быть переопределен в подклассе")


class Program:
    def __init__(self, sites_settings: dict = SITES_SETTINGS):
        self.sites_settings: dict = sites_settings
        self.tasks: list[Coroutine] = []

    async def _create_tasks(self):
        for site, settings in self.sites_settings.items():
            self.tasks.append(
                await Scrapper(
                    settings['url'],
                    settings['downloader'],
                    settings['parser']
                ).get_new_data()
            )

    async def run(self):
        await self._create_tasks()
        await asyncio.gather(*self.tasks)


if __name__ == "__main__":
    program_instance = Program(SITES_SETTINGS)
    asyncio.run(program_instance.run())

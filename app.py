import asyncio
from abc import ABC
from asyncio import coroutine
from downloader import Downloader
from parser import Parser
from models import RequestPageData
from config import SITES_SETTINGS


class Scrapper:
    def __init__(self, url: str, downloader: Downloader, parser: Parser):
        self.request_data: RequestPageData.from_url(url)
        self.downloader: Downloader = downloader
        self.parser: Parser = parser

    async def get_new_data(self):
        raise NotImplementedError("Метод должен быть переопределен в подклассе")


class Program:
    def __init__(self, sites_settings: dict):
        self.sites_settings: dict = sites_settings
        self.tasks: list[coroutine] = []

    async def _create_tasks(self):
        for site, settings in SITES_SETTINGS.items():
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







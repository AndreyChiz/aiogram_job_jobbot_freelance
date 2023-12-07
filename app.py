import asyncio
import time
from typing import Coroutine

from database import Database
from downloader import Downloader
from downloader import DynamicDownloader, StaticDownloader
from models import RequestPageData
from parser import HabrParser, FLParser, YouDoParser
from parser import Parser

SCRAPPER_SETTINGS = {'freelance.habr.com': {'url': 'https://freelance.habr.com/tasks',
                                            'downloader': StaticDownloader,
                                            'parser': HabrParser},
                     'www.fl.ru': {'url': 'https://www.fl.ru/projects/',
                                   'downloader': StaticDownloader,
                                   'parser': FLParser},
                     'youdo.com': {'url': 'https://youdo.com/tasks-all-opened-all',
                                   'downloader': DynamicDownloader,
                                   'parser': YouDoParser}
                     }


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
        self.db = Database()

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
        await self.db.create_tables()

        for item in result:
            print(item)
            await self.db.insert_data(item)
        print(len(result))

        return (result)


if __name__ == "__main__":
    start_time = time.time()
    program = Program(SCRAPPER_SETTINGS)

    asyncio.run(program.update_data())
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Время выполнения: {execution_time} секунд")

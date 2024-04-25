import asyncio
import time
from typing import Coroutine
from logger import logger

from database import Database
from downloader import DynamicDownloader, StaticDownloader, Downloader
from models import RequestPageData
from parser import HabrParser, FLParser, YouDoParser, Parser
from tg_bot import TGBot
from search_engine import SearchEngine

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
    """The class which getting data from one site"""

    def __init__(self, url: str, downloader: Downloader, parser: Parser):
        """
        :param url: The url to scrape
        :param downloader: The instance of Downloader class (type Static or Dynamic)
        :param parser: The instance of Parser class with the logic of parsing the data for each site
        """
        self.request_data: RequestPageData = RequestPageData.from_url(url)
        self.downloader: Downloader = downloader()
        self.parser: Parser = parser()

        logger.debug(self.request_data)

    async def get_data(self):
        """
        Tacking data from site.
        """
        page_text = await self.downloader.download_html(self.request_data)
        result = await self.parser.parse_data(page_text)
        return result


class Program:
    """The main program class"""

    def __init__(self, sites_settings=None, update_timeout: int = 5):
        """
        :param sites_settings: settings for the program
        :type sites_settings: dict
        """
        self.new_data_from_update: list = []
        if sites_settings is None:
            sites_settings = SCRAPPER_SETTINGS
        self.sites_settings: dict = sites_settings
        self.tasks: list[Coroutine] = []
        self.update_timeout = update_timeout

        self.db = Database()
        self.tg_bot = TGBot()
        self.search_engine = SearchEngine()

    async def _create_tasks(self):
        """
           Creates tasks for each site based on the provided settings.

           Clears the task list (`self.tasks`) and adds new tasks, each representing an instance of the
           `Scrapper` class for a specific site using the corresponding settings.
           """
        self.tasks = []
        for site, settings in self.sites_settings.items():
            self.tasks.append(
                Scrapper(
                    settings['url'],
                    settings['downloader'],
                    settings['parser']
                ).get_data()
            )

    async def _update_data(self):
        """
        Updates the data from all sites in the database extend new orders in self.data_from_update

        :param update_timeout: time to wait between updates in minutes
        """

        while True:
            await self._create_tasks()
            result = await asyncio.gather(*self.tasks)
            await self.db.create_tables()
            for item in result:
                self.new_data_from_update.extend(await self.db.insert_data(item))
            result.clear()
            await asyncio.sleep(self.update_timeout * 60)
            logger.debug(len(self.new_data_from_update))
            users_request_data = await self.db.get_user_data()

            notifications = await self.search_engine.create_notifications(
                self.new_data_from_update,
                users_request_data)
            await self.tg_bot.notify(notifications)

            logger.debug('результат')
            logger.debug(notifications)



    async def start(self):
        """Starts all proceses of application in asyncio gether"""
        await self.db.create_tables()
        bot_task = asyncio.create_task(self.tg_bot.start())
        scrasppers_task = asyncio.create_task(self._update_data())
        await asyncio.gather(bot_task, scrasppers_task)


if __name__ == "__main__":
    start_time = time.time()
    program = Program(SCRAPPER_SETTINGS)

    asyncio.run(program.start())
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Время выполнения: {execution_time} секунд")

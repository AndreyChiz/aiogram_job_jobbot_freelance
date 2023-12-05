from pydantic_settings import BaseSettings, SettingsConfigDict
from scrapper.downloader import DynamicDownloader, StaticDownloader
from scrapper.parser import HabrParser, FLParser, YouDoParser


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

class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        # postgresql+psyc
        return f'postgresql+asyncpg:// postgres:postgres'


from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin, urlparse

from sqlalchemy import Column, Integer,Boolean , String, DateTime, MetaData, DDL
from sqlalchemy.types import ARRAY
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column



class Base(DeclarativeBase):
    pass


metadata = MetaData()
on_conflict_ddl = DDL("ON CONFLICT (order_id) DO NOTHING")

class UsersOrm(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=True)
    user_keywords = Column(ARRAY(String), nullable=True)
    user_notify = Column(Boolean, default=True)



class BaseOrderData(Base):
    __tablename__ = 'base_order'
    __abstract__ = True

    order_id = Column(Integer, primary_key=True)
    load_date = Column(DateTime)
    url = Column(String)
    title = Column(String)
    price = Column(Integer, nullable=True)


class HabrOrderData(BaseOrderData):
    __tablename__ = 'freelance.habr.com'


class FlOrderData(BaseOrderData):
    __tablename__ = 'www.fl.ru'


class YoudoOrderData(BaseOrderData):
    __tablename__ = 'youdo.com'


@dataclass
class RequestPageData:
    """
    Данные для загрузки страницы.
    Варианты инициализации по url или отдельно host, path
    """
    host: str
    path: str
    request_params: Optional[dict] = None
    url: str = field(init=False, repr=True)

    def __post_init__(self):
        self.url = urljoin(self.host, self.path)

    @classmethod
    def from_url(cls, url: str, request_params: Optional[dict] = None):
        parsed_url = urlparse(url)
        return cls(parsed_url.scheme + '://' + parsed_url.netloc, parsed_url.path, request_params)


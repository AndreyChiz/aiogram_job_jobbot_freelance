import datetime
from dataclasses import dataclass, field
from typing import Optional, Annotated
from urllib.parse import urljoin, urlparse

from sqlalchemy import Column, BigInteger,Boolean , String, DateTime, MetaData, DDL, text
from sqlalchemy.types import ARRAY
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column



class Base(DeclarativeBase):
    pass


metadata = MetaData()
# on_conflict_ddl = DDL("ON CONFLICT (order_id) DO NOTHING")
created_at = Annotated[datetime.datetime, mapped_column(server_default=(text("TIMEZONE('utc', now())")))]
bigInt = Annotated[int, mapped_column(BigInteger, primary_key=True)]
u_list = Annotated[list, mapped_column(ARRAY(String),
                                       # nullable=True,
                                       default=[])]

class UsersOrm(Base):
    __tablename__ = 'users'
    user_id: Mapped[bigInt]
    user_name: Mapped[str | None]
    user_keywords: Mapped[u_list]
    user_notify: Mapped[bool] = mapped_column(Boolean, default=True)
    user_reg_data: Mapped[created_at]



class BaseOrderData(Base):
    __tablename__ = 'base_order'
    __abstract__ = True

    order_id: Mapped[bigInt]
    load_date: Mapped[created_at]
    url: Mapped[str]
    title: Mapped[str | None]
    price: Mapped[int | None]


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


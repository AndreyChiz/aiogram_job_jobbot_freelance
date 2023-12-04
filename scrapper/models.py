from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from urllib.parse import urljoin, urlparse
from dateparser import parse as dateparse
from loguru import logger


@dataclass
class OrderData:
    """Класс данных заказа.
    :param load_date можно передать строку, если класс не распознает, то присвоит текущую дату.
    :param price если не сможет распарсить - запишет None
    """
    order_id: int
    load_date: datetime | str
    url: str
    title: str
    price: Optional[int | str] = None

    def __post_init__(self):
        if isinstance(self.price, str):
            try:
                self.price = int(self.price)
            except ValueError:
                logger.warning(f"Цена заказа {self.order_id} не указана или некорректна.")
                self.price = None  # Устанавливаем price в None в случае ошибки

        if isinstance(self.load_date, str):
            parsed_date = dateparse(self.load_date)
            if parsed_date is not None:
                self.load_date = parsed_date
            else:
                logger.warning(f"Не удалось распознать дату заказа {self.order_id}. Устанавливаем текущую дату.")
                self.load_date = datetime.now()
        elif self.load_date is None:
            self.load_date = datetime.now()

        # Форматирование даты в нужный формат
        self.load_date = self.load_date.strftime("%d.%m.%Y %H:%M:%S")


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


@dataclass
class UserData:
    """
    Данные пользователя.
    :param user_key_words ключевые слова для поиска заказа.
    :param флаг включения оповещения пользователя о поступлении заказа.
    """
    user_id: int
    user_name: str = None
    user_key_words: List[str] = field(default_factory=list)
    user_notify_enable: bool = True



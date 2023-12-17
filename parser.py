import asyncio
import re
import time
from abc import ABC, abstractmethod
from typing import List
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup

from logger import logger
from models import BaseOrderData, HabrOrderData, FlOrderData, YoudoOrderData


class Parser(ABC):

    def __init__(self, ):
        self.order_data_obj_type = BaseOrderData

    async def _create_order_data_obj(
            self,
            order_id: int,
            # load_date: str | None,
            order_url: str,
            order_title: str,
            price: int):
        tmp_order_data = self.order_data_obj_type(
            order_id=order_id,
            # load_date=load_date,
            url=order_url,
            title=order_title,
            price=price
        )
        return tmp_order_data

    @abstractmethod
    async def parse_data(self, page_html: str | None) -> List[BaseOrderData] | None:
        """Returns a list of new orders"""
        raise NotImplementedError("Метод должен быть переопределен в подклассе")


class HabrParser(Parser):
    def __init__(self, ):
        self.order_data_obj_type = HabrOrderData

    async def parse_data(self, page_html: str | None) -> List[HabrOrderData] | List[None]:
        if page_html:
            orders_data: List[HabrOrderData] = []
            soup = BeautifulSoup(page_html, 'lxml')
            link = soup.find('link').get('href')
            host = 'https://' + urlparse(link).netloc if link else None
            orders_list: List = soup.find_all('li', 'content-list__item')
            if not orders_list:
                logger.warning('Список заказов не найден на странице (возможно изменилась разметка)')
                return []
            for order in orders_list:
                order_title_wrap = order.find('div', 'task__title')
                order_url: str = order_title_wrap.find('a').get('href') if order_title_wrap else None
                order_url = urljoin(host, order_url)
                try:
                    order_id = int(order_url.split('/')[-1])
                except Exception:
                    logger.warning('Невозможно получить id заказа {order_url}, заказ не будет обработан')
                    continue
                order_title = order_title_wrap.text if order_title_wrap else None
                # order_tags = order.find_all('a', 'tags__item_link')
                # order_tags = [tag.text for tag in order_tags] if order_tags else []
                price = order.find('span', 'count')
                price = int(''.join(filter(str.isdigit, price.text.strip()))) if price else None

                tmp_order_data = await self._create_order_data_obj(
                    order_id=order_id,
                    # load_date=None,
                    order_url=order_url,
                    order_title=order_title,
                    price=price
                )

                orders_data.append(tmp_order_data)
            return orders_data
        else:
            return []


class FLParser(Parser):
    def __init__(self, ):
        self.order_data_obj_type = FlOrderData

    async def parse_data(self, page_html: str | None) -> List[FlOrderData] | List[None]:
        if page_html:
            orders_data: List[FlOrderData] = []
            soup = BeautifulSoup(page_html, 'lxml')
            link = soup.find('link').get('href')

            host = 'https://' + urlparse(link).netloc if link else None
            pattern = re.compile(r'^project-item\d+$')
            orders_list: List = soup.find_all(id=pattern)

            if not orders_list:
                logger.warning('Список заказов не найден на странице (возможно изменилась разметка)')
                return []
            for order in orders_list:
                order_title_wrap = order.find('div', 'b-post__grid')
                order_url: str = order_title_wrap.find('a').get('href') if order_title_wrap else None
                order_url = urljoin(host, order_url)
                try:
                    order_id = int(order_url.split('/')[-2])
                except Exception:
                    logger.warning('Невозможно получить id заказа {order_url}, заказ не будет обработан')
                    continue
                order_title = order_title_wrap.text.rstrip().replace('\n', '') if order_title_wrap else None
                # order_tags = order.find_all('a', 'tags__item_link')
                # order_tags = [tag.text for tag in order_tags] if order_tags else []
                price = order.find('h2').find_next_sibling().text
                pattern = re.compile(r'<span class="text-4 text-dark text-decoration-none">(.*?)</span>', re.DOTALL)
                match = BeautifulSoup(pattern.search(price).group(), 'lxml').text

                def extract_number(text):
                    text = text.replace('\xa0', ' ')
                    text = re.sub(r'\s', '', text)
                    match = re.search(r'\b(\d{1,3}(?:,\d{2})?|\d+)\s*руб\b', text)
                    if match:
                        return int(match.group(1))
                    match = re.search(r'\b(\d{1,3}(?:,\d{2})?|\d+)\s*—\s*(\d{1,3}(?:,\d{2})?|\d+)\s*₽', text)
                    if match:
                        return int(match.group(2))
                    match = re.search(r'\b(\d{1,3}(?:,\d{2})?|\d+)\s*руб\b', text)
                    if match:
                        return int(match.group(1))
                    return None

                price = extract_number(match)

                tmp_order_data = await self._create_order_data_obj(
                    order_id=order_id,
                    # load_date=None,
                    order_url=order_url,
                    order_title=order_title,
                    price=price
                )
                orders_data.append(tmp_order_data)
            return orders_data
        else:
            return []


class YouDoParser(Parser):
    def __init__(self, ):
        self.order_data_obj_type = YoudoOrderData

    async def parse_data(self, page_html: str | None) -> List[YoudoOrderData] | List[None]:
        if page_html:
            orders_data: List[YoudoOrderData] = []
            soup = BeautifulSoup(page_html, 'lxml')
            link = soup.find('meta', {'property': 'og:url'}).get('content')
            host = 'https://' + urlparse(link).netloc if link else None
            orders_list: List = soup.find_all(class_=re.compile(r'TasksList_listItem__\w{5}'))
            orders_list = [item for item in orders_list if len(item.get('class')) == 1] if orders_list else None
            if not orders_list:
                logger.warning('Список заказов не найден на странице (возможно изменилась разметка)')
                return []
            for order in orders_list:

                order_title = order.find('a', class_=re.compile(r'TasksList_title__\w{5}'))
                order_title = order_title.text if order_title else None

                order_url: str = order.find('a', class_=re.compile(r'TasksList_title__\w{5}'))
                order_url = order_url.get('href').split('?')[0] if order_url else None
                order_url = urljoin(host, order_url)

                try:
                    order_id = int(order_url.split('/')[-1][1:])
                except Exception:
                    logger.warning('Невозможно получить id заказа {order_url}, заказ не будет обработан')
                    continue

                price = order.find('div', class_=re.compile(r'TasksList_price__\w{5}'))
                price = price.text if price else None

                def extract_price(input_string):
                    price_pattern = re.compile(r'\b(\d{1,3}(?:\s?\d{3})*)(?:\s?(?:₽|р|р\.|руб))?\b', re.IGNORECASE)
                    match = price_pattern.search(input_string)
                    if match:
                        price_str = match.group(1).replace(' ', '')
                        return int(price_str)
                    else:
                        return None

                price = extract_price(price)

                tmp_order_data = await self._create_order_data_obj(
                    order_id=order_id,
                    # load_date=None,
                    order_url=order_url,
                    order_title=order_title,
                    price=price
                )
                orders_data.append(tmp_order_data)
            return orders_data
        else:
            return []


async def main():
    from downloader import StaticDownloader, DynamicDownloader
    from models import RequestPageData

    start_time = time.time()

    page = RequestPageData.from_url('https://freelance.habr.com/tasks')
    downloader = StaticDownloader()
    page_text = await downloader.download_html(page)
    parser = HabrParser()
    res = await parser.parse_data(page_text)

    logger.debug(res)
    logger.debug(len(res))

    page1 = RequestPageData.from_url('https://www.fl.ru/projects/')
    downloader1 = DynamicDownloader()
    page_text1 = await downloader1.download_html(page1)

    parser1 = FLParser()
    res = await parser1.parse_data(page_text1)
    logger.debug(res)
    logger.debug(len(res))

    page2 = RequestPageData.from_url('https://youdo.com/tasks-all-opened-all')
    downloader2 = DynamicDownloader()
    page_text2 = await downloader2.download_html(page2)
    parser1 = YouDoParser()
    res = await parser1.parse_data(page_text2)
    logger.debug(res)
    logger.debug(len(res))

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Время выполнения: {execution_time} секунд")


if __name__ == '__main__':
    asyncio.run(main())

#
# async def main():
#     from downloader import StaticDownloader
#     from models import RequestPageData
#
#     page = RequestPageData.from_url('https://freelance.habr.com/tasks')
#     downloader = StaticDownloader()
#     page_text = await downloader.download_html(page)
#     parser = HabrParser()
#     res = await parser.parse_data(page_text)
#     print(res)
#
#
# if __name__ == '__main__':
#     asyncio.run(main())

import asyncio
from abc import ABC, abstractmethod
from typing import List
from urllib.parse import urlparse, urljoin
from loguru import logger
from bs4 import BeautifulSoup

from models import OrderData


class Parser(ABC):

    @abstractmethod
    async def parse_data(self, page_html: str | None) -> List[OrderData] | None:
        """Возвращает спсиок новых заказов"""
        pass


class HabrParser(Parser):
    async def parse_data(self, page_html: str | None) -> List[OrderData] | List[None]:
        if page_html:
            orders_data : List[OrderData] = []
            soup = BeautifulSoup(page_html, 'lxml')
            link = soup.find('link').get('href')
            host = 'https://' + urlparse(link).netloc if link else None
            orders_list : List = soup.find_all('li', 'content-list__item')
            if not orders_list:
                logger.warning('Список заказов не найден на странице (возможно изменилась разметка)')
                return []
            for order in orders_list:
                order_title_wrap = order.find('div','task__title')
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

                tmp_order_data = OrderData(
                    order_id=order_id,
                    load_date=None,
                    url=order_url,
                    title=order_title,
                    price=price
                )
                orders_data.append(tmp_order_data)
            return orders_data
        else: return []







async def main():
    from downloader import StaticDownloader
    from models import RequestPageData

    page = RequestPageData.from_url('https://www.fl.ru/projects/')
    downloader = StaticDownloader()
    page_text = await downloader.download_html(page)
    parser = HabrParser()
    res = await parser.parse_data(page_text)
    print(res)


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

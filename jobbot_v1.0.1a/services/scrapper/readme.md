(1)
scheduler --> <проверить наличие новых заказов на сайте>

1. спарсить с сайта заказаы с id больше чем последний id в бд сервиса(или кэше от предидущего запроса).
2. записать их бд сервиса.
3. отправить их на сервис "search_engine"


(2)
{<id заказа>:{name:<название заказа>, description: <описание заказа>,tags: <теги>, count_per_hour: <почасова оплата>, count:  <фиксированная цена>, responses: <количество откликов>, customer rating: <рейтинг заказчика},}
--> search_engine
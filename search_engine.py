from logger import logger

class SearchEngine:
    async def create_notifications(self, new_data_from_update, users_request_data) -> list:
        logger.debug(new_data_from_update)
        logger.debug(users_request_data)
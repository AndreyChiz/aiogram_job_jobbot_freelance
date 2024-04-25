class SearchEngine:
    async def create_notifications(self, new_data_from_update, users_request_data) -> list:
        """
        Creates a list of user IDs for mailing
        """
        result = []
        for order in new_data_from_update:
            tmp = {order.url:[]}
            for user in users_request_data:
                for word in user["user_keywords"]:
                    if word.lower() in order.title.lower():
                        tmp[order.url].append(user["user_id"])
                        break
            if tmp[order.url]:
                result.append(tmp)
        new_data_from_update.clear()
        return result

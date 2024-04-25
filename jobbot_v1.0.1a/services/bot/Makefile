.PHONY: run
.PHONY: clean

#ЗАПУСК
run:
	docker build -t bot . && docker run -it -d -p 443:443 --name bot_container bot && docker logs -f bot_container

# УДАЛЕНИЕ
clean:
	docker stop bot_container && docker rm bot_container

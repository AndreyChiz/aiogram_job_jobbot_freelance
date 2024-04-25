.PHONY: run
.PHONY: clean

#ЗАПУСК
run:
	cd src && docker build -t myapp . && docker run -it -d -p 8080:8000 --name myapp_container myapp && docker logs -f myapp_container

# УДАЛЕНИЕ
clean:
	docker stop myapp_container && docker rm myapp_container

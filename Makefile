.PHONY : start stop

start:
	docker-compose up -d redis
stop:
	docker-compose rm -s
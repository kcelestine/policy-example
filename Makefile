.PHONY : start stop test

start:
	docker-compose up -d redis
stop:
	docker-compose rm -s
test:
	cd src && python -m pytest tests
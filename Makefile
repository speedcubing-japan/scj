up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

restart-python:
	docker stop scj_python_1
	docker-compose up -d

makemigrations:
	docker-compose run python ./manage.py makemigrations app

migrate:
	docker-compose run python ./manage.py migrate

migrate-auth:
	docker-compose run python ./manage.py migrate auth

migrate-app:
	docker-compose run python ./manage.py migrate app

sqlmigrate:
	docker-compose run python ./manage.py sqlmigrate app ${ID}

createsuperuser:
	docker-compose run python ./manage.py createsuperuser

collectstatic:
	docker-compose run python ./manage.py collectstatic

makerankpandas:
	docker-compose run python ./manage.py makerankpandas

getdata:
	docker-compose run python ./manage.py getdata

dumpdata:
	docker-compose run python ./manage.py dumpdata app.${MODEL} > ${MODEL}.json

makedata:
	docker-compose run python ./manage.py makedata

getwcadata:
	docker-compose run python ./manage.py getwcadata

loaddata:
	docker-compose run python ./manage.py loaddata ${MODEL}.json

load-compdata:
	docker-compose run python ./manage.py loaddata competition.json
	docker-compose run python ./manage.py loaddata round.json
	docker-compose run python ./manage.py loaddata feeperevent.json
	docker-compose run python ./manage.py loaddata feepereventcount.json

load-wcadata:
	docker exec -it scj_db_1 sh /etc/mysql/fixtures/sql/wca_import.sh

load-proddata:
	scp scj:~/backup/*.json python/src/app/fixtures/
	docker-compose run python ./manage.py loaddata user.json
	docker-compose run python ./manage.py loaddata person.json
	docker-compose run python ./manage.py loaddata competitor.json
	docker-compose run python ./manage.py loaddata information.json
	docker-compose run python ./manage.py loaddata stripeprogress.json
	rm -rf python/src/app/fixtures/user.json
	rm -rf python/src/app/fixtures/person.json
	rm -rf python/src/app/fixtures/competitor.json
	rm -rf python/src/app/fixtures/information.json
	rm -rf python/src/app/fixtures/stripeprogress.json

bulkdata:
	docker-compose run python ./manage.py bulkdata

prod-bulkdata:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py bulkdata

prod-build:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose build

prod-build-no-cache:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose build --no-cache

prod-up:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose up -d

prod-restart:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose restart

prod-restart-python:
	docker stop scj_python_1
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose up -d

prod-load-compdata:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py loaddata competition.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py loaddata round.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py loaddata feeperevent.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py loaddata feepereventcount.json

prod-load-wcadata:
	docker exec -it scj_db_1 sh /etc/mysql/fixtures/sql/wca_import.sh

prod-dumpdata:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py dumpdata app.${MODEL} > ${MODEL}.json

prod-backup:
	rm -rf /home/admin/backup/*
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py dumpdata app.user > /home/admin/backup/user.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py dumpdata app.person > /home/admin/backup/person.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py dumpdata app.competitor > /home/admin/backup/competitor.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py dumpdata app.information > /home/admin/backup/information.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run python ./manage.py dumpdata app.stripeprogress > /home/admin/backup/stripprogress.json

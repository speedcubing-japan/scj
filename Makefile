up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

restart-python:
	docker stop scj_python_1
	docker-compose up -d

restart-nginx:
	docker stop scj_nginx_1
	docker-compose up -d

test:
	docker-compose run --rm python ./manage.py test

makemigrations:
	docker-compose run --rm python ./manage.py makemigrations app

migrate:
	docker-compose run --rm python ./manage.py migrate

migrate-auth:
	docker-compose run --rm python ./manage.py migrate auth

migrate-app:
	docker-compose run --rm python ./manage.py migrate app

sqlmigrate:
	docker-compose run --rm python ./manage.py sqlmigrate app ${ID}

createsuperuser:
	docker-compose run --rm python ./manage.py createsuperuser

stripe-listen:
	stripe listen --forward-to localhost:8000/stripe/webhook/

stripe-listen-connect:
	stripe listen --forward-to localhost:8000/stripe/webhook/connect/

makemessages:
	docker-compose run --rm python django-admin makemessages -l en

compilemessages:
	docker-compose run --rm python django-admin compilemessages

collectstatic:
	docker-compose run --rm python ./manage.py collectstatic

makerankpandas:
	docker-compose run --rm python ./manage.py makerankpandas

getdata:
	docker-compose run --rm python ./manage.py getdata

dumpdata:
	docker-compose run --rm python ./manage.py dumpdata app.${MODEL} > ${MODEL}.json

makedata:
	docker-compose run --rm python ./manage.py makedata

getwcadata:
	docker-compose run --rm python ./manage.py getwcadata

resetwca:
	docker-compose run --rm python ./manage.py resetwca --person_id ${PERSON_ID}

loadcompetitor:
	docker-compose run --rm python ./manage.py loadcompetitor

loaddata:
	docker-compose run --rm python ./manage.py loaddata ${MODEL}.json

load-compdata:
	docker-compose run --rm python ./manage.py loaddata competition.json
	docker-compose run --rm python ./manage.py loaddata round.json
	docker-compose run --rm python ./manage.py loaddata feeperevent.json
	docker-compose run --rm python ./manage.py loaddata feepereventcount.json

load-proddata:
	scp scj:~/backup/*.json python/src/app/fixtures/
	docker-compose run --rm python ./manage.py loaddata user.json
	docker-compose run --rm python ./manage.py loaddata person.json
	docker-compose run --rm python ./manage.py loaddata competitor.json
	docker-compose run --rm python ./manage.py loaddata information.json
	docker-compose run --rm python ./manage.py loaddata stripeprogress.json
	rm -rf python/src/app/fixtures/user.json
	rm -rf python/src/app/fixtures/person.json
	rm -rf python/src/app/fixtures/competitor.json
	rm -rf python/src/app/fixtures/information.json
	rm -rf python/src/app/fixtures/stripeprogress.json

bulkdata:
	docker-compose run --rm python ./manage.py bulkdata

clearsessions:
	docker-compose run --rm python ./manage.py clearsessions

prod-bulkdata:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py bulkdata

prod-resetwca:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py resetwca --person_id ${PERSON_ID}

prod-loadcompetitor:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py loadcompetitor

prod-build:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose build

prod-build-no-cache:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose build --no-cache

prod-up:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose up -d

prod-build-up:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose up -d --build

prod-restart:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose restart

prod-restart-python:
	docker stop scj_python_1
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose up -d

prod-load-compdata:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py loaddata competition.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py loaddata round.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py loaddata feeperevent.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py loaddata feepereventcount.json

prod-dumpdata:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py dumpdata app.${MODEL} > ${MODEL}.json

prod-backup:
	rm -rf /home/admin/backup/*
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py dumpdata app.user > /home/admin/backup/user.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py dumpdata app.person > /home/admin/backup/person.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py dumpdata app.competitor > /home/admin/backup/competitor.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py dumpdata app.information > /home/admin/backup/information.json
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py dumpdata app.stripeprogress > /home/admin/backup/stripeprogress.json

prod-clearsessions:
	COMPOSE_FILE=docker-compose.yml:docker-compose-prod.yml docker-compose run --rm python ./manage.py clearsessions

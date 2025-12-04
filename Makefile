DC := docker compose run --rm

.PHONY: test lint start stop

test-order:
	$(DC) order-service pytest -vv

lint:
	$(DC) order-service ruff check --fix . && ruff format .

create-migration-order:
	$(DC) order-service bash -c "alembic revision --autogenerate"

setup-database-order:
	$(DC) order-service alembic upgrade head && $(DC) payment-service alembic upgrade head 

start: setup-database-order
	docker compose up -d

stop:
	docker compose down
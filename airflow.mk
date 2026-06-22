ENV_FILE=--env-file .env.airflow
COMPOSE_FILE=-f airflow-services.yaml
DOCKER_COMPOSE=docker compose $(ENV_FILE) $(COMPOSE_FILE)
DAG_ID=sentinel_pipeline

.PHONY: up down init-fresh trigger status logs

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

init-fresh:
	$(DOCKER_COMPOSE) down -v
	$(DOCKER_COMPOSE) build --no-cache
	$(DOCKER_COMPOSE) up -d

trigger:
	docker exec -it $$(docker ps -qf "name=airflow-scheduler") airflow dags trigger $(DAG_ID)

status:
	$(DOCKER_COMPOSE) ps

logs:
	$(DOCKER_COMPOSE) logs -f airflow-scheduler
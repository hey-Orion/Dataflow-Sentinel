.PHONY: help install run test clean docker_build docker_test docker_run docker_clean docker_all

include airflow.mk

help:
	@echo "Available commands:"
	@echo "  make install        Install Python dependencies"
	@echo "  make run            Run the Sentinel Pipeline locally"
	@echo "  make test           Run all tests via pytest"
	@echo "  make clean          Remove local data artifacts"
	@echo ""
	@echo "  Airflow Core Shortcuts (via airflow.mk):"
	@echo "    make up             Spin up Airflow environment"
	@echo "    make down           Stop Airflow environment"
	@echo "    make init-fresh     Completely reset and rebuild Airflow"
	@echo "    make trigger        Force trigger the sentinel_pipeline DAG"
	@echo "    make status         Check container statuses"


# Local execution commands
install: requirements.txt
	python -m pip install --upgrade pip
	pip install -r requirements.txt

test:
	python -m pytest -v tests/

run:
	python -m src.pipeline

clean:
	rm -rf data/bronze/*
	rm -rf data/silver/*
	rm -rf data/gold/*


# App-specific Docker execution commands

docker_build:
	docker compose build

docker_test: docker_build
	docker compose run --rm pipeline python -m pytest -v tests/

docker_run: docker_build
	docker compose run --rm pipeline

docker_clean:
	rm -rf data/bronze/*
	rm -rf data/silver/*
	docker compose down --volumes --remove-orphans

docker_all: docker_test docker_run docker_clean
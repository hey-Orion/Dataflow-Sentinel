.PHONY: help install run test clean docker_build docker_test docker_run docker_clean docker_all

help:
	@echo "Available commands:"
	@echo "  make install        Install Python dependencies"
	@echo "  make run            Run the Sentinel Pipeline"
	@echo "  make test           Run all tests"
	@echo "  make docker_all     Build, test, and run inside Docker"
	@echo "  make docker_clean   Remove Docker containers, volumes, and orphans"
	@echo "  make clean          Remove local data artifacts"


# local execution commands--

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


# Docker execution commands--

docker_build:
	docker compose build

docker_test: docker_build
	docker compose run --rm pipeline python -m pytest -v tests/

docker_run: docker_build
	docker compose run --rm pipeline

docker_clean:
	rm -rf data/bronze/*
	rm -rf data/silver/*
#	rm -rf data/gold/*
	docker compose down --volumes --remove-orphans


docker_all: docker_test docker_run docker_clean

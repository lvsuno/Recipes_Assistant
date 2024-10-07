init-docker:
	docker-compose up

pull-phi3:
	docker-compose exec ollama ollama pull phi3


init-index-db:
	docker-compose exec streamlit python recipe_assistant/prep.py

setup:
	pipenv install --dev
	pipenv shell
	pre-commit install

quality-checks:
	pylint --recursive=y .
	black .
	isort .

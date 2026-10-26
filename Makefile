.PHONY: setup train test api web lint sample
setup:
	python -m pip install -r requirements-dev.txt
sample:
	python scripts/generate_demo.py
train:
	python -m ml.training.train
api:
	uvicorn backend.app.main:app --reload
web:
	cd frontend && npm run dev
lint:
	ruff check ml backend tests scripts

test:
	pytest -q

install:
	pip install -r requirements.txt

test:
	pytest -q

evaluate:
	python -m src.evaluate

demo:
	python -m src.demo "Should we prioritize reducing first-response time or improving self-service documentation?"

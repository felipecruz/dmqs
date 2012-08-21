test:
	py.test --verbos .

coverage:
	py.test --cov-report html --cov .

clean:
	find . -name "*.pyc" -delete

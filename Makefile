test:
	py.test --verbos .

coverage:
	py.test --cov-report html --cov .

clean:
	rm -rf htmlcov/
	rm -rf build/
	find . -name "*.pyc" -delete

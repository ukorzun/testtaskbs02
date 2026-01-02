.PHONY: install test test-allure test-html allure-serve

install:
	python -m pip install -r requirements.txt

test:
	pytest

test-allure:
	pytest --alluredir=artifacts/allure-results

test-html:
	pytest --html=artifacts/report.html --self-contained-html

allure-serve:
	allure serve artifacts/allure-results

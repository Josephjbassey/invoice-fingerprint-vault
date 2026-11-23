.PHONY: setup run test lint format check invoices video clean help

PYTHON ?= ./venv/bin/python
PIP ?= ./venv/bin/pip
GNOROOT ?= $(HOME)/.gno/gno
GNO ?= $(HOME)/.gno/bin/gno

help:
	@echo "Invoice Fingerprint Vault — Developer CLI Commands"
	@echo "================================================="
	@echo "  make setup     - Create Python venv and install dependencies"
	@echo "  make run       - Start Django local development server"
	@echo "  make test      - Run Go, Gno, and Django unit test suites"
	@echo "  make lint      - Check code compliance and formatting (Ruff + Go)"
	@echo "  make format    - Auto-format codebase (Ruff + Gofmt)"
	@echo "  make invoices  - Generate sample PDF test invoices"
	@echo "  make video     - Record and build automated demo video"
	@echo "  make clean     - Clean temporary artifacts and cache"

setup:
	python3 -m venv venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PYTHON) manage.py migrate

run:
	$(PYTHON) manage.py runserver 127.0.0.1:8000

test:
	@echo "=== Running Go Realm Unit Tests ==="
	go test -v ./realm/
	@echo "\n=== Running Gno.land Native Tests ==="
	@cd realm && GNOROOT=$(GNOROOT) $(GNO) test .
	@echo "\n=== Running Django App Security & Integration Tests ==="
	$(PYTHON) manage.py test

lint:
	$(PYTHON) -m ruff check --exclude django_app/migrations django_app vault_project scripts
	go vet ./realm/

format:
	$(PYTHON) -m ruff format django_app vault_project scripts
	$(PYTHON) -m ruff check --fix --exclude django_app/migrations django_app vault_project scripts
	gofmt -s -w ./realm/

check:
	$(PYTHON) manage.py check --deploy

invoices:
	$(PYTHON) scripts/generate_sample_invoices.py
	@for f in sample_invoices/*.pdf; do pdftoppm -png -r 150 "$$f" "$${f%.pdf}"; done
	@mkdir -p static/invoices
	@cp sample_invoices/*.png static/invoices/
	@echo "Generated sample invoices in sample_invoices/ and static/invoices/"

video:
	$(PYTHON) scripts/generate_narration.py
	$(PYTHON) scripts/record_demo_video.py

clean:
	rm -rf __pycache__ django_app/__pycache__ vault_project/__pycache__ scripts/__pycache__
	rm -rf media/video_raw

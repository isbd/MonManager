VENV := venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

$(VENV): requirements.txt ## Create the venv and install the requirements
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

seed: $(VENV) ## Seed the data in the database
	$(PYTHON) seed.py moves
	$(PYTHON) seed.py species
	$(PYTHON) seed.py shops


clean: ## Remove the venv
	rm -rf $(VENV)

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk -F '##' '{printf "%-15s %s\n", $$1, $$2}'

.PHONY: help install test check format build clean

UV_RUN ?= uv run --locked

help:  ## This help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install package for development
	@uv sync --locked

# Fixtures load the plugin after coverage starts, avoiding unmeasured imports.
test:
	@$(UV_RUN) pytest -p no:testdox tests/ --cov pytest_testdox --cov-report=xml --junitxml=junit.xml -o junit_family=legacy

check:  ## Run static code checks
	@$(UV_RUN) mypy pytest_testdox tests
	@$(UV_RUN) ruff check .
	@$(UV_RUN) ruff format --check .

format:  ## Format code and sort imports
	@$(UV_RUN) ruff check --fix .
	@$(UV_RUN) ruff format .

build:  ## Build wheel and source distribution
	@uv build

clean:  ## Clean cache and temporary files
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@rm -rf *.egg-info
	@rm -rf dist/
	@rm -rf build/

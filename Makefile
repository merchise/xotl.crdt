RYE_EXEC ?= rye run
PYTHON_VERSION ?= 3.12
CARGO_HOME ?= $(HOME)/.cargo
PATH := $(HOME)/.rye/shims:$(CARGO_HOME)/bin:$(PATH)

SHELL := /bin/bash
PYTHON_FILES := $(shell find src/$(PROJECT_NAME) -type f -name '*.py' -o -name '*.pyi')

USE_UV ?= true
install:
	@uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh
	@rye self update || curl -sSf https://rye-up.com/get | RYE_INSTALL_OPTION="--yes" bash
	@rye config --set-bool behavior.use-uv=$(USE_UV)
	@rye pin --relaxed $(PYTHON_VERSION)
	@rye sync --no-lock
.PHONY: install

format:
	@$(RYE_EXEC) ruff --fix src/
	@$(RYE_EXEC) isort src/
	@$(RYE_EXEC) ruff format src/
.PHONY: format

lint:
	@$(RYE_EXEC) ruff src/
	@$(RYE_EXEC) ruff format --check src/
	@$(RYE_EXEC) isort --check src/
.PHONY: lint

test:
	@$(RYE_EXEC) tox -e system-unit -- -n auto
.PHONY: test

doctest:
	@$(RYE_EXEC) tox -e system-doctest
.PHONY: test

mypy:
	@$(RYE_EXEC) tox -e system-staticcheck
.PHONY: mypy

docs:
	make SPHINXBUILD="$(RYE_EXEC) sphinx-build" -C docs html
.PHONY: docs


CADDY_SERVER_PORT ?= 9999
caddy: docs
	@docker run --rm -p $(CADDY_SERVER_PORT):$(CADDY_SERVER_PORT) \
         -v $(PWD)/docs/build/html:/var/www -it caddy \
         caddy file-server --browse --listen :$(CADDY_SERVER_PORT) --root /var/www
.PHONY: caddy

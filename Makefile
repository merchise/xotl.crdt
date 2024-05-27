RYE_EXEC ?= rye run
PYTHON_VERSION ?= 3.12
CARGO_HOME ?= $(HOME)/.cargo
PATH := $(HOME)/.rye/shims:$(CARGO_HOME)/bin:$(PATH)

SHELL := /bin/bash
PYTHON_FILES := $(shell find src/$(PROJECT_NAME) -type f -name '*.py' -o -name '*.pyi')

USE_UV ?= true
REQUIRED_UV_VERSION ?= 0.2.2
REQUIRED_RYE_VERSION ?= 0.34.0
bootstrap:
	@INSTALLED_UV_VERSION=$$(uv --version 2>/dev/null | awk '{print $$2}' || echo "0.0.0"); \
    UV_VERSION=$$(printf '%s\n' "$(REQUIRED_UV_VERSION)" "$$INSTALLED_UV_VERSION" | sort -V | head -n1); \
	if [ "$$UV_VERSION" != "$(REQUIRED_UV_VERSION)" ]; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi
	@INSTALLED_RYE_VERSION=$$(rye --version 2>/dev/null | head -n1 | awk '{print $$2}' || echo "0.0.0"); \
	DETECTED_RYE_VERSION=$$(printf '%s\n' "$(REQUIRED_RYE_VERSION)" "$$INSTALLED_RYE_VERSION" | sort -V | head -n1); \
	if [ "$$DETECTED_RYE_VERSION" != "$(REQUIRED_RYE_VERSION)" ]; then \
		rye self update || curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" RYE_VERSION="$(REQUIRED_RY_VERSION)" bash; \
	fi
	@rye config --set-bool behavior.use-uv=$(USE_UV)
	@rye pin --relaxed $(PYTHON_VERSION)

install: bootstrap
	@rye sync -f
.PHONY: install

sync: bootstrap
	@rye sync --no-lock
.PHONY: sync

lock: bootstrap
	@rye sync
.PHONY: lock


format:
	@$(RYE_EXEC) ruff check --fix src/
	@$(RYE_EXEC) isort src/
	@$(RYE_EXEC) ruff format src/
.PHONY: format

lint:
	@$(RYE_EXEC) ruff check src/
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

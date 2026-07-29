.PHONY: serve build dev

build:
	uv run python src/analysis/build_dashboard.py

serve: build
	uv run python src/serve.py --port 8080

dev: build
	uv run python src/serve.py --port 8080 --no-auth

**Python google drive mcp server**

create a venv with uv : `uv sync`

create .env with
DATABASE_URL=
CLIENT_ID=
CLIENT_SECRET=
USER_ID=

run fast api with uv : `uv run arc/app/main.py`
run mcp server with `uv run src/mcp_server/main.py`
run mcp client with : `uv run src/mcp_client/main.py`

Currently working on getting oauth and db access into python

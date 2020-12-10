# Clean architecture experiment


[Install `poetry`](https://python-poetry.org/docs/#installation)

Setup env & deps

```
python -m venv .venv
poetry install
```

Run server on [localhost:8000](http://localhost:8000/timemgmt/docs)

```
uvicorn --reload tempus.main:app
```

Run tests

```
pytest tests
```

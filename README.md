# Clean architecture experiment


[Install `poetry`](https://python-poetry.org/docs/#installation)

Setup env & deps

```
python -m venv .venv
poetry install
```

Setup Postgres
```
docker run -d \
    --name tempus-postgres \
    -e POSTGRES_DATABASE=tempus \
    -e POSTGRES_USER=tempus \
    -e POSTGRES_PASSWORD=pgpassword \
    -p 25432:5432 \
    postgres
sleep 5
docker exec tempus-postgres bash -c 'psql -U tempus -c "CREATE DATABASE tempus_django;"'
```

Create .env files
```
cp local.env.sample local.env
cp test.env.sample test.env
```

Run migrations
```
# legacy django app
python manage-django.py migrate
# tempus part
python -m tempus.migrations _all_ upgrade head
```

Run server on [localhost:8000](http://localhost:8000/timemgmt/docs)
```
uvicorn --reload tempus.main:app
```

Run tests
```
pytest tests
```

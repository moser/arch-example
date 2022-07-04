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

## Motivation

This experiment came about when we had a large Django app that progressively
made us slower because we were missing autonomy of teams maintaining different
parts.

The whole thing is heavly inspired by

- the [cosmic python book](https://www.cosmicpython.com/book/preface.html) 
- the [clean / hexagonal architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- the idea of [the majestic monolith](https://m.signalvnoise.com/the-majestic-monolith/)

## How

The application is split into two general parts.

There is the `legacy` part, a Django
app. Here it is just a very simple one, but in our real case it would be a very
large one.

Secondly, there is the `tempus` part which consists of small modules (called
applications here, but that might be the wrong name).

The idea is that functionality would move from the legacy app to the smaller
apps in the `tempus` part over time.

Because we would like to achieve independence of different modules we set rules
that different apps cannot import each other directly. Instead applications can
define interfaces (see `legacy/something/entrypoints`) and other apps can have
those dependency-injected on request (see `tempus/timemgmt/service_layer`).

Certain things are discouraged/forbidden:
- DB transactions across multiple apps
- Direct imports between apps

Within the small apps we tried to apply a couple of concepts:
- clean / hexagonal architecture
- good testability (without relying on a database whereever possible)
- command / query separation
- event driven communications between apps (only stubbed)

# api-permission-manager

API for managing permissions

## How to build docker-image
```bash
$ docker-compose build

```

If you want to clone private repositories on GitHub while building the image,
use the following commands instead.
```bash
$ ssh-agent
$ ssh-add
$ export DOCKER_BUILDKIT=1
$ docker built -t api:latest . --ssh=default

```


## How to run the API server
Make sure to build the image first.
```bash
$ docker-compose up

```

You can update the behavior of your API by editing `api/server.py` while running the server

## How to migrate database changes

[Aerich](https://github.com/tortoise/aerich) is used as a database migration tool.
After editing model, execute `migrate` command:
```bash
$ docker-compose exec api aerich migrate
```

And upgrade the database:
```bash
$ docker-compose exec api aerich upgrade
```

However, aerich does no support many of database editing commands (e.g. drop table) for SQLite. Use PostgreSQL, MySQL, etc. for enable migration using aerich.


## Environment Variables

- `API_DEBUG`: Enable debug mode if true.
- `DB_URL`: URL for database. If not set, "sqlite://db.sqlite3" will be used.
- `SECRET_KEY`: Secret key for the app.

*Patty* is a web application designed to help the MALIN team experiment with adapting exercises using LLMs and other AI tools.

# Authors

(in `random.shuffle` order)

- [Elise Lincker](https://github.com/eliselinc/) (classification)
- [Mohamed Amine Lasheb](https://aminelasheb.github.io/) (extraction)
- [Vincent Jacques](https://vincent-jacques.net/) (everything else)

# Documentation

There is little documentation because our small team focuses on creating a working prototype.
There is however a [graph of the DB tables](backend/generated/db-tables-graph.png), generated from the ORM models.


# Development

## Dependencies

Bash, Python and Docker (with `docker compose`).

## Scripts

`./dev.sh run` starts the development environment. You can then visit http://localhost:8080/.

While the development environment is running, `./dev.sh cycle` runs all checks (linter, type checkers, tests, etc.).

Use `./dev.sh --help` to list other commands available.

# Production

`./prod.sh preview` runs a production-like environment locally.

`./prod.sh pre-warm-build-cache` pulls base Docker images and installs dependencies, keeping result in cache.
It lets you choose when you want to run the long part of the build.

`./prod.sh publish` publishes new Docker images.
It does *not* pull the base images, so you should have run `./prod.sh pre-warm-build-cache` in the not-so-distant past.

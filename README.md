*Patty* is a web application designed to help the MALIN team experiment with adapting exercises using LLMs and other AI tools.


# Documentation

There is little documentation because our small team focuses on creating a working prototype.
There is however a [graph of the DB tables](backend/generated/db-tables-graph.png), generated from the ORM models.


# Development

## Dependencies

Bash, Python and Docker (with `cocker compose`).

## Scripts

`./dev.sh run` starts the development environment. You can then visit http://localhost:8080/.

While the development environment is running, `./dev.sh cycle` runs all checks (linter, type checkers, tests, etc.).

Use `./dev.sh --help` to list other commands available.

# Production

`./prod.sh preview` runs a production-like environment locally.

`./prod.sh publish` publishes new Docker images.

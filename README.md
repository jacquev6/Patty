*Patty* is an interface to help the MALIN team experiment with generating adapted exercises using an LLM.


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

# Car Rental Backend

## Install pre-commit hooks

```bash
pre-commit install
```

Once set up, pre-commit hooks will run automatically on every commit. The configuration file is `.pre-commit-config.yaml` in the root of the repository.

## Docker build

```bash
docker build -t fastapi-docker .
```

## Docker run

```bash
docker run -d -p 8000:8000 fastapi-docker
```

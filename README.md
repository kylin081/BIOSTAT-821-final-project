# Clinical Data System

A lightweight clinical data backend system built with Python, SQLite, FastAPI, and Docker.  
This project stores patient information and lab results, analyzes data through a Python library, and exposes query endpoints via a REST API.

---

## Architecture

```
clinical-data-system/
├── clinical/              # Core Python library (business logic)
│   ├── __init__.py
│   ├── patients.py        # Patient-related functions
│   └── labs.py            # Lab result analysis functions
├── api/                   # FastAPI layer (interface only)
│   ├── __init__.py
│   └── main.py
├── db/                    # Database schema and seed data
│   ├── schema.sql
│   └── seed.py
├── tests/                 # pytest test suite
│   ├── test_patients.py
│   └── test_labs.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml         # Ruff linting config + project metadata
└── README.md
```

### Key design decisions
- **Business logic is fully decoupled from the API.** The `clinical/` package contains all core functions; `api/` only calls them.
- **SQLite** is used for simplicity and portability, no external database server required.
- **Docker** ensures a consistent, reproducible environment across machines.

---

## Quickstart

### Option 1 — Docker (recommended)

```bash
git clone https://github.com/kylin081/clinical-data-system.git
cd clinical-data-system
docker compose up
```

The API will be available at `http://localhost:8000`.  
Interactive API docs: `http://localhost:8000/docs`

### Option 2 — Local Python environment

**Requirements:** Python 3.11+

```bash
git clone https://github.com/<your-username>/clinical-data-system.git
cd clinical-data-system

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# Initialize and seed the database
python db/seed.py

# Start the API server
uvicorn api.main:app --reload
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/patients/{id}` | Get patient info by ID |
| GET | `/patients/{id}/labs` | Get all lab results for a patient |
| GET | `/labs/abnormal` | Get all abnormal lab results |

---

## Running Tests

```bash
pytest
```

To see coverage:

```bash
pytest --cov=clinical --cov-report=term-missing
```

---

## Continuous Integration

This project uses GitHub Actions for continuous integration. The CI pipeline runs automatically on every push and pull request to the `main` and `develop` branches.

The CI pipeline includes:
- **Linting**: Code style checks with Ruff
- **Testing**: Full test suite with pytest and coverage reporting

You can see the current CI status in the [Actions tab](https://github.com/kylin081/clinical-data-system/actions) of the repository.

---

## Code Style

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
ruff check .
ruff format .
```

---

## Team

| Name | GitHub |
|------|--------|
| Kylin Sun | @kylin081 |
| Rosella Zheng | @VRosella |
| Shan Lu | @SL1324 |

---

## Generative AI Usage
 
This project used generative AI tools during development. All usage is documented below:
 
| Tool | How it was used | What it produced |
|------|----------------|-----------------|
| Claude | Help us refine the overall project structure and assist in revising the codes | README.md, issue descriptions, test reviews |
 
---

## License

MIT

# MonManager

A Pokemon-like monster server built for ComputerCraft, powered by FastAPI, PostgreSQL — fully Dockerized.

---

## Stack

| Service | Image | Purpose |
|---|---|---|
| `api` | Custom (FastAPI) | REST + WebSocket game server |
| `db` | postgres:16-alpine | Persistent player/monster data |

---

## Requirements

Docker

---

## Quick Start

```bash
# 1. Build and start
make build
make up

# 2. Check API docs
open http://localhost:8000/docs
```

---

## Project Structure

```
├── api
│   ├── crud
│   │   └── ...                     # Database manipulations (Create Read Update Delete)
│   ├── database.py
│   ├── dependencies.py
│   ├── Dockerfile
│   ├── main.py
│   ├── models
│   │   └── ...                     # Database table structure and relationships
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── routes
│   │   └── ...                     # FastAPI endpoint routes
│   ├── schemas
│   │   └── ...                     # FastAPI schemas for endpoint input/output structuring
│   └── services
│       └── ...                     # Backend logic
```

**Structured Flow:**
    routes (filtered by schemas) -> services -> crud -> models

---

## Key Endpoints

player.py
- [X] `POST     /player                     -- create player`
- [X] `GET      /player                     -- [AUTH] list all players`
- [X] `GET      /player/{id}                -- [AUTH] get specific player by id`

monster.py
- [X] `GET    /monster/                     -- [AUTH] list a player's monsters`
- [X] `GET    /monster/{id}                 -- [AUTH] get specific monster by id`

encounter.py
- [X] `POST     /encounter/wild             -- [AUTH] attempt a wild monster`
- [ ] `POST     /encounter/challenge/{id}   -- [AUTH] attempt to challenge a player to encounter`
- [ ] `POST     /encounter/attack           -- [AUTH] attempt an attack`
- [ ] `POST     /encounter/swap             -- [AUTH] attempt to swap monsters`
- [X] `POST     /encounter/surrender        -- [AUTH] forfeit the battle`
- [ ] `GET      /encounter/{id}             -- [AUTH] get the status of a battle (possibly spectating)`
- [ ] `GET      /encounter                  -- [AUTH] get the status of the current battle`

Full docs at: `http://localhost:8000/docs`

---

## ComputerCraft

### Emulation

Emulation can be done utilizing craftos

https://www.craftos-pc.cc/docs/installation

Settings files can be found under
```
~/.local/share/craftos-pc/config/*.json
```
and emulated files are under
```
~/.local/share/craftos-pc/computer/
```

Started with `craftos` command

### Usage

```lua
-- List all players
local res = http.get("http://YOUR_IP:8000/player")
local players = textutils.unserialiseJSON(res.readAll())
res.close()
```
Most endpoints require an API key that is given upon account creation.

---

## Makefile commands

```bash
build:           Build the containers fresh
db-command:      Enter postgres container for SQL commands
down:            Shut the docker containers down
lint:            Linting fixes to the api directory
lint-check:      Check for linting issues without fixes
help:            Show this help message
logs:            View the logs from the docker containers
nuke:            Nuke the database and re-seed it
refresh:         Build the containers fresh then restart them
seed:            Seed the data into the database
up:              Bring the docker containers up
```

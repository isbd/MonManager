# MonManager

A Pokemon-like monster server built for ComputerCraft, powered by FastAPI, PostgreSQL, and Redis — fully Dockerized.

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

TBD

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
- [ ] `POST     /encounter/wild             -- [AUTH] attempt a wild monster`
- [ ] `POST     /encounter/challenge/{id}   -- [AUTH] attempt to challenge a player to encounter`
- [ ] `POST     /encounter/{id}/attack      -- [AUTH] attempt an attack`
- [ ] `POST     /encounter/{id}/swap        -- [AUTH] attempt to swap monsters`
- [ ] `POST     /encounter/{id}/surrender   -- [AUTH] forfeit the battle`
- [ ] `GET      /encounter/{id}             -- [AUTH] get the status of the current battle`

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

## Useful Commands

```bash
make build      # build the containers
make up         # start all services
make down       # stop all services
make refresh    # build the containers and start them back up
make logs       # tail all logs
make db-command # enter db for direct sql commands
make lint       # lint and auto fix api dir. Requires container running
make lint-check # check lint errors in api dir. Requires container running
```

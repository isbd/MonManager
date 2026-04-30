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
- [X] `GET      /player                     -- list all players`
- [X] `GET      /player/{id}                -- get specific player by id`
- [ ] `GET      /player/{id}/monsters       -- list a player's monsters`
- [ ] `GET      /player/{id}/party          -- list a player's party`
- [ ] `GET      /player/{id}/party          -- list a player's party`

monster.py
- [ ] `GET    /monster/{id}                 -- get specific monster by id`

encounter.py
- [ ] `POST     /encounter/wild             -- attempt a wild monster`
- [ ] `GET      /encounter/{id}             -- get the status of the current battle`
- [ ] `POST     /encounter/{id}/attack      -- attempt an attack`
- [ ] `POST     /encounter/{id}/swap        -- attempt to swap monsters`
- [ ] `POST     /encounter/{id}/surrender   -- forfeit the battle`

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

---

## Useful Commands

```bash
make build      # build the containers
make up         # start all services
make down       # stop all services
make refresh    # build the containers and start them back up
make logs       # tail all logs
make db-command # enter db for direct sql commands
```

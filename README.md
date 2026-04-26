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
-- List your monsters
local res = http.get("http://YOUR_IP:8000/EXAMPLE")
local mons = textutils.unserialiseJSON(res.readAll())
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
```

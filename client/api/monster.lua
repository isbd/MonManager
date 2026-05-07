local core = require("api/core")

local function get_monsters()
    return core.get("/monster/")
end

local function get_monster(monster_id)
    return core.get("/monster/" .. monster_id)
end

return { get_monsters = get_monsters, get_monster = get_monster }
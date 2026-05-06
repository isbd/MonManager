local core = require("api/core")

local function attack(slot)
    return core.post("/battle/attack", { attack_id = slot })
end

local function catch()
    return core.post("/battle/catch")
end

local function get_moves()
    return core.post("/battle/moves")
end

return { attack = attack, catch = catch, get_moves = get_moves }
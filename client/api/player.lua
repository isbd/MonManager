local core = require("api/core")

local function register(name)
    local data = core.post_unauthed("/player/", { name = name })
    if not data then
        return nil, "Registration failed"
    end
    core.save_config({ api_key = data.api_key, player_id = data.id })
    return data
end

local function get_player()
    local config = core.load_config()
    if not config or not config.player_id then
        return nil, "No player config found"
    end
    return core.get("/player/" .. config.player_id)
end

return { register = register, get_player = get_player }
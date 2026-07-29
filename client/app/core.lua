local ui = require("app.ui")
local M = {}

local api = require("app.api.core")

local screens = {
    menu  = require("app.screens.menu"),
    party = require("app.screens.party"),
    battle = require("app.screens.battle"),
}

local state = {
    screen = "menu",
    dirty = true,
}

local ctx = {}

local function navigate(name)
    if not screens[name] then return end
    state.screen = name
    screens[name].load(state, ctx)
    state.dirty = true
end

local function dispatch(action)
    if not action then return end
    if action == "quit" then
        state.running = false
    elseif action:sub(1, 5) == "goto:" then
        navigate(action:sub(6))
    else
        local scr = screens[state.screen]
    if scr.handle then scr.handle(state, action, ctx) end
        state.dirty = true
    end
end

function ctx.setTimer(seconds, action)
  local id = os.startTimer(seconds)
  timers[id] = action
end

function ctx.queueAction(action)
  dispatch(action)
end

local function startup()
    -- TODO: wire intitial websocket connection
    -- TODO: May need to remove once shifted to actual in game (cc)
    config.set("http_enable", true)
    local player_api = require("app.api.player")

    local config_file = "config.json"
    if not fs.exists(config_file) then
        io.write("Enter your name: ")
        local name = io.read()
        local data = player_api.register(name)
        if not data then
            error("Registration failed.")
        end
        print("Registered as " .. data.name .. "!")
        os.sleep(1)
    end
    navigate("menu")
    state.running = true
end

function M.run()
    startup()

    while state.running do
        if state.dirty then
            ui.reset()
            screens[state.screen].draw(state)
            state.dirty = false
        end

        local ev, p1, p2, p3 = os.pullEvent()
        if ev == "mouse_click" then
            dispatch(ui.hitTest(p2, p3))
        elseif ev == "websocket_message" then
            -- websocket handling
        elseif ev == "timer" then
            local action = timers[p1]
            if action then
                timers[p1] = nil
                dispatch(action)
            end
        end
    end

    term.setBackgroundColor(colors.black)
    term.clear()
    term.setCursorPos(1, 1)
end

return M
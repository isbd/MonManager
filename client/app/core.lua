local ui = require("app.ui.ui")
local M = {}

local api = require("app.api.core")
local config_file = "config.json"

local screens = {
    menu  = require("app.screens.menu"),
    party = require("app.screens.party"),
    challenge = require("app.screens.challenge"),
    fish = require("app.screens.fish"),
    battle = require("app.screens.battle"),
    monmanager = require("app.screens.monmanager"),
}

local state = {
    screen = "menu",
    dirty = true,
}

local ctx = {}
ctx.timers = {}

local function navigate(name)
    if not screens[name] then return end
    state.screen = name
    screens[name].load(state, ctx)
    state.dirty = true
end

local function dispatch(action)
    if not action then return end
    local scr = screens[state.screen]

    if action == "quit" then
        state.running = false
    elseif type(action) == "string" and action:sub(1, 5) == "goto:" then
        navigate(action:sub(6))
    elseif scr and scr.handle then
        local next_action = scr.handle(state, action, ctx)
        if next_action then
            state.dirty = true
            return dispatch(next_action)
        end
    end
    state.dirty = true
end

function ctx.setTimer(seconds, action)
    local id = os.startTimer(seconds)
    ctx.timers[id] = action
end

function ctx.queueAction(action)
    dispatch(action)
end

local function startup()
    -- TODO: May need to remove once shifted to actual in game (cc)
    config.set("http_enable", true)
    local player_api = require("app.api.player")

    if not fs.exists(config_file) then
        io.write("Enter your name: ")
        local name = io.read()
        local data = player_api.register(name)
        if not data then
            error("Registration failed.")
        end
        term.write("Registered as " .. data.name .. "!")
        os.sleep(1)
    end

    local ws, ws_err = api.connect_ws()
    if ws then
        term.write("WebSocket connected.")
    else
        os.error("WebSocket failed: " .. tostring(ws_err))
    end
    os.sleep(1)
    ctx.ws = ws
    ctx.ws_opened_at = os.clock()

    navigate("menu")
    state.running = true
end

function M.run(config)
    startup()

    config_file = config

    while state.running do
        if state.dirty then
            ui.reset()
            screens[state.screen].draw(state)
            state.dirty = false
        end

        local ev, p1, p2, p3 = os.pullEvent()
        if ev == "mouse_click" then
            dispatch(ui.hitTest(p2, p3))
        elseif ev == "mouse_scroll" then
            local scr = screens[state.screen]
            if scr.onScroll then
                scr.onScroll(state, p1, p2, p3)
                state.dirty = true
            end
        elseif ev == "websocket_message" then
            -- websocket handling
            local scr = screens[state.screen]
            term.write(p1.message)
            if scr.eventHandler then
                scr.eventHandler(state, ev, p1, p3)
            end
        elseif ev == "websocket_closed" then
            os.error("WebSocket failed: ".. tostring(p3))
        elseif ev == "timer" then
            local action = ctx.timers[p1]
            if action then
                ctx.timers[p1] = nil
                dispatch(action)
            end
        elseif ev == "char" or ev == "key" then
            local scr = screens[state.screen]
            if scr.onKey then
                local action = scr.onKey(state, ev, p1, ctx)
                if action then dispatch(action) end
                state.dirty = true
            end
        end
    end

    term.setBackgroundColor(colors.black)
    term.clear()
    term.setCursorPos(1, 1)
end

return M
local ui = require("app.ui")
local M = {}

function M.load(state, ctx)
    -- load actions
end

function M.draw(state)
    term.setCursorPos(2, 1)
    term.write("== Monster Game ==")
    ui.button(2, 3, "Party", "goto:party")
    ui.button(2, 5, "Battle", "goto:battle")
    ui.button(2, 7, "Quit",  "quit")
end

function M.handle(state, action, ctx)
    -- screen-specific actions
end

return M
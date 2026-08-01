local ui = require("app.ui.ui")
local panel = require("app.ui.panel")
local encounter_api = require("app.api.encounter")
local M = {}

local list
local received_challenges = {}
local sent_challenges= {}

local function makeDummyChallenges(n)
    local names = { "ABC", "BCD", "CDE", "DFG", "FGH", "GHI", "HIJ", "IJK", "JKL", "KLM" }
    local challenges = {}
    for i = 1, n do
        table.insert(challenges, {
            challenge_id = i,
            challenger = names[((i - 1) % #names) + 1],
            challenger_id = 100 + i,
            challenged = "You",
            challenged_id = 1,
        })
    end
    return challenges
end

local function reloadChallenges()
    received_challenges = {}
    sent_challenges = {}
    local result, err = encounter_api.challenges()

    if not result then
        print("=== ERROR: ===")
        print(err or "Unknown error (nil returned)")
        return
    end
    sent_challenges = result.sent_challenges
    -- received_challenges = result.received_challenges
    received_challenges = makeDummyChallenges(400)
end

function M.load(state, ctx)
    -- load actions
    list = list or panel.newPanelList{
        x = 2, y = 3, width = 24, row_height = 3, visible_rows = 4,
        drawRow = function(ch, x, y, w)
            ui.fillRect(x, y, w, 2, colors.gray)
            term.setBackgroundColor(colors.gray)
            term.setCursorPos(x + 1, y)
            term.write(ch.challenger)
            term.setBackgroundColor(colors.black)
            ui.button(x + w - 9, y + 1, "Y", { type = "accept", challenge = ch }, colors.green)
            ui.button(x + w - 5, y + 1, "X",    { type = "reject", challenge = ch }, colors.red)
        end
    }
    reloadChallenges()
    list:setItems(received_challenges)
end

function M.draw(state)
    term.setCursorBlink(false)
    term.setCursorPos(2, 1)
    term.write("== Challenges ==")
    list:draw()
    ui.button(2, 17, "Back", "goto:menu")
end

function M.handle(state, action, ctx)

end

function M.onScroll(state, dir, x, y, ctx)
    if list and list:contains(x, y) then
        list:onScroll(dir)
    end
end

return M
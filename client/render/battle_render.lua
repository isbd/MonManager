
term.setCursorBlink(false)
local hud  = window.create(term.current(), 1, 1,  26, 1)
local mon_hud_a  = window.create(term.current(), 1, 2,  13, 1)
local mon_hud_b  = window.create(term.current(), 14, 2,  13, 1)
local mon_a = window.create(term.current(), 1, 2,  13, 16)
local mon_b = window.create(term.current(), 14, 2,  26, 16)
local bar  = window.create(term.current(), 1, 18, 26, 3)
local mod_a_box  = require("/lib.pixelbox_lite").new(mon_a)
local mod_b_box  = require("/lib.pixelbox_lite").new(mon_b)


local function fillPixelbox(mod_box, color)
    if mod_box.clear then
        mod_box:clear(color)
    else
        local w, h = mod_box:getSize()
        for y = 1, h do
            for x = 1, w do
                mod_box:setPixel(x, y, color)
            end
        end
    end
    mod_box:render()
end

local function renderTestMessage(win, message, bgColor, textColor)
    bgColor = bgColor or colors.gray
    textColor = textColor or colors.white
    message = message or "TEST"

    local w, h = win.getSize()

    hud.setVisible(false)

    win.setBackgroundColor(bgColor)
    win.setTextColor(textColor)
    win.clear()

    local x = math.max(1, math.floor((w - #message) / 2) + 1)
    local y = math.max(1, math.floor((h - 1) / 2) + 1)

    win.setCursorPos(x, y)
    win.write(message)
    hud.setVisible(true)
end

fillPixelbox(mod_a_box, colors.red)
fillPixelbox(mod_b_box, colors.blue)
renderTestMessage(hud, "HUD", colors.black, colors.lime)
renderTestMessage(mon_hud_a, "A", colors.yellow, colors.white)
renderTestMessage(mon_hud_b, "B", colors.green, colors.white)
renderTestMessage(bar, "BAR TEST", colors.gray, colors.yellow)

os.sleep(.3)
renderTestMessage(bar, "BAR TEST", colors.gray, colors.yellow)
os.sleep(.3)
renderTestMessage(bar, "BARING!", colors.orange, colors.white)
os.sleep(.3)
renderTestMessage(bar, "BAR TEST", colors.gray, colors.yellow)
os.sleep(.3)
renderTestMessage(bar, "BARING!", colors.orange, colors.white)
os.sleep(.3)
renderTestMessage(bar, "BAR TEST", colors.gray, colors.yellow)
os.sleep(.3)
renderTestMessage(bar, "BARING!", colors.orange, colors.white)
os.sleep(.3)
renderTestMessage(bar, "BAR TEST", colors.gray, colors.yellow)
os.sleep(.3)
renderTestMessage(bar, "BARING!", colors.orange, colors.white)

os.sleep(5)

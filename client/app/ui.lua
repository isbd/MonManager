local M = {}
M.buttons = {}
M.width, M.height = term.getSize()

function M.reset()
    M.buttons = {}
    term.setBackgroundColor(colors.black)
    term.clear()
end

function M.button(x, y, label, action)
    term.setCursorPos(x, y)
    term.setBackgroundColor(colors.gray)
    term.write(" " .. label .. " ")
    term.setBackgroundColor(colors.black)
    table.insert(M.buttons, {x=x, y=y, w=#label+2, action=action})
end

function M.hitTest(x, y)
    for _, b in ipairs(M.buttons) do
        if y == b.y and x >= b.x and x < b.x + b.w then
            return b.action
        end
    end
end

function M.apply_palette(pal)
    if not pal then return end
    local t = term.current()
    for digit, rgb in pairs(pal) do
        local colorConst = colors.fromBlit(digit)
        if colorConst then
            t.setPaletteColor(colorConst, rgb[1], rgb[2], rgb[3])
        end
    end
end

function M.render_image(box, image)
    local canvas = box.canvas
    for y = 1, box.height do
        local canvasRow = canvas[y]
        local imageRow  = image[y]
        for x = 1, box.width do
        local char = imageRow and imageRow[x]
        if char and char ~= " " then
            local color = colors.fromBlit(char)
            if color then
            canvasRow[x] = color
            end
        end
        end
    end
    box:render()
end

function M.fillPixelbox(mod_box, color)
    if mod_box.clear then
        mod_box:clear(color)
    else
        for y = 1, mod_box.height do
        local row = mod_box.canvas[y]
        for x = 1, mod_box.width do
            row[x] = color
        end
        end
    end
    mod_box:render()
end

function M.renderWindowMessage(win, message, bgColor, textColor)
    bgColor = bgColor or colors.gray
    textColor = textColor or colors.white
    message = message or ""

    local w, h = win.getSize()

    win.setVisible(false)

    win.setBackgroundColor(bgColor)
    win.setTextColor(textColor)
    win.clear()

    local x = math.max(1, math.floor((w - #message) / 2) + 1)
    local y = math.max(1, math.floor((h - 1) / 2) + 1)

    win.setCursorPos(x, y)
    win.write(message)
    win.setVisible(true)
end

return M
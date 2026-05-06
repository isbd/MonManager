local player_api = require("api/player")
local encounter_api = require("api/encounter")
local monster_api = require("api/monster")
local battle_api = require("api/battle")

config.set("http_enable", true)

if not fs.exists("config.json") then
    io.write("Enter your name: ")
    local name = io.read()
    local data = player_api.register(name)
    if not data then
        print("Registration failed.")
        return
    end
    print("Registered as " .. data.name .. "!")
end

local function print_value(key, value, indent)
    indent = indent or ""
    if type(value) == "table" then
        print(indent .. key .. ":")
        for k, v in pairs(value) do
            print_value(k, v, indent .. "  ")
        end
    else
        print(indent .. key .. ": " .. tostring(value))
    end
end

function get_player()
    local player = player_api.get_player()

    if not player then
        print("Failed to fetch player.")
        return
    end

    print("=== Player Info ===")
    print("ID:   " .. player.id)
    print("Name: " .. player.name)

    if player.active_encounter_id then
        print("In encounter: " .. player.active_encounter_id)
    else
        print("Not in an encounter")
    end
end

get_player()

local result = encounter_api.attempt_wild()
print(type(result))
print(result)

-- function display_result(api_func, label, ...)
--     local result = api_func(...)

--     if not result then
--         print("Failed to fetch result.")
--         return
--     end

--     print("=== " .. (label or "Result") .. " ===")
--     for key, value in pairs(result) do
--         print_value(key, value)
--     end
-- end


-- local options = {
--     { label = "Player Info",         func = player_api.get_player },
--     { label = "Wild Encounter",      func = encounter_api.attempt_wild },
--     { label = "Surrender Encounter", func = encounter_api.surrender },
--     { label = "Encounter Info",      func = encounter_api.encounter,   args = { "Encounter ID" } },
--     { label = "Catch Attempt",       func = battle_api.catch,          args = { "Monster ID" } },
--     { label = "Attack Attempt",      func = battle_api.attack,         args = { "Move ID" } },
--     { label = "Moves",               func = battle_api.moves },
-- }

-- local function prompt_args(arg_names)
--     if not arg_names then return {} end
--     local values = {}
--     for _, name in ipairs(arg_names) do
--         io.write(name .. ": ")
--         table.insert(values, io.read())
--     end
--     return values
-- end

-- while true do
--     print("\n=== Menu ===")
--     for i, option in ipairs(options) do
--         print(i .. ". " .. option.label)
--     end
--     print("0. Exit")

--     io.write("Select: ")
--     local input = tonumber(io.read())

--     if input == 0 then
--         print("Goodbye!")
--         break
--     elseif input and options[input] then
--         local selected = options[input]
--         local args = prompt_args(selected.args)
--         display_result(selected.func, selected.label, table.unpack(args))
--     else
--         print("Invalid option.")
--     end
-- end
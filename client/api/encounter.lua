local core = require("api/core")

local function attempt_wild()
    return core.post("/encounter/wild")
end

local function surrender()
    return core.post("/encounter/surrender")
end

local function encounter()
    return core.get("/encounter/")
end

return { attempt_wild = attempt_wild, surrender = surrender, encounter = encounter }
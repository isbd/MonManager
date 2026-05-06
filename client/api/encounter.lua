local core = require("api/core")

local function attempt_wild()
    return core.post("/encounter/wild", {})
end

local function surrender()
    return core.post("/encounter/surrender")
end

return { attempt_wild = attempt_wild, surrender = surrender }
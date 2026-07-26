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

local function challenges()
    return core.get("/encounter/challenges")
end

local function cancel_challenge(challenge_id)
    return core.post("/encounter/challenge/cancel", {challenge_id = challenge_id})
end

local function respond_challenge(challenge_id, accept)
    return core.post("/encounter/challenge/respond", {challenge_id = challenge_id, accept = accept})
end

local function challenge(player_id)
    return core.post("/encounter/challenge", {player_id = player_id})
end

return {
    attempt_wild = attempt_wild,
    surrender = surrender,
    encounter = encounter,
    challenges = challenges,
    cancel_challenge = cancel_challenge,
    respond_challenge = respond_challenge,
    challenge = challenge,
}
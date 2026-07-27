local API_BASE = "http://api:8000"
local config_path = "config.json"

local WS_BASE = API_BASE:gsub("^http", "ws")

local function set_config_path(path)
    config_path = path
end

local function load_config()
    if not fs.exists(config_path) then
        return nil
    end
    local f = fs.open(config_path, "r")
    local data = textutils.unserialiseJSON(f.readAll())
    f.close()
    return data
end

local function save_config(data)
    local f = fs.open(config_path, "w")
    f.write(textutils.serialiseJSON(data))
    f.close()
end

local function load_api_key()
    local config = load_config()
    if not config then return nil end
    return config.api_key
end

local function post_unauthed(path, body)
    local url = API_BASE .. path
    http.request({
        url = url,
        method = "POST",
        headers = { ["Content-Type"] = "application/json" },
        body = textutils.serialiseJSON(body)
    })

    while true do
        local event, param1, param2 = os.pullEvent()
        if event == "http_success" then
            local raw = param2.readAll()
            param2.close()
            return textutils.unserialiseJSON(raw)
        elseif event == "http_failure" then
            return nil, param2
        end
    end
end

local function request(method, path, body)
    local key = load_api_key()
    if not key then
        error("No API key found. Register first.")
    end

    local url = API_BASE .. path
    local headers = {
        ["Content-Type"] = "application/json",
        ["X-API-Key"] = key
    }

    http.request({
        url = url,
        method = method,
        headers = headers,
        body = body and textutils.serialiseJSON(body) or nil
    })

    while true do
        local event, param1, param2, param3 = os.pullEvent()
        if event == "http_success" and param1 == url then
            local status = param2.getResponseCode()
            local raw = param2.readAll()
            param2.close()
            if status < 200 or status >= 300 then
                return nil, "HTTP " .. status .. ": " .. raw
            end
            return textutils.unserialiseJSON(raw)
        elseif event == "http_failure" and param1 == url then
            local errMsg = tostring(param2)
            if param3 then
                local body = param3.readAll()
                param3.close()
                if body and body ~= "" then
                    errMsg = errMsg .. ": " .. body
                end
            end
            return nil, "Request failed: " .. errMsg
        end
    end
end

local function get(path) return request("GET", path) end
local function post(path, body) return request("POST", path, body or {}) end

local function connect_ws()
    local key = load_api_key()
    if not key then
        return nil, "No API key found. Register first."
    end
    local ws, err = http.websocket(WS_BASE .. "/websocket/ws", {
        ["X-API-Key"] = key
    })
    if not ws then
        return nil, err
    end
    return ws
end

return {
    get = get, post = post,
    post_unauthed = post_unauthed,
    save_config = save_config,
    load_config = load_config,
    connect_ws = connect_ws,
    set_config_path = set_config_path
}
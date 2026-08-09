std = "lua51"
globals = {
    "turtle", "fs", "peripheral", "redstone", "rs", "rednet",
    "http", "colors", "colours", "paintutils", "term", "textutils",
    "vector", "settings", "shell", "multishell", "parallel", "keys",
    "disk", "gps", "pocket", "commands", "config", "window",
    "printError", "read", "write", "sleep", "os",
}
allow_defined_top = true
max_line_length = 120
ignore = {"212"}  -- unused args (CC event/screen handlers)
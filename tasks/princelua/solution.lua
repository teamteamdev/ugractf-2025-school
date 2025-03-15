function hook()
  i = 1
  while true do
    name, value = debug.getlocal(2, i) -- skip getlocal() and hook()
    if not name then break end         -- out of bounds
    if value == false then
      debug.setlocal(2, i, true)
    end
    i = i + 1
  end
end

debug.sethook(hook, "r") -- set hook only on return event
castle.open()

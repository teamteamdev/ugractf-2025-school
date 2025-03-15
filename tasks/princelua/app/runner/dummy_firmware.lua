return function(is_trusted)
  local w = { is_trusted }
  return function()
    if not w[1]() then
      warn("castle.open() called in untrusted mode")
      return
    end
    print("castle opened")
  end
end

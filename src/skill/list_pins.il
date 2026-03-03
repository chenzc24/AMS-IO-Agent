
cv = geGetWindowCellView()
pins = cv~>pins
printf("Number of pins: %d\n" length(pins))
foreach(pin pins printf("%s\n" pin~>name))

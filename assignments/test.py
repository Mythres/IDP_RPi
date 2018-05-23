import ass1.ax12.ax12 as ax12

servos = ax12.Ax12()

temp = str(servos.readTemperature(id))
pos = str(servos.readPosition(id))
print("Position: " + pos + ", Temperature: " + temp)

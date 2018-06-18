import assignments.ass1.ax12.ax12 as ax12
from time import sleep

servos = ax12.Ax12()

while True:
    servos.move(1,1)
    servos.move(2,1)
    sleep(2)
    servos.move(1,1000)
    servos.move(2,1000)
    sleep(2)

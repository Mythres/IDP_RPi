import ax12.ax12 as ax12
from time import sleep

servos = ax12.Ax12()
servo_ids = servos.learnServos(1, 50, True)
print(servo_ids)

while True:
    for i in servo_ids:
        servos.move(i, 100)
        sleep(2)
        servos.move(i, 1000)
        sleep(2)

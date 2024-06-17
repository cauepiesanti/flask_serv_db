from time import sleep
import RPi.GPIO as GPIO

DIR = 6   # Direcao GPIO Pino5
STEP = 5  # Step GPIO Pino 6
CW =  0    # RotaÃ§Ã£o sentido horário
CCW = 0    # RotaÃ§Ã£o sentido anti-horário
SPR = 400  # Numero de passos por rotação completa(360 / 7.5)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, CW)

step_count = SPR
#delay = .0208
delay = .0020

for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)

sleep(.400)
#GPIO.output(DIR, CCW)
#for x in range(step_count):
#    GPIO.output(STEP, GPIO.HIGH)
#    sleep(delay)
#    GPIO.output(STEP, GPIO.LOW)
#    sleep(delay)

GPIO.cleanup


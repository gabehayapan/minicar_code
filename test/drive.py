def forward(GPIO):
    GPIO.output(16, False)
    GPIO.output(11, True)
    GPIO.output(22, False)
    GPIO.output(18, False)

def backward(GPIO):
    GPIO.output(16, True)
    GPIO.output(11, False)
    GPIO.output(22, False)
    GPIO.output(18, False)

def left_turn(GPIO):
    GPIO.output(22, True)
    GPIO.output(18, False)

def right_turn(GPIO):
    GPIO.output(22, False)
    GPIO.output(18, True)

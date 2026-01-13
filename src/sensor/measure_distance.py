def Measure(GPIO, time, trig, echo):
    dis = 0
    n = 3
    for i in range(n):
        sigoff = 0
        sigon = 0
        GPIO.output(trig, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(trig, GPIO.LOW)
        start = time.time()
        while (GPIO.input(echo) == GPIO.LOW):
            sigoff = time.time()
            if sigoff - start > 0.02:
                break
        while (GPIO.input(echo) == GPIO.HIGH):
            sigon = time.time()
            if sigon - sigoff > 0.02:
                break
        d = (sigon - sigoff) * 34000 / 2
        if d > 200:
            dis += 200 / n
        else:
            dis += d / n
    return dis

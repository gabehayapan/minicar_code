import RPi.GPIO as GPIO
import drive
import measure_distance
import time
import numpy as np

GPIO.setmode(GPIO.BOARD)

# Triger
t_list = [15, 13, 35, 32, 36]
GPIO.setup(t_list, GPIO.OUT, initial=GPIO.LOW)

# Echo
e_list = [26, 24, 37, 31, 38]
GPIO.setup(e_list, GPIO.IN)

# Motor
m_list = [22, 18, 16, 11]
GPIO.setup(m_list, GPIO.OUT)

# minimum distance
Cshort = 30
short = 50

d = np.zeros(7)

FORWARD = 1
BACKWARD = 2
LEFT_TURN = 3
RIGHT_TURN = 4

print("Press any key to start!")
input()

start_time = time.time()

try:
    while True:
        FRdis = measure_distance.Measure(GPIO, time, 15, 26)
        LHdis = measure_distance.Measure(GPIO, time, 13, 24)
        RHdis = measure_distance.Measure(GPIO, time, 32, 31)
        RLHdis = measure_distance.Measure(GPIO, time, 35, 37)
        RRHdis = measure_distance.Measure(GPIO, time, 36, 38)
        print(f"{FRdis},{LHdis},{RHdis},{RLHdis},{RRHdis}")

        if FRdis >= Cshort or LHdis > 15 or RHdis > 15:
            if LHdis <= short and RHdis >= LHdis:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
            elif LHdis > short and RHdis < LHdis:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
            elif LHdis < short and RHdis < short:
                if (LHdis - RHdis) > 10:
                    drive.forward(GPIO)
                    drive.left_turn(GPIO)
                    d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                if (RHdis - LHdis) > 10:
                    drive.forward(GPIO)
                    drive.right_turn(GPIO)
                    d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                else:
                    drive.forward(GPIO)
                    d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, FORWARD]])
            else:
                drive.forward(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, FORWARD]])
        elif time.time() - start_time < 1:
            pass
        else:
            drive.backward(GPIO)
            d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, BACKWARD]])
        time.sleep(0.05)

except KeyboardInterrupt:
    np.savetxt('./record_data.csv', d, fmt='%.3e')
    GPIO.cleanup()

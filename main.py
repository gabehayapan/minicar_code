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
short = 70

d = np.zeros(6)

print("Press any key to start!")
input()

start_time = time.time()

try:
    while True:
        FRdis = measure_distance.Measure(GPIO, time, 15, 26)
        LHdis = measure_distance.Measure(GPIO, time, 13, 24)
        RHdis = measure_distance.Measure(GPIO, time, 31, 31)
        RLHdis = measure_distance.Measure(GPIO, time, 35, 37)
        RRHdis = measure_distance.Measure(GPIO, time, 36, 38)

        if FRdis >= Cshort:
            if LHdis <= short and RHdis >= short:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
            elif LHdis > short and RHdis < short:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
            elif LHdis < short and RHdis < short:
                if (LHdis - RHdis) > 10:
                    drive.forward(GPIO)
                    drive.left_turn(GPIO)
                if (RHdis - LHdis) > 10:
                    drive.forward(GPIO)
                    drive.right_turn(GPIO)
                else:
                    drive.forward(GPIO)
                    drive.right_turn(GPIO)
            else:
                drive.forward(GPIO)
#        elif short > LHdis or short > RHdis:
#            if short > LHdis:
#                drive.Accel(PWM_PARAM, pwm, time, FORWARD_S)
#                drive.Steer(PWM_PARAM, pwm, time, RIGHT_COURSE_CORR)
#            else short > RHdis:
#                drive.Accel(PWM_PARAM, pwm, time, FORWARD_S)
#                drive.Steer(PWM_PARAM, pwm, time, LEFT_COURSE_CORR)
#        elif short > RLHdis or short > RRHdis:
#            if short > RLHdis:
#                drive.Accel(PWM_PARAM, pwm, time, FORWARD_S)
#                drive.Steer(PWM_PARAM, pwm, time, RIGHT_COURSE_CORR)
#            else short > RRHdis:
#                drive.Accel(PWM_PARAM, pwm, time, FORWARD_S)
#                drive.Steer(PWM_PARAM, pwm, time, LEFT_COURSE_CORR)
        elif time.time() - start_time < 1:
            pass
        else:
            drive.backward(GPIO)
            time.sleep(0.1)
            GPIO.cleanup()
            d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis]])
            np.savetxt('./record_data.csv', d, fmt='%.3e')
        time.sleep(0.05)

except KeyboardInterrupt:
    np.savetxt('./record_data.csv', d, fmt='%.3e')
    GPIO.cleanup()

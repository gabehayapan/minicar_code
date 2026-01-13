import RPi.GPIO as GPIO
import Adafruit_PCA9685
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

pwm = Adafruit_PCA9685.PCA9685(address=0x40)
pwm.set_pwm_freq(60)

PWM_PARAM = drive.ReadPWMPARAM(pwm)

# minimum distance
Cshort = 30
short = 70

# straight(Duty cycle) FORWARD_S = 90
# curve(Duty cycle)
FORWARD_C = 70
# back(Duty cycle)
REVERSE = -60

# Steer(Duty cycle)
LEFT = 90
RIGHT = -90

LEFT_COURSE_CORR = 50
RIGHT_COURSE_CORR = 50

d = np.zeros(6)

drive.Accel(PWM_PARAM, pwm, time, 0)
drive.Steer(PWM_PARAM, pwm, time, 0)

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
                drive.Accel(PWM_PARAM, pwm, time, FORWARD_C)
                drive.Steer(PWM_PARAM, pwm, time, RIGHT)
            elif LHdis > short and RHdis < short:
                drive.Accel(PWM_PARAM, pwm, time, FORWARD_C)
                drive.Steer(PWM_PARAM, pwm, time, LEFT)
            elif LHdis < short and RHdis < short:
                if (LHdis - RHdis) > 10:
                    drive.Accel(PWM_PARAM, pwm, time, FORWARD_S)
                    drive.Steer(PWM_PARAM, pwm, time, LEFT_COURSE_CORR)
                if (RHdis - LHdis) > 10:
                    drive.Accel(PWM_PARAM, pwm, time, FORWARD_S)
                    drive.Steer(PWM_PARAM, pwm, time, RIGHT_COURSE_CORR)
                else:
                    drive.Accel(PWM_PARAM, pwm, time, FORWARD_S)
                    drive.Steer(PWM_PARAM, pwm, time, RIGHT)
            else:
                drive.Accel(PWM_PARAM, pwm, time, FORWARD_S)
                drive.Steer(PWM_PARAM, pwm, time, 0)
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
            drive.Accel(PWM_PARAM, pwm, time, REVERSE)
            drive.Steer(PWM_PARAM, pwm, time, 0)
            time.sleep(0.1)
            drive.Accel(PWM_PARAM, pwm, time, 0)
            drive.Steer(PWM_PARAM, pwm, time, 0)
            GPIO.cleanup()
            d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis]])
            np.savetxt('./record_data.csv', d, fmt='%.3e')
        time.sleep(0.05)

except KeyboardInterrupt:
    np.savetxt('./record_data.csv', d, fmt='%.3e')
    drive.Accel(PWM_PARAM, pwm, time, 0)
    drive.Steer(PWM_PARAM, pwm, time, 0)
    GPIO.cleanup()

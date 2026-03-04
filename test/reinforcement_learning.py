import RPi.GPIO as GPIO
import drive
import measure_distance
import reinforcement
import q_table
import time
import numpy as np
import random
from collections import deque

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

ACTIONS = [FORWARD, BACKWARD, LEFT_TURN, RIGHT_TURN]

try:
    Q = q_table.load_Q("q_table.pkl")
except FileNotFoundError:
    Q = defaultdict(lambda: np.zeros(len(ACTIONS)))

alpha = 0.1
gamma = 0.9
epsilon = 0.2

prev_action = STRAIGHT

LHdis = measure_distance.Measure(GPIO, time, 13, 24)
RHdis = measure_distance.Measure(GPIO, time, 32, 31)

LH_deque = deque([LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis, LHdis])
RH_deque = deque([RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis, RHdis])

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

        avg_LHdis = sum(LH_deque) / len(LH_deque)
        avg_RHdis = sum(RH_deque) / len(RH_deque)

        if FRdis >= Cshort or LHdis > 15 or RHdis > 15:
            if LHdis <= short and RHdis >= LHdis:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("right")
                action = RIGHT_TURN
            elif LHdis > short and RHdis < LHdis:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                print("left")
                action = LEFT_TURN
            elif RRHdis < 50 and LHdis > RHdis * 0.8:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                print("left")
                action = LEFT_TURN
            elif RLHdis < 50 and LHdis < RHdis * 0.8:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("right")
                action = RIGHT_TURN
            elif RHdis < 70 and LHdis > RHdis * 0.8:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                print("left")
                action = LEFT_TURN
            elif LHdis < 70 and LHdis * 0.8 < RHdis:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("right")
                action = RIGHT_TURN
            elif LHdis < short and RHdis < short:
                if (LHdis - RHdis) > 10:
                    drive.forward(GPIO)
                    drive.left_turn(GPIO)
                    d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                    print("left")
                    action = LEFT_TURN
                if (RHdis - LHdis) > 10:
                    drive.forward(GPIO)
                    drive.right_turn(GPIO)
                    d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                    print("right")
                    action = RIGHT_TURN
                else:
                    drive.forward(GPIO)
                    d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, FORWARD]])
                    print("forward")
                    action = FORWARD_TURN
            elif RHdis > avg_RHdis * 1.1:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("right")
                action = RIGHT_TURN
            elif LHdis < avg_LHdis * 0.7:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("right")
                action = RIGHT_TURN
            elif RHdis < avg_RHdis * 0.7:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                action = left_TURN
            elif LHdis > avg_LHdis * 1.5:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                print("left")
                action = left_TURN
            else:
                drive.forward(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, FORWARD]])
                print("forward")
                action = FORWARD
        elif time.time() - start_time < 1:
            pass
        else:
            drive.backward(GPIO)
            d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, BACKWARD]])
            action = BACKWARD
        LH_deque.popleft()
        LH_deque.append(LHdis)
        RH_deque.popleft()
        RH_deque.append(RHdis)
        time.sleep(0.025)


        state = reinforcement.discretize_state(FR, LH, RH, prev_action)
        reward = calc_reward(FR, LH, RH, action, prev_action)


        FRdis = measure_distance.Measure(GPIO, time, 15, 26)
        LHdis = measure_distance.Measure(GPIO, time, 13, 24)
        RHdis = measure_distance.Measure(GPIO, time, 32, 31)
        RLHdis = measure_distance.Measure(GPIO, time, 35, 37)
        RRHdis = measure_distance.Measure(GPIO, time, 36, 38)
        print(f"{FRdis},{LHdis},{RHdis},{RLHdis},{RRHdis}")

        avg_LHdis = sum(LH_deque) / len(LH_deque)
        avg_RHdis = sum(RH_deque) / len(RH_deque)

        if FRdis >= Cshort or LHdis > 15 or RHdis > 15:
            if LHdis <= short and RHdis >= LHdis:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("right")
            elif LHdis > short and RHdis < LHdis:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                print("left")
            elif RRHdis < 50 and LHdis > RHdis * 0.8:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                print("left")
            elif RLHdis < 50 and LHdis < RHdis * 0.8:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("left")
            elif RHdis < 70 and LHdis > RHdis * 0.8:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                print("left")
            elif LHdis < 70 and LHdis * 0.8 < RHdis:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("left")
            elif LHdis < short and RHdis < short:
                if (LHdis - RHdis) > 10:
                    drive.forward(GPIO)
                    drive.left_turn(GPIO)
                    d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                    print("left")
                if (RHdis - LHdis) > 10:
                    drive.forward(GPIO)
                    drive.right_turn(GPIO)
                    d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                    print("right")
                else:
                    drive.forward(GPIO)
                    d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, FORWARD]])
                    print("forward")
            elif RHdis > avg_RHdis * 1.1:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("right")
            elif LHdis < avg_LHdis * 0.7:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
                print("right")
            elif RHdis < avg_RHdis * 0.7:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, RIGHT_TURN]])
            elif LHdis > avg_LHdis * 1.5:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, LEFT_TURN]])
                print("left")
            else:
                drive.forward(GPIO)
                d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, FORWARD]])
                print("forward")
        elif time.time() - start_time < 1:
            pass
        else:
            drive.backward(GPIO)
            d = np.vstack([d, [time.time() - start_time, FRdis, RHdis, LHdis, RRHdis, RLHdis, BACKWARD]])
        LH_deque.popleft()
        LH_deque.append(LHdis)
        RH_deque.popleft()
        RH_deque.append(RHdis)
        time.sleep(0.025)


        next_state = reinforcement.discretize_state(FR, LH, RH, action)
        Q[state][action] += alpha * (reward + gamma * np.max(Q[next_state] - Q[state][action]))

        prev_action = action

except KeyboardInterrupt:
    np.savetxt('./record_data.csv', d, fmt='%.3e')
    q_table.save_Q(Q)
    GPIO.cleanup()

from collectoins import defaultdict
import random


def discretize_state(FR, LH, RH, prev_action):
    FR_bin = min(int(FR / 10), 10)
    diff = LH - RH
    diff_bin = max(min(int(diff / 5), 5), -5)
    diff_bin += 5

    return FR_bin, diff_bin, prev_action


def select_action(state):
    if random.random() < epsilon:
        return random.choice(ACTIONS)
    return int(np.argmax(Q[state]))


def calc_reward(FR, LH, RH, action, prev_action):
    r = 0.0

    r += 1.0

    if action != prev_action:
        r -= 0.3

    r -= abs(LH - RH) * 0.05

    if FR < 20:
        r -= 5.0

    return r


def execute_action(GPIO, action):
    drive.forward(GPIO):

    if action == STRAIGHT:
        pass
    elif action == RIGHT_TURN:
        drive.right_turn(GPIO)
    elif action == LEFT_TURN:
        drive.left_turn(GPIO)

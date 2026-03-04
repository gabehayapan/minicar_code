import RPi.GPIO as GPIO
import time
import datetime
import numpy as np
import statistics
from typing import Dict, Tuple, Optional
from collections import deque

import drive
import measure_distance

SENSORS: Dict[str, Tuple[int, int]] = {
        "FR": (15, 26),
        "LH": (13, 24),
        "RLH": (35, 37),
        "RH": (32, 31),
        "RRH": (36, 38),
}


# Triger
t_list = [15, 13, 35, 32, 36]

# Echo
e_list = [26, 24, 37, 31, 38]

# Motor
m_list = [22, 18, 16, 11]

# minimum distance
Cshort = 30
short = 50

d = np.zeros(7)

FORWARD = 1
BACKWARD = 2
LEFT_TURN = 3
RIGHT_TURN = 4


class RunningStats:
    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.M2 = 0.0
        self.base_dis = 0.0
        self.is_turn = 0.0

    def update(self, x):
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.M2 += delta * delta2

    @property
    def variance(self):
        return self.M2 / (self.n - 1) if self.n > 1 else 10.0

    @property
    def std(self):
        return self.variance ** 0.5


class SimpleKalman1D:

    def __init__(self, x0: float, p0: float = 50.0, q: float = 3.0, r: float = 50.0) -> None:
        self.x = float(x0)
        self.p = float(p0)
        self.q = float(q)
        self.r = float(r)

    def update(self, his: float, z: float, r: Optional[float] = None,) -> float:
        self.p += self.q

        r_use = self.r if r is None else float(r)
        k = self.p / (self.p + r_use)
        if (his != None) and self.x >= his or self.x < 0:
            self.x = self.x + k * (float(z) - self.x)
        else:
            self.x = self.x + 0.9 * (float(z) - self.x)
        self.p = (1.0 - k) * self.p
        return self.x


KALMAN: Dict[str, SimpleKalman1D] = {}

KALMAN_PARAM = {
        "FR": dict(p0=80.0, q=6.0, r=25.0),
        "LH": dict(p0=60.0, q=3.0, r=45.0),
        "RH": dict(p0=60.0, q=3.0, r=45.0),
        "RLH": dict(p0=60.0, q=3.0, r=45.0),
        "RRH": dict(p0=60.0, q=3.0, r=45.0),
}

def sanitize_dist(x: float, fallback: float = 71.0) -> float:
    return fallback if x < 0 else x


def filter_dist(name: str, z: float, his: float) -> float:
    if name == "FR":
        return float(z)

    kf = KALMAN.get(name)
    if kf is None:
        prm = KALMAN_PARAM.get(name, {})
        kf = SimpleKalman1D(z, **prm)
        KALMAN[name] = kf

    return kf.update(his, z)


def read_sensors(his: dict) -> dict:
    d: Dict[str, float] = {}
    print("raw data")
    for name, (trig, echo) in SENSORS.items():
        z = measure_distance.Measure(GPIO, time, trig, echo)
        print(f"{name}: {z}")
        if his is None:
            z = sanitize_dist(z)
            d[name] = filter_dist(name, float(z), None)
        else:
            z = sanitize_dist(z, his[name])
            d[name] = filter_dist(name, float(z), his[name])
    print("")
    return d

def decide_action_slow(cur: dict, his: dict):
    FRdis = cur["FR"]
    LHdis = cur["LH"]
    RLHdis = cur["RLH"]
    RHdis = cur["RH"]
    RRHdis = cur["RRH"]
    if FRdis > 200 and RHdis > 80 and LHdis > 80:
        drive.slow_forward(GPIO)
        print("slow forward")
    elif RLHdis < 45 and RRHdis < 45:
        if RLHdis > RRHdis:
            drive.slow_left(GPIO)
            print("slow left")
        elif RLHdis <= RRHdis:
            drive.slow_right(GPIO)
            print("slow right")
    elif LHdis < 70 and RHdis < 70:
        if FRdis < 50:
            drive.slow_right(GPIO)
            print("slow right")
        elif LHdis > RHdis:
            drive.slow_left(GPIO)
            print("slow left")
        elif LHdis <= RHdis:
            drive.slow_right(GPIO)
            print("slow right")
    elif RLHdis < 45 and LHdis < RHdis * 0.8:
        drive.slow_right(GPIO)
        print("slow right")
    elif RRHdis < 40 and LHdis > RHdis * 0.8:
        drive.slow_left(GPIO)
        print("slow left")
        time.sleep(0.05)
    elif LHdis < 90 and LHdis * 0.8 < RHdis:
        drive.slow_right(GPIO)
        print("slow right")
    elif RHdis < 70 and LHdis > RHdis * 0.8:
        drive.slow_left(GPIO)
        print("slow left")
        time.sleep(0.05)
    elif LHdis < short and RHdis < short:
        if (LHdis - RHdis) > 10:
            drive.slow_left(GPIO)
            print("slow left")
        if (RHdis - LHdis) > 10:
            drive.slow_right(GPIO)
            print("slow right")
        else:
            drive.slow_forward(GPIO)
            print("slow forward")
    elif LHdis < his["LH"] * 0.7:
        drive.slow_right(GPIO)
        print("slow right")
    elif RHdis < his["RH"] * 0.7:
        drive.slow_left(GPIO)
        print("slow left")
    else:
        drive.slow_forward(GPIO)
        print("slow forward")

def decide_action(cur: dict, his: dict):
    FRdis = cur["FR"]
    LHdis = cur["LH"]
    RLHdis = cur["RLH"]
    RHdis = cur["RH"]
    RRHdis = cur["RRH"]
    if FRdis > 200 and RHdis > 80 and LHdis > 80:
        drive.forward(GPIO)
        print("forward")
        time.sleep(0.05)
    elif RLHdis < 45 and RRHdis < 45:
        if RLHdis > RRHdis:
            drive.forward(GPIO)
            drive.left_turn(GPIO)
            print("left")
            time.sleep(0.05)
        elif RLHdis <= RRHdis:
            drive.forward(GPIO)
            drive.right_turn(GPIO)
            print("right")
            time.sleep(0.05)
    elif LHdis < 70 and RHdis < 70:
        if FRdis < 50:
            drive.forward(GPIO)
            drive.right_turn(GPIO)
            print("right")
            time.sleep(0.05)
        elif LHdis > RHdis:
            drive.forward(GPIO)
            drive.left_turn(GPIO)
            print("left")
            time.sleep(0.05)
        elif LHdis <= RHdis:
            drive.forward(GPIO)
            drive.right_turn(GPIO)
            print("right")
            time.sleep(0.05)
    elif RLHdis < 45 and LHdis < RHdis * 0.8:
        drive.forward(GPIO)
        drive.right_turn(GPIO)
        print("right")
        time.sleep(0.05)
    elif RRHdis < 40 and LHdis > RHdis * 0.8:
        drive.forward(GPIO)
        drive.left_turn(GPIO)
        print("left")
        time.sleep(0.05)
    elif LHdis < 90 and LHdis * 0.8 < RHdis:
        drive.forward(GPIO)
        drive.right_turn(GPIO)
        print("right")
        time.sleep(0.05)
    elif RHdis < 70 and LHdis > RHdis * 0.8:
        drive.forward(GPIO)
        drive.left_turn(GPIO)
        print("left")
        time.sleep(0.05)
    elif LHdis < short and RHdis < short:
        if (LHdis - RHdis) > 10:
            drive.forward(GPIO)
            drive.left_turn(GPIO)
            print("left")
            time.sleep(0.05)
        if (RHdis - LHdis) > 10:
            drive.forward(GPIO)
            drive.right_turn(GPIO)
            print("right")
            time.sleep(0.05)
        else:
            drive.forward(GPIO)
            print("forward")
            time.sleep(0.05)
    elif LHdis < his["LH"] * 0.7:
        drive.forward(GPIO)
        drive.right_turn(GPIO)
        print("right")
        time.sleep(0.05)
    elif RHdis < his["RH"] * 0.7:
        drive.forward(GPIO)
        drive.left_turn(GPIO)
        time.sleep(0.05)
    else:
        drive.forward(GPIO)
        print("forward")
        time.sleep(0.05)

def main() -> None:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(t_list, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(e_list, GPIO.IN)
    GPIO.setup(m_list, GPIO.OUT)

    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"record_data_{run_id}.csv"
    print(f"logging to: {log_filename}")

    cur = read_sensors(None)
    print("start")
    print(f'FR:{cur["FR"]}')
    print(f'LH:{cur["LH"]}')
    print(f'RH:{cur["RH"]}')
    print(f'RLH:{cur["RLH"]}')
    print(f'RRH:{cur["RRH"]}')

    his = {}
    his["FR"] = cur["FR"]
    his["LH"] = cur["LH"]
    his["RH"] = cur["RH"]
    his["RLH"] = cur["RLH"]
    his["RRH"] = cur["RRH"]

    LH_stats = RunningStats()
    RH_stats = RunningStats()
    RRH_stats = RunningStats()
    delta_stats = RunningStats()

    is_short = False
    RH_is_short = False
    RRH_is_short = False
    LH_is_short = True

    print("Press any key to start!")
    input()

    start_time = time.time()
    drive.forward(GPIO)

    try:
        while True:
            cur = read_sensors(his)
            FRdis = cur["FR"]
            LHdis = cur["LH"]
            RHdis = cur["RH"]
            RLHdis = cur["RLH"]
            RRHdis = cur["RRH"]
            print(
                    f'FR:{cur["FR"]}'
                    f'LH:{cur["LH"]}'
                    f'RH:{cur["RH"]}'
                    f'RLH:{cur["RLH"]}'
                    f'RRH:{cur["RRH"]}'
            )

            LH_residual = LHdis - his["LH"]
            if LH_stats.is_turn == 0:
                LH_stats.update(LH_residual)

            RH_residual = RHdis - his["RH"]
            if RH_stats.is_turn == 0:
                RH_stats.update(RH_residual)

            RRH_residual = RRHdis - his["RRH"]
            if RRH_stats.is_turn == 0:
                RRH_stats.update(RRH_residual)

            delta = RHdis - LHdis
            delta_his = his["RH"] - his["LH"]
            delta_residual = delta - delta_his
            if delta_stats.is_turn == 0:
                delta_stats.update(delta_residual)

            if RH_residual > 1.7 * RH_stats.std or (RH_stats.is_turn > 0 and (cur["RH"] - RH_stats.base_dis > 1.7 * RH_stats.std)) or RH_is_short:
                RH_stats.is_turn += 1
                if RH_stats.base_dis == 0:
                    RH_stats.base_dis = his["RH"]
            else:
                RH_stats.is_turn = 0
                RH_stats.base_dis = 0.0

            if RRH_residual > 2 * RRH_stats.std or (RRH_stats.is_turn > 0 and (cur["RRH"] - RRH_stats.base_dis > 2 * RRH_stats.std)) or RRH_is_short:
                RRH_stats.is_turn += 1
                if RRH_stats.base_dis == 0:
                    RRH_stats.base_dis = his["RRH"]
            else:
                RRH_stats.is_turn = 0
                RRH_stats.base_dis = 0.0

            if (LH_residual > 2.2 * LH_stats.std or (LH_stats.is_turn > 0 and (cur["LH"] - LH_stats.base_dis > 2.2 * LH_stats.std))) and LH_is_short:
                LH_stats.is_turn += 1
                if LH_stats.base_dis == 0:
                    LH_stats.base_dis = his["LH"]
            else:
                LH_stats.is_turn = 0
                LH_stats.base_dis = 0.0
                LH_is_short = True

            if delta_residual > 1.5 * delta_stats.std or is_short:
                delta_stats.is_turn += 1
            else:
                delta_stats.is_turn = 0

            if FRdis >= Cshort and (RHdis < RRHdis) and (not RRH_is_short):
                drive.slow_left(GPIO)
                is_short = False
                RH_is_short = False
                RRH_is_short = False
                LH_is_short = True
                RH_stats.is_turn = 0
                RRH_stats.is_turn = 0
                LH_stats.is_turn = 0
                RH_stats.base_dis = 0.0
                RRH_stats.base_dis = 0.0
                LH_stats.base_dis = 0.0
                print("avoid wall slow left")
            elif FRdis >= Cshort and (LHdis < RLHdis):
                drive.slow_right(GPIO)
                is_short = False
                LH_is_short = True
                RH_is_short = False
                RRH_is_short = False
                RH_stats.is_turn = 0
                RRH_stats.is_turn = 0
                LH_stats.is_turn = 0
                RH_stats.base_dis = 0.0
                RRH_stats.base_dis = 0.0
                LH_stats.base_dis = 0.0
                print("avoid wall slow right")
            elif LHdis < 30 or RLHdis < 30:
                drive.forward(GPIO)
                drive.right_turn(GPIO)
                print("avoid left wall")
            elif RHdis < 50 or RRHdis < 30:
                drive.forward(GPIO)
                drive.left_turn(GPIO)
                print("avoid right wall")
            elif FRdis >= Cshort or LHdis > 15 or RHdis > 15:
                if RRH_stats.is_turn >= 3:
                    if RHdis > 40 and RRHdis > 25:
                        drive.forward(GPIO)
                        drive.right_turn(GPIO)
                        print("RRH short right")
                        time.sleep(0.05)
                        RRH_is_short = True
                    else:
                        drive.forward(GPIO)
                        drive.left_turn(GPIO)
                        time.sleep(0.05)
                        print("RRH short left")
                        if LHdis > 70:
                            RRH_is_short = True
                        else:
                            RRH_is_short = False
                elif RH_stats.is_turn >= 3:
                    if RHdis > 40 and RRHdis > 25:
                        drive.forward(GPIO)
                        drive.right_turn(GPIO)
                        print("RH short right")
                        time.sleep(0.05)
                        RH_is_short = True
                    else:
                        drive.forward(GPIO)
                        drive.left_turn(GPIO)
                        print("RH short left")
                        time.sleep(0.05)
                        RH_is_short = False
                elif LH_stats.is_turn >= 3:
                    if RHdis > 50 or RRHdis > 30:
                        LH_is_short = False
                        print("reset LH_is_short")
                    else:
                        drive.forward(GPIO)
                        drive.left_turn(GPIO)
                        print("LH short left")
                        time.sleep(0.05)
                elif delta_stats.is_turn >= 3:
                    if RHdis > 40 and RRHdis > 25:
                        drive.forward(GPIO)
                        drive.right_turn(GPIO)
                        print("RIGHT BRANCH")
                        time.sleep(0.05)
                        is_short = True
                    else:
                        drive.forward(GPIO)
                        drive.left_turn(GPIO)
                        print("PREPARE RIGHT")
                        time.sleep(0.05)
                        is_short = False
                else:
                    if RH_stats.is_turn == 0 and RRH_stats.is_turn == 0 and LH_stats.is_turn == 0 and delta_stats.is_turn == 0:
                        decide_action(cur, his)
                    else:
                        decide_action_slow(cur, his)
            elif time.time() - start_time < 1:
                time.sleep(0.05)
                pass
            else:
                drive.backward(GPIO)
                time.sleep(0.05)

            his["FR"] = his["FR"] + (cur["FR"] - his["FR"]) * 3/ 10
            his["LH"] = his["LH"] + (cur["LH"] - his["LH"]) * 3/ 10
            his["RLH"] = his["RLH"] + (cur["RLH"] - his["RLH"]) * 3/ 10
            his["RH"] = his["RH"] + (cur["RH"] - his["RH"]) * 3/ 10
            his["RRH"] = his["RRH"] + (cur["RRH"] - his["RRH"]) * 3/ 10


    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()

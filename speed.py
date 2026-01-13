import time

wall = [30, 0]

def go_forward(x, y):
    x = x + 1;
    return x, y

def distance_from_wall(x, y):
    return wall[0] - x, wall[1] - y

#def brake(pwm):
#    pwm = pwm * 0.7
#    set(Pin, pwm)

if __name__ == "__main__":
    x = 0
    y = 0
    pwm = 40
    while True:
        time.sleep(0.1)
        x, y = go_forward(x, y)
        print(f"current location:({x}, {y})")
        dis_x, dis_y = distance_from_wall(x, y)
        print(f"distance:({dis_x}, {dis_y})\n")
        if (dis_x <= 3):
            print("brake\n")
#            brake(pwm)
        if (x == 30):
            break

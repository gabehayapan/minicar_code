import pickle
from collections import defaultdict
import numpy as np


def load_Q(filename="q_table.pkl"):
    with open(filename, "rb") as f:
        data = pickle.load(f)

    Q = defaultdict(lambda:np.zeros(len(ACTIONS)))
    Q.update(data)
    return Q


def save_Q(Q, filename="q_table.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(dict(Q), f)

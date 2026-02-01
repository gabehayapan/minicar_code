import numpy as np


def Sigmoid(x):
    return 1 / (1 + np.exp(-x))


def Softmax(x):
    x = x - np.max(x)
    return np.exp(x) / np.sum(np.exp(x))


X = np.array([5, 100, 20, 120, 30, 30])
y = np.array([0, 1, 0, 0])

W1 = np.random.randn(6, 6) / np.sqrt(6)
B1 = np.random.randn(6) / np.sqrt(6)
Z1 = np.dot(X, W1) + B1
A1 = Sigmoid(Z1)

W2 = np.random.randn(6, 6) / np.sqrt(6)
B2 = np.random.randn(6) / np.sqrt(6)
Z2 = np.dot(A1, W2) + B2
A2 = Sigmoid(Z2)

W3 = np.random.randn(6, 4) / np.sqrt(5)
B3 = np.random.randn(6) / np.sqrt(6)
Z3 = np.dot(A2, W3) + B3
A3 = Softmax(Z3)

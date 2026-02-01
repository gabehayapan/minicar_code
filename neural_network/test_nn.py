import numpy as np


def Sigmoid(x):
    return 1 / (1 + np.exp(-x))


def Softmax(x):
    x = x - np.max(x)
    return np.exp(x) / np.sum(np.exp(x))


def cross_entropy(y, t):
    if y.ndim == 1:
        t = t.reshape(1, t.size)
        y = y.reshape(1, y.size)

    if t.size == y.size:
        t = t.argmax(axis=1)

    batch_size = y.shape[0]
    return -np.sum(np.log(y[np.arange(batch_size), t] + 1e-7)) / batch_size


X = np.array([[5, 100, 20, 120, 30, 30], [6, 100, 30, 120, 20, 10]])
t = np.array([[0, 1, 0, 0], [0, 0, 1, 0]])
lr = 0.01

for i in range(X.shape[0]):

    # === forward ===

    W1 = np.random.randn(6, 6) / np.sqrt(6)
    B1 = np.random.randn(6) / np.sqrt(6)
    Z1 = np.dot(X[i], W1) + B1
    A1 = Sigmoid(Z1)

    W2 = np.random.randn(6, 6) / np.sqrt(6)
    B2 = np.random.randn(6) / np.sqrt(6)
    Z2 = np.dot(A1, W2) + B2
    A2 = Sigmoid(Z2)

    W3 = np.random.randn(6, 4) / np.sqrt(5)
    B3 = np.random.randn(4) / np.sqrt(4)
    Z3 = np.dot(A2, W3) + B3
    y = Softmax(Z3)

    loss = cross_entropy(y, t[i])
    print(f"loss:{loss}")

    # === backward ===

    delta3 = y - t[i]

    dW3 = np.outer(A2, delta3)
    dB3 = delta3

    delta2 = np.dot(delta3, W3.T) * A2 * (1 - A2)
    dW2 = np.outer(A1, delta2)
    dB2 = delta2

    delta1 = np.dot(delta2, W2.T) * A1 * (1 - A1)
    dW1 = np.outer(X[i], delta1)
    dB1 = delta1

    W3 -= lr * dW3
    B3 -= lr * dB3

    W2 -= lr * dW2
    B2 -= lr * dB2

    W1 -= lr * dW1
    B1 -= lr * dB1

print(f"W1:{W1}")
print(f"B1:{B1}")
print(f"W2:{W2}")
print(f"B2:{B2}")
print(f"W3:{W3}")
print(f"B3:{B3}")

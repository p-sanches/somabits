import numpy as np
import matplotlib.pyplot as plt

# plt.axis([0, 10, 0, 1])

# for i in range(10):
#     y = np.random.random()
#     plt.scatter(i, y)
#     plt.pause(0.05)

# plt.show()

Fs = 125
f = 1
sample = 400
x = np.arange(sample)
y = np.sin(2 * np.pi * f * x / Fs)

for i in range(len(y)):
    plt.scatter(x[i], y[i])
    plt.pause(0.00001)
plt.show()

# plt.plot(x, y)
# plt.xlabel('sample(n)')
# plt.ylabel('voltage(V)')
# plt.show()
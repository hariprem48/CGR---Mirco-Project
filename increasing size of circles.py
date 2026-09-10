import matplotlib.pyplot as plt
import numpy as np

theta = np.linspace(0, 2*np.pi, 500)

for i in range(5):
    r = 80 + 100*i
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    plt.plot(x, y)

plt.axis("equal")
plt.grid()
plt.show()
import matplotlib.pyplot as plt
import numpy as np

# Center of flower
hc = 0
kc = 0

# Number of circles
n = 12

# Distance from center
R = 5

# Radius of each small circle
r = np.sqrt(2)

theta = np.linspace(0, 2*np.pi, 500)

for i in range(n):

    # Center of each circle
    hi = hc + R * np.cos(2*np.pi*i/n)
    ki = kc + R * np.sin(2*np.pi*i/n)

    # Circle equation
    x = hi + r * np.cos(theta)
    y = ki + r * np.sin(theta)

    plt.plot(x, y)

# Center point
plt.plot(hc, kc, 'o')

plt.axis("equal")
plt.grid()
plt.show()
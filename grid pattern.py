import matplotlib.pyplot as plt

k_values = range(-5, 6)

# Vertical lines: x = k
for k in k_values:
    plt.plot([k, k], [-5, 5], label=f"x = {k}")

# Horizontal lines: y = k
for k in k_values:
    plt.plot([-5, 5], [k, k], label=f"y = {k}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Grid Pattern")

plt.grid()
plt.xlim(-5, 5)
plt.ylim(-5, 5)

plt.show()
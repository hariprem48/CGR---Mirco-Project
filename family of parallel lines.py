import matplotlib.pyplot as plt

x = range(-10, 11)

c_values = [-8, -4, 0, 4, 8]

for c in c_values:
    y = [2*i + c for i in x]
    plt.plot(x, y, label=f"c = {c}")

plt.xlabel("x")
plt.ylabel("y")
plt.title("Family of Parallel Lines: y = 2x + c")

plt.legend()
plt.grid()
plt.show()
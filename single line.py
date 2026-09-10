import matplotlib.pyplot as plt

x = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]

y = [2*i + 1 for i in x]

plt.plot(x, y)

plt.xlabel("x")
plt.ylabel("y")
plt.title("y = 2x + 1")

plt.grid()
plt.show()
import matplotlib.pyplot as plt
import numpy as np

# Sample data for three lines
x = [1, 2, 4, 8, 16, 32, 64, 128, 256]
x = np.array(x, dtype=str)
# 5
y1 = [56.94,111.74,206.07,321.99,368.32,34.63,41.91,37.01,32.74]
# 25
y2 = [14.89,28.74,52.09,88.34,118.97,165.07,203.72,95.28,87.05]
# 100
y3 = [4,8.45,13.05,22.65,33.24,47.90,55.85,54.39,61.92]

# Plotting the lines with different colors and point shapes
plt.plot(x, y1, marker='o', color='blue', label='Delay(5ms)')  # Square markers, blue color
plt.plot(x, y2, marker='s', color='orange', label='Delay(25ms)')  # Triangle markers, orange color
plt.plot(x, y3, marker='^', color='grey', label='Delay(100ms)')  # Circle markers, grey color

# Adding labels and legend
plt.xlabel('Window Size')
plt.ylabel('Throughput (KBps)')
plt.legend()

# Displaying the plot
# plt.grid(True)
plt.grid(axis='y')
plt.plot()

plt.show()
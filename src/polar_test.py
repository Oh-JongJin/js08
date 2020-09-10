import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pi = np.pi

csv = pd.read_csv('C:/Users/user/AppData/Roaming/JetBrains/PyCharmCE2020.2/scratches/target/HANHWA Panoramic Camera.csv'
                  , names=['x', 'y', 'dis', 'ang'])
dist = csv['dis']
dist_list = dist.values.tolist()
dist_list.pop(0)

angle = csv['x']
angle_list = angle.values.tolist()
angle_list.pop(0)
N = len(dist_list)

print("angle", angle_list)
print("dist", dist_list)

# Fixing random state for reproducibility
np.random.seed(19680801)

# Compute areas and colors
colors = 2 * pi * np.random.rand(N)

fig = plt.figure("Visibility")
fig.set_facecolor('skyblue')
ax = fig.add_subplot(111, projection='polar')
ax.set_thetamin(-90)
ax.set_thetamax(90)

for i in range(N):
    angle_list[i] = round((float(angle_list[i]) * 180) / 1920, 3)
    ax.scatter((pi * angle_list[i] / 180) + (-pi/2), float(dist_list[i]), s=20, cmap='hsv', alpha=0.75)

ax.set_xticks([-pi/2, -pi/6, -pi/3, 0, pi/6, pi/3, pi/2])
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.set_xlabel("Visibility", fontsize=30)
rlab = plt.ylabel("(km)")
rlab.set_position((2, 0.2))
rlab.set_rotation(0)

fig.set_tight_layout(True)

mng = plt.get_current_fig_manager()
# mng.window.showMaximized()
plt.show()

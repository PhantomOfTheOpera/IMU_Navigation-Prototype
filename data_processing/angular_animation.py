import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import v_utils as utils

dt = 4
interval = 20

lines = utils.read_angular("angular.txt")
fig, ax = plt.subplots(subplot_kw=dict(projection="3d"))


def update(i):
    idx = i * interval // dt
    print(idx)
    x, y, z = lines[idx][:3]
    vectors = lines[idx][3:]
    coords = 3*x, 3*y, 3*z
    # coords = 0, 0, 0

    edges, points = utils.make_cube(coords, vectors)

    plt.cla()
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_zlim(-5, 5)

    faces = Poly3DCollection(edges, linewidths=0.3, edgecolors='k')
    faces.set_facecolor((0,0,1,0.1))

    ax.add_collection3d(faces)
    ax.scatter(points[:,0], points[:,1], points[:,2], s=0)


ani = animation.FuncAnimation(fig, update, frames=len(lines) * dt // interval, interval=interval)
ani.save('coil.gif', writer='imagemagick')

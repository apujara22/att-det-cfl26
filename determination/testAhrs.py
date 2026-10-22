import numpy as np
import ahrs
import datetime
from ahrs.utils import WMM

from ahrs import DCM
from ahrs.filters import TRIAD

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def main():
    print("testing")

    rng = np.random.default_rng

    theta = np.linspace(0.01, 2*np.pi-0.01, 50)

    # mag field data
    magX = 10 * np.cos(theta)
    magY = 10 * np.sin(theta)
    magZ = np.zeros(np.size(magX))

    magXmeas = np.random.normal(loc=magX, scale=1, size=np.size(magX))
    magYmeas = np.random.normal(loc=magY, scale=1, size=np.size(magY))
    magZmeas = np.random.normal(loc=magZ, scale=0.5, size=np.size(magZ))

    magMeas = np.column_stack((magXmeas, magYmeas, magZmeas))

    magTrue = np.array([1, 0, 0])

    # sun vector data
    thetaSun = theta + np.pi/2
    sunX = 10 * np.cos(thetaSun)
    sunY = 10 * np.sin(thetaSun)
    sunZ = np.zeros(np.size(sunX))

    sunXmeas = np.random.normal(loc=sunX, scale=1, size=np.size(sunX))
    sunYmeas = np.random.normal(loc=sunY, scale=1, size=np.size(sunY))
    sunZmeas = np.random.normal(loc=sunZ, scale=0.5, size=np.size(sunZ))

    sunMeas = np.column_stack((sunXmeas, sunYmeas, sunZmeas))
    
    sunTrue = np.array([0, 1, 0])

    # Modify vectors
    h = magTrue
    h = h / np.linalg.norm(h)

    s = sunTrue
    s = s / np.linalg.norm(s)

    magMeas = magMeas / np.linalg.norm(magMeas, axis=1, keepdims=True)

    sunMeas = sunMeas / np.linalg.norm(sunMeas, axis=1, keepdims=True)

    print(f"measured mag: {magMeas}")
    print(f"measured sun: {sunMeas}")

    # Perform estimation
    triad = ahrs.filters.TRIAD(w1=magMeas, w2=sunMeas, v1=h, v2=s)
    print(f"results: \n{triad.A}")


    ## Ploting

    L = 0.5  # Half-length of box along each axis

    vertices = L * np.array([
        [-1, -1, -1],
        [ 1, -1, -1],
        [ 1,  1, -1],
        [-1,  1, -1],
        [-1, -1,  1],
        [ 1, -1,  1],
        [ 1,  1,  1],
        [-1,  1,  1]
    ])

    # Pairs of vertex indices defining box edges
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    # --------------------------------------------------
    # SET UP 3D PLOT
    # --------------------------------------------------

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111, projection="3d")

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_zlim(-1, 1)

    ax.set_xlabel("Inertial X")
    ax.set_ylabel("Inertial Y")
    ax.set_zlabel("Inertial Z")
    ax.set_box_aspect([1, 1, 1])
    ax.set_title("Spacecraft Attitude Animation")

    # Draw inertial-frame vectors ONCE; they remain fixed
    ax.quiver(
        0, 0, 0,
        *magTrue,
        color="blue",
        linewidth=2,
        arrow_length_ratio=0.12,
        label="B-field vector"
    )

    ax.quiver(
        0, 0, 0,
        *sunTrue,
        color="red",
        linewidth=2,
        arrow_length_ratio=0.12,
        label="Sun Vector"
    )

    # Draw inertial coordinate axes
    ax.quiver(0, 0, 0, 1.2, 0, 0, color="gray",
            alpha=0.35, arrow_length_ratio=0.08)
    ax.quiver(0, 0, 0, 0, 1.2, 0, color="gray",
            alpha=0.35, arrow_length_ratio=0.08)
    ax.quiver(0, 0, 0, 0, 0, 1.2, color="gray",
            alpha=0.35, arrow_length_ratio=0.08)

    # Spacecraft box edges
    box_lines = []
    for edge in edges:
        line, = ax.plot([], [], [], color="black", linewidth=2)
        box_lines.append(line)

    # Optional body axes: X (orange), Y (green), Z (purple)
    axis_length = 0.8
    body_axes = [
        ax.plot([], [], [], color="orange", linewidth=2)[0],
        ax.plot([], [], [], color="green", linewidth=2)[0],
        ax.plot([], [], [], color="purple", linewidth=2)[0]
    ]

    ax.legend(loc="upper left")

    ax.view_init(elev=30, azim=45)

    # --------------------------------------------------
    # ANIMATION
    # --------------------------------------------------

    def update(i):
        C = triad.A[i].T    # transpose b/c A represents ref to body

        # Transform box vertices from body to inertial coordinates
        vertices_inertial = (C @ vertices.T).T

        # Update box edges
        for line, (start, end) in zip(box_lines, edges):
            p1 = vertices_inertial[start]
            p2 = vertices_inertial[end]

            line.set_data([p1[0], p2[0]], [p1[1], p2[1]])
            line.set_3d_properties([p1[2], p2[2]])

        # Update spacecraft body axes
        unit_axes = np.eye(3)
        colors_axes = body_axes

        for j, line in enumerate(colors_axes):
            direction = C @ unit_axes[j] * axis_length

            line.set_data([0, direction[0]], [0, direction[1]])
            line.set_3d_properties([0, direction[2]])

        ax.set_title(
            f"Spacecraft Attitude — Frame {i + 1}/{len(triad.A)}"
        )

        return box_lines + body_axes


    ani = FuncAnimation(
        fig,
        update,
        frames=len(triad.A),
        interval=750,
        blit=False
    )

    plt.tight_layout()

    ani.save("spacecraft_attitude.mp4", writer="ffmpeg", fps=5)

    #plt.close()



    # Perform estimation
    # wmm = WMM(latitude=48.137154, longitude=11.576124, height=0.519, date=datetime.date(2020, 10, 3))


if __name__ == "__main__":
    main()
import matplotlib.pyplot as plt

positions = {
    "pirate": (0.0, 0.0),
    "corsaire": (0.4, 0.1),
    "flibustier": (0.8, 0.0),
    "boucanier": (0.5, 0.4),
    "capitaine": (0.1, -0.5),
    "équipage": (0.0, -1.0),
    "moussaillon": (0.1, -1.5),

    "navire": (2.0, 1.0),
    "galion": (1.6, 1.2),
    "voile": (2.2, 1.5),
    "boussole": (2.7, 1.0),
    "océan": (2.4, 2.0),
    "tempête": (2.8, 1.8),

    "trésor": (4.0, 0.5),
    "butin": (3.7, 0.2),
    "carte": (4.3, 0.3),
    "île": (4.5, -0.2),

    "canon": (2.5, -1.5),
    "abordage": (2.8, -1.2),
    "sabre": (3.2, -1.4),
    "mutinerie": (2.7, -1.9),
}

fig, ax = plt.subplots(figsize=(10, 6))

for mot, (x, y) in positions.items():
    ax.scatter(x, y)
    ax.annotate(
        mot,
        (x, y),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=10,
    )

ax.grid(True, alpha=0.3)
ax.set_aspect("equal")

plt.tight_layout()
plt.show()

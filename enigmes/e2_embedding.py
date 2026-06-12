import matplotlib.pyplot as plt

points = {
    # Lettre I
    "trésor": (1.6, 2.35),
    "carte": (1.5, 1.8),
    "or": (1.4, 1.3),

    # Lettre A
    "navire": (4.1, 4.75),
    "boussole": (4.65, 4.05),
    "voile": (4.95, 4.85),
    "océan": (5.75, 4.85),
    "tempête": (5.25, 3.45),

    "terre": (0.3, 0.08),
    "capitaine": (1.0, 5.5),
    "équipage": (2, 4.7),
    "moussaillon": (3.2, 6.0),

    "bouteille": (3.3, 0.2),
    "verre": (4.1, 1.8),
    "stylo": (6.7, 0.2),

    "canon": (4.85, 6.8),
    "corsaire": (6, 6.95),
    "sirène": (7.2, 5.5),
    "banane": (7.2, 2.7),

    "homme": (1.5, 7.0),
    "femme": (2.2, 7.5),
    "papa": (0.3, 6.9),
    "maman": (1, 7.4),
}

fig, ax = plt.subplots(figsize=(9, 7))

ax.set_axisbelow(True)
ax.grid(True, which='major', linestyle='-', alpha=0.4)

for mot, (x, y) in points.items():
    ax.scatter(x, y, s=60, color='brown')
    ax.text(x - 0.3, y + 0.15, mot, fontsize=13)

ax.set_xlim(-0.1, 8)
ax.set_ylim(-0.1, 8)

ax.set_xticks(range(0, 9))
ax.set_yticks(range(0, 9))

ax.set_aspect('equal')

plt.tight_layout()
plt.show()
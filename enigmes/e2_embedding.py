import matplotlib.pyplot as plt

points = {
    # Lettre I
    "pomme": (1.6, 2.35),
    "banane": (1.5, 1.8),
    "poire": (1.4, 1.3),

    # Lettre A
    "navire": (4.1, 4.75),
    "boussole": (4.4, 4.1),
    "voile": (4.9, 4.65),
    "océan": (5.65, 4.55),
    "tempête": (4.8, 3.45),

    "terre": (0.4, 0.1),
    "capitaine": (1.0, 5),
    "équipage": (2, 4.2),

    "route": (3.3, 0.2),
    "verre": (4.1, 1.8),
    "stylo": (6.7, 0.2),

    "corsaire": (4.85, 6.8),
    "canon": (6, 6.95),
    "sirène": (7.2, 5.5),
    "plume": (7.2, 2.7),

    "papa": (0.3, 6.4),
    "maman": (1, 7.4),
    "homme": (1.5, 6.5),
    "femme": (2.2, 7.5),
}

fig, ax = plt.subplots(figsize=(9, 7))

ax.set_axisbelow(True)
ax.grid(True, which='major', linestyle='-', alpha=0.4)

for mot, (x, y) in points.items():
    ax.scatter(x, y, s=60, color='brown')
    ax.text(x - 0.1, y + 0.15, mot, fontsize=12)

ax.set_xlim(-0.1, 8)
ax.set_ylim(-0.1, 8)

ax.set_xticks(range(0, 9))
ax.set_yticks(range(0, 9))

ax.set_aspect('equal')

plt.tight_layout()
plt.show()
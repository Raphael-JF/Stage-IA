from random import randint

cars = ['/', '|', '\\', '—']

for i in range(50):
    for j in range(149):
        print(cars[randint(0, len(cars)-1)], end='')
    print()


import random

secret_santa_title = "Office Secret Santa 2026"


def draw(names):
    shuffled = names[:]
    random.shuffle(shuffled)
    return {giver: shuffled[(i + 1) % len(shuffled)] for i, giver in enumerate(shuffled)}

import networkx as nx
import numpy as np


class PitchMeta:
    x = 16
    y = 12


nodes = np.array([i for i in range(0, PitchMeta.x * PitchMeta.y)]).reshape(PitchMeta.y, PitchMeta.x)

for i in range(PitchMeta.y):
    for j in range(PitchMeta.x):
        print()

print(nodes)

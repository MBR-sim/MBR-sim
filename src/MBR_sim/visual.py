#IMPORTS
from tkinter import font
import util
import matplotlib.pyplot as plt 
import numpy as np; np.random.seed(0)
import seaborn as sns

# All kind of visulation

# graph based visualization
def resource_table(hw_cfg, graph):
    num_tiles = int(hw_cfg['SYSTEM']['TILES'])
    rows, cols = util.factint(num_tiles)
    cellText = np.array([[0 for i in range(0,cols)]])
    cellCycles = []
    maxLines = 0
    maxWidth = 0
    for r in range(0, rows):
        row = []
        cycles = []
        for c in range(0, cols):
            tile = r * cols + c + 1
            if (tile <= len(graph.nodes)):
                node = graph.nodes[tile - 1]
                cycles.append(node.layer_cycles)
                string = str(tile) + "\nCycles: {}".format(int(cycles[-1])) + "\n\n" + node.name.replace(";", "\n")
                maxWidth = max(maxWidth, len(max(string.split("\n"), key= lambda s: len(s))))
                maxLines = max(maxLines, len(string.split("\n")))
                if r % 2 == 1:
                    row.insert(0, string)
                else: row.append(string)
            else:
                row.append("")
                cycles.append(0)
        cellText = np.vstack([cellText, row])
        cellCycles.append(cycles)
    cellText = np.delete(cellText, 0, axis=0)
    print(maxWidth)
    print(maxLines)

    cellWidth = 1.25 * maxWidth
    cellHeight = 4 * maxLines
    sns.set(rc = {'figure.figsize':(cellWidth,cellHeight)})
    print(cellText)
    ax = sns.heatmap(cellCycles, annot=cellText, fmt="s", cbar = True,  linewidths=.5)
    plt.savefig("resource_heatmap.svg")



# Mapping visulation



# Result visulazation



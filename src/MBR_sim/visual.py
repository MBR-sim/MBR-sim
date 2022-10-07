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
    cellData = []
    maxLines = 0
    maxWidth = 0
    for r in range(0, rows):
        row = []
        data = []
        for c in range(0, cols):
            data.append(1)
            tile = r * cols + c + 1
            if (tile <= len(graph.nodes)):
                node = graph.nodes[tile - 1]
                string = str(tile) + "\n" + node.name.replace(";", "\n")
                maxWidth = max(maxWidth, len(max(string.split("\n"), key= lambda s: len(s))))
                maxLines = max(maxLines, len(string.split("\n")))
                row.append(string)
            else:
                row.append("")
        cellText = np.vstack([cellText, row])
        cellData.append(data)
    cellText = np.delete(cellText, 0, axis=0)
    print(maxWidth)
    print(maxLines)

    cellWidth = 1.25 * maxWidth
    cellHeight = 4 * maxLines
    sns.set(rc = {'figure.figsize':(cellWidth,cellHeight)})
    print(cellText)
    ax = sns.heatmap(cellData, annot=cellText, fmt="s", cbar = False,  linewidths=.5)
    plt.savefig("resource_table.svg")



# Mapping visulation



# Result visulazation



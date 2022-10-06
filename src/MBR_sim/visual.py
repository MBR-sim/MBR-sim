#IMPORTS
from tkinter import font
import util
import matplotlib.pyplot as plt 

# All kind of visulation

# graph based visualization
def resource_table(hw_cfg, graph):
    num_tiles = int(hw_cfg['SYSTEM']['TILES'])
    rows, cols = util.factint(num_tiles)
    cellText = []
    for r in range(0, rows):
        row = []
        for c in range(0, cols):
            tile = r * cols + c + 1
            if (tile <= len(graph.nodes)):
                node = graph.nodes[tile - 1]
                row.append(str(tile) + "\n" + node.name.replace(";", "\n"))
            else:
                row.append("")
        cellText.append(row)
    
    plt.rcParams["figure.figsize"] = [100.00, 100.50]
    plt.rcParams["figure.autolayout"] = True
    fig, ax = plt.subplots()
    ax.axis('tight')
    ax.set_axis_off() 
    table = ax.table( 
        cellText = cellText,  
        rowLabels = [i for i in range(0, rows)],  
        colLabels = [i for i in range(0, cols)], 
        cellLoc ='center',  
        loc ='upper left')
      
    ax.set_title('Resources Mapped', 
                fontweight ="bold")
    plt.savefig("resource_table.svg", bbox_inches='tight')



# Mapping visulation



# Result visulazation



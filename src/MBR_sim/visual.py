#IMPORTS
import MBR_sim.util as util
import matplotlib.pyplot as plt 
import numpy as np; np.random.seed(0)
import seaborn as sns
import csv

# All kind of visulation

# graph based visualization
def resource_table(hw_cfg, graph, directory):
    num_tiles = int(hw_cfg['SYSTEM']['TILES'])
    rows, cols = util.factint(num_tiles)
    cellText = np.array([[0 for i in range(0,cols)]])
    cellCycles = []
    maxLines = 0
    maxWidth = 0
    # graph.print_nodes()
    # print(util.Node.convID)
    graph.nodes.sort(key = lambda node: list(node.convID)[0])
    for r in range(0, rows):
        row = []
        cycles = []
        for c in range(0, cols):
            tile = r * cols + c + 1
            if (tile <= len(graph.nodes)):
                node = graph.nodes[tile - 1]
                names = "\n".join((node.name.replace(";", "\n").replace("__", "\n")).split("\n")[:16])
                string = str(tile) + "\nCycles: {}".format(int(node.layer_cycles)) + "\nWeight Size: {}".format(int(node.weight_size)) + "\n\n" + names + "\n CONV ID: {}".format(node.convID)
                maxWidth = max(maxWidth, len(max(string.split("\n"), key= lambda s: len(s))))
                maxLines = max(maxLines, len(string.split("\n")))
                if r % 2 == 1:
                    row.insert(0, string)
                    cycles.insert(0, node.layer_cycles)
                else: 
                    row.append(string)
                    cycles.append(node.layer_cycles)
            else:
                row.append("")
                cycles.append(0)
        cellText = np.vstack([cellText, row])
        cellCycles.append(cycles)
    cellText = np.delete(cellText, 0, axis=0)

    cellWidth = 1.3 * maxWidth
    cellHeight = 3 * maxLines
    sns.set(rc = {'figure.figsize':(cellWidth * (cols/8),cellHeight * (rows/8))})
    colormap = sns.diverging_palette(120, 10, as_cmap=True)
    ax = sns.heatmap(cellCycles, annot=cellText, fmt="s", cbar = True,  linewidths=.5, cmap = colormap)
    plt.savefig(directory + "/resrouce_heatmap.svg")
    plt.savefig(directory + "/resrouce_heatmap.png")

def csvOut(fileName, graph, directory):

    f = open(directory + "/outCSV.csv", 'w')
    writer = csv.writer(f)
    writer.writerow(["LyrName", "LyrType", "MACS", "InT(W)", "InT(H)", "InT(D)", "InT(Size))", "OutT(W)",
                     "OutT(H)", "OutT(D)", "OutT(Size)", "WgtT(W)", "WgtT(H)", "WgtT(D)", "WgtT(Num)", "WgtT(Size)", "Linear Cycles", "SIMD Cycles", "Store Cycles", "Load Cycles", "Layer Cycles", "Weight Size"])
    for node in graph.nodes:
        row = [node.name, node.op_type, node.MACS]
        row.extend(node.input_t_size)
        row.extend(node.output_t_size)
        if node.weight_t_size is not None: row.extend(node.weight_t_size)
        else: row.extend([" "," "," "," "," "])
        row.extend([int(node.linear_cycles), int(node.simd_cycles), int(node.store_cycles), int(node.load_cycles), int(node.layer_cycles), int(node.weight_size)])
        writer.writerow(row)
    f.close()



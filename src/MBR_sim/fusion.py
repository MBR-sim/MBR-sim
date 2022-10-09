#IMPORTS
import MBR_sim.util as util

#Fuses Back to Back SIMD
def fuse_simd(graph, hw_cfg):
    fused_nodes = []

    i = 0
    while len(graph.nodes) > 1:
        firstNode = graph.nodes[0]
        secondNode = graph.nodes[1]

        if (firstNode.op_type in util.linearTypes):
            fused_nodes.append(graph.nodes.pop(0))
        elif (secondNode.op_type in util.linearTypes):
            fused_nodes.append(graph.nodes.pop(0))
        else:
            fusedNode = firstNode.copy()
            fusedNode.name = firstNode.name + "+" + secondNode.name
            fusedNode.op_type = "{}+{}".format(firstNode.op_type,secondNode.op_type)
            fusedNode.simd_cycles = firstNode.simd_cycles + secondNode.simd_cycles

            fusedNode.output_t_size = secondNode.output_t_size
            fusedNode.input_t_size = firstNode.input_t_size
            fusedNode.weight_t_size = firstNode.weight_t_size
            fusedNode.calculatePerf(hw_cfg)

            graph.nodes.pop(0)
            graph.nodes.pop(0)
            graph.nodes.insert(0, fusedNode)
    fused_nodes.extend(graph.nodes)
    graph.nodes = fused_nodes
    return graph

#Inlines each MatMul and SIMD layer into a node
def inline_linear_simd(graph, hw_cfg):
    fused_nodes = []
    i = 0
    while len(graph.nodes) > 1:
        firstNode = graph.nodes[0]
        secondNode = graph.nodes[1]

        if (firstNode.op_type not in util.linearTypes):
            fused_nodes.append(graph.nodes.pop(0))
        elif (secondNode.op_type in util.linearTypes):
            fused_nodes.append(graph.nodes.pop(0))
        else:
            fusedNode = firstNode.copy()
            fusedNode.name = firstNode.name + ";" + secondNode.name
            fusedNode.op_type = "{};{}".format(firstNode.op_type,secondNode.op_type)
            fusedNode.simd_cycles = secondNode.simd_cycles
            fusedNode.MACS = firstNode.MACS

            fusedNode.output_t_size = secondNode.output_t_size
            fusedNode.input_t_size = firstNode.input_t_size
            fusedNode.weight_t_size = firstNode.weight_t_size
            fusedNode.calculatePerf(hw_cfg)

            graph.nodes.pop(0)
            graph.nodes.pop(0)
            graph.nodes.insert(0, fusedNode)
    
    fused_nodes.extend(graph.nodes)
    graph.nodes = fused_nodes
    return graph

def split_layers_weights(graph, hw_cfg):
    while len(graph.nodes) < int(hw_cfg['SYSTEM']['TILES']):
        graph.nodes.sort(key = lambda node: node.layer_cycles)
        largest_node = graph.nodes.pop(0)
        print(largest_node.layer_cycles)
        name = largest_node.name
        print(name)

        for i in range(0,2):
            split_node = largest_node.copy()
            split_node.name = name.split("_")[:-1] + "_" + str(int(name.split("_")[-1]) * 2 + i)
            split_node.weight_t_size[3] //= 2
            split_node.calculatePerf(hw_cfg)
            graph.nodes.append(split_node)

'''
1. Look at smallest layer, look at before and after. 
    ex: 50 is smallest, fuse with 49 or 51?
    Recursive

Iterate through each node, starting with smalllest
'''
def spread_layers(graph, hw_cfg):
    print("HERE")
    while len(graph.nodes) < int(hw_cfg['SYSTEM']['TILES']):
        graph.nodes.sort(key = lambda node: node.layer_cycles, reverse=True)
        largest_node = graph.nodes.pop(0)
        name = largest_node.name

        for i in range(0,2):
            split_node = largest_node.copy()
            if (split_node.name[-3:-1] == "__"): split_node.name = name + str(i)
            else: split_node.name = name + "__{}".format(i)
            split_node.weight_t_size[3] //= 2
            split_node.MACS //= 2
            split_node.simd_cycles //= 2
            split_node.calculatePerf(hw_cfg)
            print(largest_node.layer_cycles)
            print(split_node.layer_cycles)
            print()
            graph.nodes.append(split_node)

def combimne_multiple_layers(graph, hw_cfg):
    while (len(graph.nodes) > int(hw_cfg['SYSTEM']['TILES'])):
        graph.nodes.sort(key=lambda node: node.stage_cycles)
        smallest_node_0 = graph.nodes.pop(-1)            
        smallest_node_1 = graph.nodes.pop(-2)
        combined_node = smallest_node_0.copy()
        combined_node.tile = 1
        combined_node.output_t_size = smallest_node_1.output_t_size
        combined_node.stage_cycles = smallest_node_0.stage_cycles + smallest_node_1.stage_cycles
        graph.nodes.append(combined_node)

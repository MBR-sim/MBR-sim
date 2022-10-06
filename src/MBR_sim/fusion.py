#IMPORTS
import MBR_sim.util as util


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
            fusedNode = util.Node(firstNode.name + "+" + secondNode.name)
            fusedNode.op_type = "{}+{}".format(firstNode.op_type,secondNode.op_type)
            fusedNode.simd_cycles = firstNode.simd_cycles + secondNode.simd_cycles

            fusedNode.output_t_size = secondNode.output_t_size
            fusedNode.input_t_size = firstNode.input_t_size
            fusedNode.weight_t_size = firstNode.weight_t_size
            
            graph.nodes.pop(0)
            graph.nodes.pop(0)
            graph.nodes.insert(0, fusedNode)
    fused_nodes.extend(graph.nodes)
    graph.nodes = fused_nodes
    return graph

def inline_linear_simd(graph):
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
            fusedNode = util.Node(firstNode.name + ";" + secondNode.name)
            fusedNode.op_type = "{};{}".format(firstNode.op_type,secondNode.op_type)
            fusedNode.simd_cycles = secondNode.simd_cycles
            fusedNode.MACS = firstNode.MACS

            fusedNode.output_t_size = secondNode.output_t_size
            fusedNode.input_t_size = firstNode.input_t_size
            fusedNode.weight_t_size = firstNode.weight_t_size

            graph.nodes.pop(0)
            graph.nodes.pop(0)
            graph.nodes.insert(0, fusedNode)
    
    fused_nodes.extend(graph.nodes)
    graph.nodes = fused_nodes
    return graph


def split_layers(graph, hw_cfg):
    if (len(graph.nodes) < int(hw_cfg['SYSTEM']['TILES'])):
        while len(graph.nodes) != int(hw_cfg['SYSTEM']['TILES']):
            graph.nodes.sort(key = lambda node: node.stage_cycles)
            largest_node = graph.nodes[0]
            largest_node_0 = largest_node.copy()
            largest_node_1 = largest_node.copy()
            largest_node_0.name = largest_node_0.name.split("_")[0] + "_".join(largest_node_0.name.split("_")[1:]) + "_0"
            largest_node_1.name = largest_node_1.name.split("_")[0] + "_".join(largest_node_1.name.split("_")[1:]) + "_1"
            
            largest_node_0.stage_cycles //= 2

'''
1. Look at smallest layer, look at before and after. 
    ex: 50 is smallest, fuse with 49 or 51?
    Recursive
'''
def fuse_multiple_layers(graph, hw_cfg):
    while (len(graph.nodes) > int(hw_cfg['SYSTEM']['TILES'])):
        graph.nodes.sort(key=lambda node: node.stage_cycles)
        smallest_node_0 = graph.nodes.pop(-1)            
        smallest_node_1 = graph.nodes.pop(-2)
        combined_node = smallest_node_0.copy()
        combined_node.tile = 1
        combined_node.output_t_size = smallest_node_1.output_t_size
        combined_node.stage_cycles = smallest_node_0.stage_cycles + smallest_node_1.stage_cycles
        graph.nodes.append(combined_node)

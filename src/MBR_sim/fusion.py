#IMPORTS
import MBR_sim.util


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

def fuse_linear(graph):
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






            
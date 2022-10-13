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
            fusedNode.simd_cycles = firstNode.simd_cycles + secondNode.simd_cycles
            fusedNode.MACS = firstNode.MACS + secondNode.MACS

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
            split_node.weight_t_size[3] //= 2 #Divde Input and Output tensors
            split_node.MACS //= 2
            split_node.simd_cycles //= 2
            split_node.calculatePerf(hw_cfg)
            print(largest_node.layer_cycles)
            print(split_node.layer_cycles)
            print()
            graph.nodes.append(split_node)

def combine_multiple_layers(graph, hw_cfg):
    while (len(graph.nodes) > int(hw_cfg['SYSTEM']['TILES'])):
        graph.nodes.sort(key=lambda node: -node.layer_cycles)
        smallestNode = graph.nodes.pop(-1)
        print(smallestNode.layer_cycles)
        #Finding node with convolution ID 1 above and 1 below
        beforeNode = next((node for node in graph.nodes if (smallestNode.convID[0] - 1) in node.convID), None)
        afterNode = next((node for node in graph.nodes if (smallestNode.convID[0] + 1) in node.convID), None)
        print(graph.nodes)
        if beforeNode is not None and afterNode is not None:
            pairedNode = beforeNode if beforeNode.layer_cycles < afterNode.layer_cycles else afterNode
        elif beforeNode is not None and afterNode is None:
            pairedNode = beforeNode
        elif beforeNode is None and afterNode is not None:
            pairedNode = afterNode
        else:
            raise Exception("Can not combine only 1 layer!")
        graph.nodes.remove(pairedNode)

        combinedNode = smallestNode.copy()
        combinedNode.name += ";" + pairedNode.name
        combinedNode.op_type = "{};{}".format(smallestNode.op_type,pairedNode.op_type)
        combinedNode.output_t_size = pairedNode.output_t_size
        combinedNode.outDatatype = pairedNode.outDatatype
        combinedNode.simd_cycles += pairedNode.simd_cycles
        combinedNode.MACS += pairedNode.MACS
        combinedNode.convID.extend(pairedNode.convID)
        
        combinedNode.calculatePerf(hw_cfg)
        graph.nodes.append(combinedNode)

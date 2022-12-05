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
            fusedNode.weight_size += secondNode.weight_size
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
            fusedNode.weight_size += secondNode.weight_size
            fusedNode.calculatePerf(hw_cfg)

            graph.nodes.pop(0)
            graph.nodes.pop(0)
            graph.nodes.insert(0, fusedNode)
    
    fused_nodes.extend(graph.nodes)
    graph.nodes = fused_nodes
    return graph

def split_repeats(graph, hw_cfg):
    splitNodes = []
    for node in graph.nodes:
        for i in range(node.repeats):
            splitNode = node.copy()
            splitNode.name += "_" + str(i)
            splitNode.repeats = 1
            splitNode.calculatePerf(hw_cfg)
            splitNodes.append(splitNode)
    graph.nodes = splitNodes

def spread_layers_capped(graph, hw_cfg):
    while len(graph.nodes) < int(hw_cfg['SYSTEM']['TILES']):
        graph.nodes.sort(key = lambda node: node.layer_cycles, reverse=True)
        largest_node = graph.nodes.pop(0)
        name = largest_node.name

        for i in range(0,2):
            split_node = largest_node.copy()
            if (split_node.name[-3:-1] == "__"): split_node.name = name + str(i)
            else: split_node.name = name + "__{}".format(i)
            split_node.weight_t_size[3] //= 2 #Divde Input and Output tensors
            split_node.output_t_size = [dimension//2 for dimension in split_node.output_t_size]
            split_node.input_t_size = [dimension//2 for dimension in split_node.input_t_size]
            split_node.weight_size //= 2
            split_node.MACS //= 2
            split_node.simd_cycles //= 2
            split_node.calculatePerf(hw_cfg)
            graph.nodes.append(split_node)

def spread_layers_threshold(graph, hw_cfg, threshold):
    avgCycles = sum([node.layer_cycles for node in graph.nodes])/len(graph.nodes)
    graph.nodes.sort(key = lambda node: node.layer_cycles, reverse=True)
    while graph.nodes[0].layer_cycles > avgCycles * threshold:
        graph.nodes.sort(key = lambda node: node.layer_cycles, reverse=True)
        largest_node = graph.nodes.pop(0)
        # largest_node.print_node()
        name = largest_node.name
        for i in range(0,2):
            split_node = largest_node.copy()
            if (split_node.name[-3:-1] == "__"): split_node.name = name + str(i)
            else: split_node.name = name + "__{}".format(i)
            split_node.weight_t_size[3] //= 2 #Divde Input and Output tensors
            split_node.output_t_size = [dimension//2 for dimension in split_node.output_t_size]
            split_node.input_t_size = [dimension//2 for dimension in split_node.input_t_size]
            split_node.weight_size //= 2
            split_node.MACS //= 2
            split_node.simd_cycles //= 2
            split_node.calculatePerf(hw_cfg)
            graph.nodes.append(split_node)
        avgCycles = sum([node.layer_cycles for node in graph.nodes])/len(graph.nodes)
        graph.nodes.sort(key = lambda node: node.layer_cycles, reverse=True)

def combine_multiple_layers_capped(graph, hw_cfg):
    graph.nodes.sort(key=lambda node: -node.layer_cycles)
    if hw_cfg['SYSTEM']['ENABLE_WEIGHT_SPLITTING'] == "1":
        maxWgtCapacity = int(hw_cfg['SYSTEM']['MAX_WEIGHT_CAPACITY'])
    else:
        maxWgtCapacity = 2 ** 40
    excludedNodes = []
    while (len(graph.nodes) + (len(excludedNodes)) > int(hw_cfg['SYSTEM']['TILES'])):
        if (len(graph.nodes) == 0):
            print("Can not fit within tiles!")
            raise(Exception())
            break
        smallestNode = graph.nodes.pop(-1)
        #Finding node with convolution ID 1 above and 1 below
        possiblePairedNodes = []
        possiblePairedNodes.extend([node for node in graph.nodes if any([(convID + 1) in node.convID for convID in smallestNode.convID])])
        possiblePairedNodes.extend([node for node in graph.nodes if any([(convID - 1) in node.convID for convID in smallestNode.convID])])
        possiblePairedNodes.extend([node for node in graph.nodes if any([(convID) in node.convID for convID in smallestNode.convID])])
        possiblePairedNodes.sort(key = lambda node: node.layer_cycles)
        while (len(possiblePairedNodes) > 0) and (possiblePairedNodes[0].weight_size + smallestNode.weight_size > maxWgtCapacity):
            possiblePairedNodes.pop(0)
        if len(possiblePairedNodes) > 0:
            pairedNode = possiblePairedNodes[0]
        else:
            excludedNodes.append(smallestNode)
            continue
        graph.nodes.remove(pairedNode)

        combinedNode = smallestNode.copy()
        combinedNode.name += ";" + pairedNode.name
        combinedNode.op_type = "{};{}".format(smallestNode.op_type,pairedNode.op_type)
        if (list(smallestNode.convID)[0] - 1) in pairedNode.convID: #pariedNode is before smallestNode
            combinedNode.output_t_size = pairedNode.output_t_size
            combinedNode.outDatatype = pairedNode.outDatatype
        elif (list(smallestNode.convID)[0] + 1) in pairedNode.convID: #pariedNode is before afterNode
            combinedNode.input_t_size = pairedNode.input_t_size
            combinedNode.inDatatype = pairedNode.inDatatype
        combinedNode.simd_cycles += pairedNode.simd_cycles
        combinedNode.MACS += pairedNode.MACS
        combinedNode.weight_size += pairedNode.weight_size
        combinedNode.convID = combinedNode.convID.union(pairedNode.convID)
        
        combinedNode.calculatePerf(hw_cfg)
        graph.nodes.append(combinedNode)
        graph.nodes.sort(key = lambda node: -node.layer_cycles)
    graph.nodes.extend(excludedNodes)
    graph.nodes.sort(key = lambda node: -node.layer_cycles)

def combine_multiple_layers_threshold(graph, hw_cfg, threshold):
    avgCycles = sum([node.layer_cycles for node in graph.nodes])/len(graph.nodes)
    graph.nodes.sort(key = lambda node: node.layer_cycles)
    if hw_cfg['SYSTEM']['ENABLE_WEIGHT_SPLITTING'] == "1":
        maxWgtCapacity = int(hw_cfg['SYSTEM']['MAX_WEIGHT_CAPACITY'])
    else:
        maxWgtCapacity = 2 ** 40
    excludedNodes = []
    while graph.nodes[0].layer_cycles < avgCycles * threshold:
        graph.nodes.sort(key=lambda node: node.layer_cycles)
        smallestNode = graph.nodes.pop(0)
        #Finding node with convolution ID 1 above and 1 below
        possiblePairedNodes = []
        possiblePairedNodes.extend([node for node in graph.nodes if any([(convID + 1) in node.convID for convID in smallestNode.convID])])
        possiblePairedNodes.extend([node for node in graph.nodes if any([(convID - 1) in node.convID for convID in smallestNode.convID])])
        possiblePairedNodes.extend([node for node in graph.nodes if any([(convID) in node.convID for convID in smallestNode.convID])])
        possiblePairedNodes.sort(key = lambda node: node.layer_cycles)
        while (len(possiblePairedNodes) > 0) and (possiblePairedNodes[0].weight_size + smallestNode.weight_size > maxWgtCapacity):
            possiblePairedNodes.pop(0)
        if len(possiblePairedNodes) > 0:
            pairedNode = possiblePairedNodes[0]
        else:
            excludedNodes.append(smallestNode)
            continue

        graph.nodes.remove(pairedNode)
        combinedNode = smallestNode.copy()
        combinedNode.name += ";" + pairedNode.name
        combinedNode.op_type = "{};{}".format(smallestNode.op_type,pairedNode.op_type)
        if (list(smallestNode.convID)[0] - 1) in pairedNode.convID: #pariedNode is before smallestNode
            combinedNode.output_t_size = pairedNode.output_t_size
            combinedNode.outDatatype = pairedNode.outDatatype
        elif (list(smallestNode.convID)[0] + 1) in pairedNode.convID: #pariedNode is before afterNode
            combinedNode.input_t_size = pairedNode.input_t_size
            combinedNode.inDatatype = pairedNode.inDatatype
        combinedNode.simd_cycles += pairedNode.simd_cycles
        combinedNode.MACS += pairedNode.MACS
        combinedNode.weight_size += pairedNode.weight_size
        combinedNode.convID = combinedNode.convID.union(pairedNode.convID)
        
        combinedNode.calculatePerf(hw_cfg)
        graph.nodes.append(combinedNode)
        avgCycles = sum([node.layer_cycles for node in graph.nodes])/len(graph.nodes)
        graph.nodes.sort(key = lambda node: -node.layer_cycles)
    graph.nodes.extend(excludedNodes)
    graph.nodes.sort(key = lambda node: -node.layer_cycles)

def two_pair_min(graph, hw_cfg):
    if hw_cfg['SYSTEM']['ENABLE_WEIGHT_SPLITTING'] == "1":
        maxWgtCapacity = int(hw_cfg['SYSTEM']['MAX_WEIGHT_CAPACITY'])
    else:
        maxWgtCapacity = 2 ** 40
    excludedNodes = []
    while len(graph.nodes) > 0:
        maxLayerCycles = max([node.layer_cycles for node in graph.nodes])
        graph.nodes.sort(key = lambda node: node.layer_cycles)
        smallestNode = graph.nodes.pop(0)
        #Finding node with convolution ID 1 above and 1 below
        possiblePairedNodes = []
        possiblePairedNodes.extend([node for node in graph.nodes if any([(convID + 1) in node.convID for convID in smallestNode.convID])])
        possiblePairedNodes.extend([node for node in graph.nodes if any([(convID - 1) in node.convID for convID in smallestNode.convID])])
        possiblePairedNodes.extend([node for node in graph.nodes if any([(convID) in node.convID for convID in smallestNode.convID])])
        possiblePairedNodes.sort(key = lambda node: node.layer_cycles)
        while (len(possiblePairedNodes) != 0) and possiblePairedNodes[0].weight_size + smallestNode.weight_size > maxWgtCapacity:
            possiblePairedNodes.pop(0)
        if len(possiblePairedNodes) > 0:
            pairedNode = possiblePairedNodes[0]
        else:        
            excludedNodes.append(smallestNode)
            continue
        
        if pairedNode.layer_cycles + smallestNode.layer_cycles + 1 >= maxLayerCycles:
            excludedNodes.append(smallestNode)
            continue
        
        #Combining Smallest Nodes
        graph.nodes.remove(pairedNode)
        combinedNode = smallestNode.copy()
        combinedNode.name += ";" + pairedNode.name
        combinedNode.op_type = "{};{}".format(smallestNode.op_type,pairedNode.op_type)
        if (list(smallestNode.convID)[0] - 1) in pairedNode.convID: #pariedNode is before smallestNode
            combinedNode.output_t_size = pairedNode.output_t_size
            combinedNode.outDatatype = pairedNode.outDatatype
        elif (list(smallestNode.convID)[0] + 1) in pairedNode.convID: #pariedNode is before afterNode
            combinedNode.input_t_size = pairedNode.input_t_size
            combinedNode.inDatatype = pairedNode.inDatatype
        combinedNode.simd_cycles += pairedNode.simd_cycles
        combinedNode.MACS += pairedNode.MACS
        combinedNode.weight_size += pairedNode.weight_size
        combinedNode.convID = combinedNode.convID.union(pairedNode.convID)
        combinedNode.calculatePerf(hw_cfg)
        graph.nodes.append(combinedNode)

        #Splitting Largest Node
        graph.nodes.sort(key = lambda node: node.layer_cycles, reverse=True)
        largest_node = graph.nodes.pop(0)
        name = largest_node.name
        for i in range(0,2):
            split_node = largest_node.copy()
            if (split_node.name[-3:-1] == "__"): split_node.name = name + str(i)
            else: split_node.name = name + "__{}".format(i)
            split_node.weight_t_size[-1] //= 2 #Divde Input and Output tensors
            split_node.output_t_size[-1] //= 2
            split_node.input_t_size[-1] //= 2
            split_node.weight_size //=2
            split_node.MACS //= 2
            split_node.simd_cycles //= 2
            split_node.calculatePerf(hw_cfg)
            graph.nodes.append(split_node)
        maxLayerCycles = max([node.layer_cycles for node in graph.nodes])
        

    graph.nodes.extend(excludedNodes)
    graph.nodes.sort(key = lambda node: -node.layer_cycles)
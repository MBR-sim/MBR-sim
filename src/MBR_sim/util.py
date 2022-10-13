#IMPORTS
import math 
import MBR_sim.simulate as simulate
import MBR_sim.util as util
# Node and Graph Class

linearTypes = ["Convolution"]

class Node ():
    uidCounter = 0
    convID = 0

    def __init__(self, name):
        self.name = name
        self.uid = Node.uidCounter
        Node.uidCounter += 1
        self.convID = []
        self.op_type = None
        self.data_type = None
        self.tiles = None
        self.tile = None
    
        self.inDatatype = ""
        self.outDatatype = ""
        self.wgtDatatype = ""

        self.input_t_size = None #(W, H, D, Size)
        self.output_t_size = None #(W, H, D, Size)
        self.weight_t_size = None #(W, H, D, N, Size)
        self.ops_cnt = None
        
        self.compute_cycles = 0
        self.load_cycles = 0
        self.store_cycles = 0
        self.simd_cycles = 0
        self.linear_cycles = 0
        self.layer_cycles = 0
        self.stage_cycles = 0
        self.MACS = 0
        
        self.input_deps = None
        self.output_deps = None

    def calculatePerf(self, hw_cfg):
        self.convID.sort()
        #Calculates Volumes
        self.input_t_size = self.input_t_size[:3] + [math.prod(self.input_t_size[:3])]
        self.output_t_size = self.output_t_size[:3] + [math.prod(self.output_t_size[:3])]
        if self.weight_t_size is not None:
            self.weight_t_size = self.weight_t_size[:4] + [math.prod(self.weight_t_size[:4])]

        self.load_cycles = self.input_t_size[3]//int(hw_cfg['TILE']['NOC_BW'])
        self.store_cycles = self.output_t_size[3]//int(hw_cfg['TILE']['NOC_BW'])
        if any([linType in self.op_type for linType in util.linearTypes]):
            self.linear_cycles = (self.MACS//int(hw_cfg['TILE']['MAC_BW']))/simulate.mac_util(self, hw_cfg)
        else:
            self.linear_cycles = 0
        self.layer_cycles = max(self.load_cycles, self.simd_cycles, self.linear_cycles, self.store_cycles)
        self.tiles = 1
        self.stage_cycles = self.layer_cycles//self.tiles

    def __repr__(self):
        return "{}; {}".format(self.name, self.convID[0])

    # Method
    def print_node(self):
        print("Name: {}, UID: {}, CONVID: {}".format(self.name, self.uid, self.convID[0]))
        print("Input Tensor:" + str(self.input_t_size))
        print("Ouput Tensor: " + str(self.output_t_size))
        print("Weight Tensor:" + str(self.weight_t_size))
        if self.simd_cycles:
            print("SIMD Cycles: {}".format(self.simd_cycles))
        if self.MACS:
            print("MACS: {}".format(self.MACS))
    
    def copy(self):
        newNode = Node(self.name)
        newNode.convID = self.convID
        newNode.op_type = self.op_type
        newNode.data_type = self.data_type
        newNode.tiles = self.tiles
        newNode.tile = self.tile
        
        newNode.inDatatype = self.inDatatype
        newNode.outDatatype = self.outDatatype
        newNode.wgtDatatype = self.wgtDatatype
    
        newNode.input_t_size = self.input_t_size #(W, H, D, Size)
        newNode.output_t_size = self.output_t_size #(W, H, D, Size)
        newNode.weight_t_size = self.weight_t_size #(W, H, D, N, Size)
        newNode.ops_cnt = self.ops_cnt
        
        newNode.compute_cycles = self.compute_cycles
        newNode.load_cycles = self.load_cycles
        newNode.store_cycles = self.store_cycles
        newNode.simd_cycles = self.simd_cycles
        newNode.linear_cycles = self.linear_cycles
        newNode.layer_cycles = self.layer_cycles
        newNode.stage_cycles = self.stage_cycles
        newNode.MACS = self.MACS
        
        newNode.input_deps = self.input_deps
        newNode.output_deps = self.output_deps
        return newNode

class Graph():
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.globalInDatatype = ""
        self.globalOutDatatype = ""
        self.globalWgtDatatype = ""

    def add_node(self, node):
        self.nodes.append(node)
        self.nodes.sort(key = lambda node: node.uid)
    
    def remove_node(self, node_removed):
        i = 0
        while i < len(self.nodes):
            node = self.nodes[i]
            if node.uid == node_removed.uid:
                self.nodes.pop(i)
                return
        raise Exception("Node does not exist.")

    def print_nodes(self):
        for node in self.nodes:
            node.print_node()
            print()
  
def tileToPos(hw_cfg, tile):
    print(tile)
    tile -= 1
    num_tiles = int(hw_cfg['SYSTEM']['TILES'])
    rows, cols = factint(num_tiles)
    print(rows, cols)
    row = tile//cols
    col = tile%rows if row %2 == 0 else (cols - tile%rows - 1)
    print(row, col)
    print()
    return int(row),int(col)

def factint(n):
    pos_n = abs(n)
    max_candidate = int(math.sqrt(pos_n))
    for candidate in range(max_candidate, 0, -1):
        if pos_n % candidate == 0:
            break
    return candidate, n //candidate


#Helper function for mapper.split_by_weight
def split(a, n):
    k, m = divmod(a, n)
    vals = [k + 1 for i in range(m)]
    vals.extend([k for i in range(n-m)])
    return vals




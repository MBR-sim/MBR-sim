#IMPORTS
import math 
# Node and Graph Class

linearTypes = ["Convolution"]

class Node ():
    uidCounter = 0

    def __init__(self, name):
        self.name = name
        self.uid = Node.uidCounter
        Node.uidCounter += 1
        self.op_type = None
        self.data_type = None
        self.tiles = None
        self.tile = None
    
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
        self.MACS = 0
        
        self.input_deps = None
        self.output_deps = None

    # Method
    def print_node(self):
        print("Name: {}, UID: {}".format(self.name, self.uid))
        print("Input Tensor:" + str(self.input_t_size))
        print("Ouput Tensor: " + str(self.output_t_size))
        print("Weight Tensor:" + str(self.weight_t_size))
        if self.simd_cycles:
            print("SIMD Cycles: {}".format(self.simd_cycles))
        if self.MACS:
            print("MACS: {}".format(self.MACS))

class Graph():
    def __init__(self, name):
        self.name = name
        self.nodes = []

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




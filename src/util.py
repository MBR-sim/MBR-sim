# Node and Graph Class

class Node ():
    name:
    uid: 
    op_type:
    data_type:
   
    input_t_size:
    output_t_size:
    ops_cnt:
    
    compute_cycles:
    load_cycles:
    store_cycles:
    simd_cycles:
    layer_cycles:
    
    input_deps:
    output_deps:

    # Method
    print_node()

class Graph():
    name:
    nodes[]:

    # Method
    add_node()
    remove_node()
    print_nodes()  
  





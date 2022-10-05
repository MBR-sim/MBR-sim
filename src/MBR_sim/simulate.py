#IMPORTS
import MBR_sim.util
import math
# Main simulation file

# Compute all kind of cycles
def calculateSIMDCycles(graph, hw_cfg):
    for node in graph.nodes:
        if (node.op_type not in util.linearTypes):
            op_type = node.op_type.upper()
            OutT = node.output_t_size[-1]
            if op_type in hw_cfg['SIMD_PERF']:
                node.simd_cycles = OutT//int(hw_cfg['SIMD_PERF'][op_type])
            else:
                raise Exception("SIMD OP: {} NOT SUPPORTED".format(op_type))

def calculateMACS(graph, hw_cfg):
    for node in graph.nodes:
        if (node.op_type in util.linearTypes):
            node.MACS = int(node.output_t_size[3] * node.weight_t_size[4]/node.weight_t_size[3])

def mac_util(node):
    wgtWidth = node.weight_t_size[0]
    wgtHeight = node.weight_t_size[1]
    if (wgtHeight == wgtWidth):
        if (wgtHeight == 1): return 0.9
        if (wgtHeight == 3): return 1
        if (wgtHeight == 7): return 0.5
    raise Exception("MAC NOT SUPPORTED: {} x {}".format(wgtWidth, wgtHeight))


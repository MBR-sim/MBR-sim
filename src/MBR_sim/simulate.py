#IMPORTS
import MBR_sim.util as util
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
                raise Exception("SIMD OP: {} NOT SUPPORTED".format(op_type)) #Don't Break, print warning and add defaults

def calculateMACS(graph, hw_cfg):
    for node in graph.nodes:
        if (node.op_type in util.linearTypes):
            #For Convolution Layers, Total MAC is Weight Volume * Output Volume
            #For MatMul Layers, Total MAC is Ouput Volume * Weight Width
            node.MACS = int(math.prod(node.output_t_size[:2]) * node.weight_t_size[4])


def mac_util(node, hw_cfg):
    #TODO: For different convolutions, should be in Config File.

    wgtWidth = node.weight_t_size[0]
    wgtHeight = node.weight_t_size[1]
    if (wgtHeight == wgtWidth):
        if (wgtHeight == 1): return float(hw_cfg['MAC_UTIL']['KER_1'])
        elif (wgtHeight == 3): return float(hw_cfg['MAC_UTIL']['KER_3'])
        elif (wgtHeight == 5): return float(hw_cfg['MAC_UTIL']['KER_5'])
        elif (wgtHeight == 7): return float(hw_cfg['MAC_UTIL']['KER_7'])
    raise Exception("MAC NOT SUPPORTED: {} x {}".format(wgtWidth, wgtHeight)) #Don't Break, print warning and add defaults



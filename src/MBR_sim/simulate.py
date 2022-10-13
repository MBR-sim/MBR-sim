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
            if op_type in hw_cfg['SIMD_PERF_' + node.inDatatype.upper()]:
                node.simd_cycles = OutT//int(hw_cfg['SIMD_PERF_' + node.inDatatype.upper()][op_type])
            else:
                raise Exception("SIMD OP: {} NOT SUPPORTED".format(op_type)) #Don't Break, print warning and add defaults

def calculateMACS(graph, hw_cfg):
    for node in graph.nodes:
        if (node.op_type in util.linearTypes):
            #TODO: support MatMul, not just convolution 
            node.MACS = int(math.prod(node.output_t_size[:2]) * node.weight_t_size[4])


def mac_util(node, hw_cfg):
    macUtil = 1

    #Calculate MacUtil
    wgtWidth = node.weight_t_size[0]
    wgtHeight = node.weight_t_size[1]
    if (wgtHeight == wgtWidth):
        if (wgtHeight == 1): macUtil = float(hw_cfg['MAC_UTIL']['KER_1'])
        elif (wgtHeight == 3): macUtil = float(hw_cfg['MAC_UTIL']['KER_3'])
        elif (wgtHeight == 5): macUtil = float(hw_cfg['MAC_UTIL']['KER_5'])
        elif (wgtHeight == 7): macUtil = float(hw_cfg['MAC_UTIL']['KER_7'])
    else:
        print("WEIGHT NOT SUPPORTED: {} x {}".format(wgtWidth, wgtHeight))
        macUtil = float(hw_cfg['MAC_UTIL']['DEFAULT'])

    #Calculate Effective MacUtil (Using Datatype)
    macUtil *= float(hw_cfg['DATATYPE'][node.inDatatype.upper()]) * float(hw_cfg['DATATYPE'][node.outDatatype.upper()]) * float(hw_cfg['DATATYPE'][node.wgtDatatype.upper()])
    return macUtil



# Given a list of nodes (graph) and a system config (tiles)
# Mapper maps the work in such a way that it minimizes the cycles
# improves the overall utilization

#IMPORTS
import pandas as pd
from MBR_sim.util import *
import MBR_sim.fusion as fusion
import math

class Mapper:
    def __init__(self, hw_cfg) -> None:
        self.hw_cfg = hw_cfg
        pass
    def generate_nodes(self, csv_file, args):
        df = pd.read_csv(csv_file)

        #Format Data
        df.dropna(subset=['LyrName'], inplace=True)
        df = df.reset_index()

        self.graph = Graph("graph")
        i = 1
        for index, row in df.iterrows():
            maxWgtCapacity = 0
            if row['Type'] in linearTypes and self.hw_cfg['SYSTEM']['ENABLE_WEIGHT_SPLITTING'] == "1":
                maxWgtCapacity = int(self.hw_cfg['SYSTEM']['MAX_WEIGHT_CAPACITY'])
            node = Node(row['LyrName'])
            node.op_type = row['Type']

            #Setting Datatypes
            node.inDatatype = row['InDatatype']
            node.outDatatype = row['OutDatatype']
            node.wgtDatatype = row['WgtDatatype']

            if node.op_type in linearTypes:
                node.convID = [Node.convID]
                Node.convID += 1
                if self.hw_cfg['DATATYPE']['USE_GLOBAL'] == "1":
                    node.inDatatype = args.input_datatype
                    node.outDatatype = args.output_datatype
                    node.wgtDatatype = args.weight_datatype


            node.output_t_size = [row['OutT(W)'], row['OutT(H)'], row['OutT(D)']]
            node.input_t_size = [row['InT(W)'], row['InT(H)'], row['InT(D)']]
            if (not row.isnull().any()):
                node.weight_t_size = [int(row['WgtT(W)']), int(row['WgtT(H)']), int(row['WgtT(D)']), int(row['WgtT(Num)'])]
            node.tile = i
            node.calculatePerf(self.hw_cfg)
            splitNodes = [node]
            if maxWgtCapacity != 0:
                splitNodes = self.split_by_weight(node)
            [self.graph.add_node(node) for node in splitNodes]
            i += 1
        return self.graph
    
    def split_by_weight(self, node):
        maxWeight = int(self.hw_cfg['SYSTEM']['MAX_WEIGHT_CAPACITY'])
        slots = math.ceil(node.weight_t_size[-1]/maxWeight)
        totalWeightNum = node.weight_t_size[-2]
        split = []
        for i in range(0, slots):
            splitNode = node.copy()
            splitNode.weight_t_size[-2] = util.split(totalWeightNum, slots)[i]
            splitNode.calculatePerf(self.hw_cfg)
            split.append(splitNode)
        return split

    def fuse_nodes(self):
        fusion.fuse_simd(self.graph, self.hw_cfg)
        fusion.inline_linear_simd(self.graph, self.hw_cfg)
        fusion.spread_layers(self.graph, self.hw_cfg)
        fusion.combine_multiple_layers(self.graph, self.hw_cfg)
        return self.graph



# Given a list of nodes (graph) and a system config (tiles)
# Mapper maps the work in such a way that it minimizes the cycles
# improves the overall utilization

#IMPORTS
from cmath import nan
from doctest import OutputChecker
import pandas as pd
from util import *
import fusion

class Mapper:
    def __init__(self, hw_cfg) -> None:
        self.hw_cfg = hw_cfg
        pass
    def generate_nodes(self, csv_file):
        df = pd.read_csv(csv_file)

        #Format Data
        df.dropna(subset=['LyrName'], inplace=True)
        df = df.reset_index()
        for InT in df['InT(Size)']: df['InT(Size)'].replace({InT : int(str(InT).replace(",", ""))}, inplace=True)
        for OutT in df['OutT(Size)']: df['OutT(Size)'].replace({OutT : int(str(OutT).replace(",", ""))}, inplace=True)
        for WgtT in df['WgtT(Size)']: df['WgtT(Size)'].replace({WgtT : str(WgtT).replace(",", "")}, inplace=True)

        self.graph = Graph("graph")
        for index, row in df.iterrows():
            node = Node(row['LyrName'])
            node.op_type = row['Type']
            node.output_t_size = (row['OutT(W)'], row['OutT(H)'], row['OutT(D)'], row['OutT(Size)'])
            node.input_t_size = (row['InT(W)'], row['InT(H)'], row['InT(D)'], row['InT(Size)'])
            if (not row.isnull().any()):
                node.weight_t_size = (int(row['WgtT(W)']), int(row['WgtT(H)']), int(row['WgtT(D)']), int(row['WgtT(Num)']), int(row['WgtT(Size)']))
            self.graph.add_node(node)
        return self.graph
    
    def fuse_nodes(self):
        fusion.fuse_simd(self.graph, self.hw_cfg)
        fusion.fuse_linear(self.graph)
        return self.graph



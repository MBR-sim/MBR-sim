# Main python file
#IMPORTS
import configparser
import MBR_sim.mapper as mapper
import MBR_sim.simulate as simulate
import MBR_sim.util as util
import sys
import MBR_sim.visual as visual
import argparse

def main(args):
   #Assign unique Conv ID.
   hw_cfg = configparser.ConfigParser()
   hw_cfg.read(args.config)

   csv_file = args.csv
   if (args.macbw is not None): hw_cfg['TILE']['MAC_BW'] = str(args.macbw)
   if (args.nocbw is not None): hw_cfg['TILE']['NOC_BW'] = str(args.nocbw)
   if (args.simdbw is not None): hw_cfg['TILE']['SIMD_BW'] = str(args.simdbw)
   if (args.numtiles is not None): hw_cfg['SYSTEM']['TILES'] = str(args.numtiles)   

   map = mapper.Mapper(hw_cfg)

   graph = map.generate_nodes(csv_file)
   if hw_cfg['DATATYPE']['USE_GLOBAL'] == "1":
      graph.globalInDatatype = args.input_datatype
      graph.globalOutDatatype = args.output_datatype
      graph.globalWgtDatatype = args.weight_datatype
   # graph.print_nodes()
   
   simulate.calculateSIMDCycles(graph, hw_cfg)
   simulate.calculateMACS(graph, hw_cfg)
   # graph.print_nodes()

   for node in graph.nodes:
      node.calculatePerf(hw_cfg)

   graph = map.fuse_nodes()
   # graph.print_nodes()

   for node in graph.nodes:
      node.calculatePerf(hw_cfg)

   graph.nodes.sort(key=lambda node: node.convID)

   #Finding Totals
   tot_MACS = 0
   tot_lin_cycles = 0
   tot_tiles = 0
   tot_lyr_cycles = 0
   tot_stage_cycles = 0
   max_stage_cycles = 0
   for node in graph.nodes:
      tot_MACS += node.MACS
      tot_lin_cycles += node.linear_cycles
      tot_tiles += node.tiles
      tot_lyr_cycles += node.layer_cycles
      tot_stage_cycles += node.stage_cycles
      max_stage_cycles = max(max_stage_cycles, node.stage_cycles)

   print("Total MACS: {:.2e}".format(tot_MACS))
   print("Mac Cycles: {:.2e}".format(tot_lin_cycles))
   print("Mac Util: {:.0%}".format((tot_MACS//int(hw_cfg['TILE']['MAC_BW']))/(max_stage_cycles * tot_tiles))) #Difference Between Tensor and Parallelism
   if args.parallelism == "tensor":
      print("Total Cycles: {:.2e}".format(tot_lyr_cycles))
      print("Total Stage Cycles: {:.2e}".format(tot_stage_cycles))
      print("IPS/Chip: {}".format((int(hw_cfg['SYSTEM']['FREQ'])//tot_stage_cycles)) * (int(hw_cfg['SYSTEM']['TILES'])//tot_tiles))
      #TODO: Add Latency
   elif args.parallelism == "pipeline":
      print("Total Cycles: {:.2e}".format(tot_lyr_cycles))
      print("Total Cycle Length: {:.2e}".format(tot_lyr_cycles//tot_tiles))
      print("IPS/Chip: {}".format((int(hw_cfg['SYSTEM']['FREQ'])//tot_stage_cycles)) * (int(hw_cfg['SYSTEM']['TILES'])//tot_tiles))

   visual.resource_table(hw_cfg, graph)

if __name__ == "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("-c", "--config", help = "the path to the hardware config file", type=str, default="src/MBR_sim/configs/hw_config1.cfg")
   parser.add_argument("-f", "--csv", help = "the path to the csv file of the workload", type=str, default="src/MBR_sim/workloads/csv/ResNet50.csv")
   parser.add_argument("-p", "--parallelism", help = "Choose between tensor or pipeline parrallelism", choices=["tensor","pipeline"], type=str, default="pipeline")
   parser.add_argument("-m", "--macbw", help = "the mac bandwidth of the hardware, if not entered, uses hw_cfg", type=int)
   parser.add_argument("-b", "--nocbw", help = "the noc bandwidth of the hardware, if not entered, uses hw_cfg", type=int)
   parser.add_argument("-s", "--simdbw", help = "the simd bandwidth of the hardware, if not entered, uses hw_cfg", type=int)
   parser.add_argument("-n", "--numtiles", help = "the number of tiles in the hardware, if not entered, uses hw_cfg", type=int)
   parser.add_argument("-i", "--input_datatype", help = "the global input datatype for workload", type=str)
   parser.add_argument("-o", "--output_datatype", help = "the global output datatype for workload", type=str)
   parser.add_argument("-w", "--weight_datatype", help = "the global weight datatype for workload", type=str)
   args = parser.parse_args()
   main(args)
# Main python file
#IMPORTS
import configparser
import MBR_sim.mapper as mapper
import simulate
import MBR_sim.util as util
import sys
import visual
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
   
   simulate.calculateSIMDCycles(graph, hw_cfg)
   simulate.calculateMACS(graph, hw_cfg)

   for node in graph.nodes:
      node.calculatePerf(hw_cfg)

   graph = map.fuse_nodes()

   for node in graph.nodes:
      node.calculatePerf(hw_cfg)

   #Knob for Tensor Parrallelism
   # Take layer cycles  = orig layer cycles/tiles
   # Sum all layer cycles
   graph.print_nodes()


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
   print("Mac Util: {:.0%}".format((tot_MACS//int(hw_cfg['TILE']['MAC_BW']))/(max_stage_cycles * tot_tiles)))
   print("Total Cycles: {:.2e}".format(tot_lyr_cycles))
   print("Total Stage Cycles: {:.2e}".format(tot_stage_cycles))
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
   args = parser.parse_args()
   main(args)
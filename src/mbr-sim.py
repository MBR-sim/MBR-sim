# Main python file
#IMPORTS
import configparser
import mapper
import simulate
import util


# All the command line options
 


def main():
   hw_config_file = "configs/hw_config1.cfg"
   hw_cfg = configparser.ConfigParser()
   hw_cfg.read(hw_config_file)
   
   #INITS
   map = mapper.Mapper(hw_cfg)
   
   csv_file = "csvs/ResNet50.csv"
   graph = map.generate_nodes(csv_file)
   
   simulate.calculateSIMDCycles(graph, hw_cfg)
   simulate.calculateMACS(graph, hw_cfg)
   print(graph)

   graph = map.fuse_nodes()

   for node in graph.nodes:
      node.load_cycles = node.input_t_size[3]//int(hw_cfg['TILE']['NOC_BW'])
      node.store_cycles = node.output_t_size[3]//int(hw_cfg['TILE']['NOC_BW'])
      if any([linType in node.op_type for linType in util.linearTypes]):
         node.linear_cycles = (node.MACS//int(hw_cfg['TILE']['MAC_BW']))//simulate.mac_util(node)
      else:
         node.linear_cycles = 0
      node.layer_cycles = max(node.load_cycles, node.simd_cycles, node.linear_cycles, node.store_cycles)
      node.tiles = 1
      node.stage_cycles = node.layer_cycles//node.tiles

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

if __name__ == "__main__":
   main()
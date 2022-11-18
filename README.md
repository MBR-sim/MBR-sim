# MBR-SIM: A Speed-of-Light Model for ML Accelerators

## Installation
1. Requirements: Python 3.8
2. Open folder and run: `pip3 install .` to install the required packages.

## Command Line Arguments
**Sample Command** `python3 src/MBR_sim/mbr-sim.py`

  -h, --help            show this help message and exit
  
  -c CONFIG, --config CONFIG
                        the path to the hardware config file
  
  -f CSV, --csv CSV     the path to the csv file of the workload
  
  -p {tensor,pipeline}, --parallelism {tensor,pipeline}
                        Choose between tensor or pipeline parrallelism
  
  -m MACBW, --macbw MACBW
                        the mac bandwidth of the hardware, if not entered, uses hw_cfg
  
  -b NOCBW, --nocbw NOCBW
                        the noc bandwidth of the hardware, if not entered, uses hw_cfg
  
  -s SIMDBW, --simdbw SIMDBW
                        the simd bandwidth of the hardware, if not entered, uses hw_cfg
  
  -n NUMTILES, --numtiles NUMTILES
                        the number of tiles in the hardware, if not entered, uses hw_cfg
  
  -i INPUT_DATATYPE, --input_datatype INPUT_DATATYPE
                        the global input datatype for workload
  
  -o OUTPUT_DATATYPE, --output_datatype OUTPUT_DATATYPE
                        the global output datatype for workload
  
  -w WEIGHT_DATATYPE, --weight_datatype WEIGHT_DATATYPE
                        the global weight datatype for workload
  
  --comment COMMENT     comment character for csv files

## Results
1. Configuration 1: 576 MACs/cycle | 64 tiles

    **Command Line:** `python3 src/MBR_sim/mbr-sim.py -m 576 -n 64`
  
    IPS: 4982 
2. Configuration 2: 576 MACs/cycles | 32 tiles

    **Command Line:** `python3 src/MBR_sim/mbr-sim.py -m 576 -n 64` 

    IPS: 4881
3. Configuration 3: 1152 MACs/cycles | 32 tiles

    **Command Line:** `python3 src/MBR_sim/mbr-sim.py -m 1172 -n 32`

    IPS: 4982
    
**Authors**: Ben Maydan, Mehul Goel, Raj Parihar

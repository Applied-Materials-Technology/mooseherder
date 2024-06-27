'''
==============================================================================
EXAMPLE: Run MOOSE in parallel multiple times then read sweep results

Author: Lloyd Fletcher, Rory Spencer
==============================================================================
'''
import time
from pathlib import Path
from pprint import pprint
from mooseherder import (MooseHerd,
                         MooseRunner,
                         MooseConfig,
                         InputModifier,
                         DirectoryManager,
                         SweepReader)

NUM_PARA_RUNS = 3
USER_DIR = Path.home()

def main() -> None:
    """main: parallel herd run multiple times and read
    """
    print("-"*80)
    print('EXAMPLE: Parallel Herd Setup & Run')
    print("-"*80)
    # Setup the MOOSE input modifier and runner
    moose_input = Path('scripts/moose/moose-mech-simple.i')
    moose_modifier = InputModifier(moose_input,'#','')

    moose_config = MooseConfig().read_config(Path.cwd() / 'moose-config.json')
    moose_runner = MooseRunner(moose_config)
    moose_runner.set_run_opts(n_tasks = 1,
                              n_threads = 2,
                              redirect_out = True)

    dir_manager = DirectoryManager(n_dirs=4)

    # Start the herd and create working directories
    herd = MooseHerd([moose_runner],[moose_modifier],dir_manager)

    # Set the parallelisation options, we have 8 combinations of variables and
    # 4 MOOSE intances running, so 2 runs will be saved in each working directory
    herd.set_num_para_sims(n_para=4)

     # Send all the output to the examples directory and clear out old output
    dir_manager.set_base_dir(Path('examples/'))
    dir_manager.clear_dirs()
    dir_manager.create_dirs()

    # Create variables to sweep in a list of dictionaries, 8 combinations possible.
    n_elem_y = [10,20]
    e_mod = [1e9,2e9]
    p_rat = [0.3,0.35]
    moose_vars = list()
    for nn in n_elem_y:
        for ee in e_mod:
            for pp in p_rat:
                # Needs to be list[list[dict]] - outer list is simulation iteration,
                # inner list is what is passed to each runner/inputmodifier
                moose_vars.append([{'n_elem_y':nn,'e_modulus':ee,'p_ratio':pp}])

    print('Herd sweep variables:')
    pprint(moose_vars)
    print()

    # Run all variable combinations across 4 MOOSE instances with two runs saved in
    # each sim-workdir
    for rr in range(NUM_PARA_RUNS):
        herd.run_para(moose_vars)

        print(f'Run time (para {rr+1}) = {herd.get_sweep_time():.3f} seconds')
        print('------------------------------------------')

    print("-"*80)
    print('EXAMPLE: Read Herd Sweep Output')
    print("-"*80)
    sweep_reader = SweepReader(dir_manager,num_para_read=4)
    output_files = sweep_reader.read_all_output_keys()

    print('Herd output files (from output_keys.json):')
    pprint(output_files)
    print()

    print("-"*80)
    print('Reading all output files sequentially as a list(SimData).')
    print()
    start_time = time.perf_counter()
    read_all = sweep_reader.read_results_sequential()
    read_time_seq = time.perf_counter() - start_time

    print(f'Number of simulations outputs: {len(read_all):d}')

    print("-"*80)
    print('Reading all output files in parallel as list(SimData).')
    print()
    start_time = time.perf_counter()
    read_all = sweep_reader.read_results_para()
    read_time_para = time.perf_counter() - start_time

    print(f'Number of simulations outputs: {len(read_all):d}')
    print()
    print("="*80)
    print(f'Read time sequential = {read_time_seq:.6f} seconds')
    print(f'Read time parallel   = {read_time_para:.6f} seconds')
    print("="*80)
    print()

if __name__ == '__main__':
    main()

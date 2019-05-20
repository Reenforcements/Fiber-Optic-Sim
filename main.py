from FiberOpticSimulation import *
import argparse
import multiprocessing
from multiprocessing import queues
from numpy import mean

# Sample command:
# python main.py --simulation_count 16 --node_count 10 --lambda 5 --mu 1 --wavelength_count 10 --wavelength_mode between_any --transient_count 5000 --target_count 50000 --step_wavelength

parser = argparse.ArgumentParser(description="Run an optical network simulation.")

parser.add_argument("--simulation_count", type=int, default=8, help="The number of parallel simulations to run and average.")
parser.add_argument("--node_count", type=int, action='store', required=True, help="The number of nodes on the bus network.")
parser.add_argument("--lambda", type=float, action='store', dest="lambda_parameter", required=True, help="The average arrival rate.")
parser.add_argument("--mu", type=float, action='store', dest="mu_parameter", required=True, help="The average duration of each connection.")
parser.add_argument("--wavelength_count", type=int, action='store', required=True, help="The number of different wavelengths available to the bus.")
parser.add_argument("--wavelength_mode", action='store', required=True, choices=[ConnectionDirector.WavelengthMode_Between_Any, ConnectionDirector.WavelengthMode_First_and_Last, ConnectionDirector.WavelengthMode_Wavelength_Conversion],
default=[ConnectionDirector.WavelengthMode_Between_Any], help="""One of the following simulation modes: 
between_any means any node can be a start node and any node can be an end node. 
first_and_last means connections can only originate from node 1 and end at node 10. 
wavelength_conversion allows different wavelengths to be used between nodes.""")

parser.add_argument("--transient_count", type=int, action='store', required=True, help="How many events to ignore at the beginning of the simulation.")
parser.add_argument("--target_count", type=int, action='store', required=True, help="How many events after the transient amount to collect statistics on.")

parser.add_argument("--step_wavelength", action='store_true', required=False, default=False, help="Run multiple batches and increase W from 1 to wavelength_count.")

args = parser.parse_args()

def run_batch(args, wavelength_count):
    all_statistics = multiprocessing.queues.SimpleQueue()
    sims = []
    for i in range(0, args.simulation_count):
        sim = FiberOpticSimulation(
            node_count=args.node_count,
            lambda_parameter=args.lambda_parameter,
            mu_parameter=args.mu_parameter,
            wavelength_mode=args.wavelength_mode,
            wavelength_count=wavelength_count,
            transient_count=args.transient_count,
            target_count=args.target_count)
        sims.append(sim)
        sim.all_statistics = all_statistics
        sim.start_simulation()

    unfinished_sims = list(sims)
    while len(unfinished_sims) > 0:
        unfinished_sims[0].wait_for_simulation()
        unfinished_sims.remove(unfinished_sims[0])

    Pbs = []
    while all_statistics.empty() == False:
        s = all_statistics.get()
        print(s)
        Pbs.append(s["Pb"])

    return mean(Pbs)


if args.step_wavelength is False:
    Pb_avg = run_batch(args, args.wavelength_count)
    print("Average Pb for W={} is {}.".format(args.wavelength_count, Pb_avg))
else:
    Pb_averages = []
    for i in range(2, args.wavelength_count+1):
        Pb_avg = run_batch(args, i)
        Pb_averages.append(Pb_avg)
        print("Total average Pb for W={} is {}.".format(i, Pb_avg))

    for w, pb in enumerate(Pb_averages):
        print("Total average Pb for W={} is {}.".format(w+2, pb))
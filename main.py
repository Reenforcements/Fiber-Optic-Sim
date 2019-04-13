from FiberOpticSimulation import *
import argparse
import multiprocessing
from multiprocessing import queues

# Sample command:
# python main.py --node_count 10 --lambda 5 --mu 1 --wavelength_count 10 --wavelength_mode between_any --transient_count 100 --target_count 800

parser = argparse.ArgumentParser(description="Run an optical network simulation.")

parser.add_argument("--simulation_count", type=int, default=8, help="The number of simulations to run and average.")
parser.add_argument("--node_count", type=int, action='store', required=True, help="The number of nodes on the bus network.")
parser.add_argument("--lambda", type=float, action='store', dest="lambda_parameter", required=True, help="The average arrival rate.")
parser.add_argument("--mu", type=float, action='store', dest="mu_parameter", required=True, help="The average duration of each connection.")
parser.add_argument("--wavelength_count", type=int, action='store', required=True, help="The number of different wavelengths available to the bus.")

parser.add_argument("--transient_count", type=int, action='store', required=True, help="How many connections to ignore at the beginning of the simulation.")
parser.add_argument("--target_count", type=int, action='store', required=True, help="How many connections after the transient amount to collect statistics on.")

parser.add_argument("--wavelength_mode", action='store', required=True, choices=[ConnectionDirector.WavelengthMode_Between_Any, ConnectionDirector.WavelengthMode_First_and_Last, ConnectionDirector.WavelengthMode_Wavelength_Conversion],
default=[ConnectionDirector.WavelengthMode_Between_Any], help="""The simulation mode. 
between_any means any node can be a start node and any node can be an end node. 
first_and_last means connections can only originate from node 1 and end at node 10. 
wavelength_conversion allows different wavelengths to be used between nodes.""")

args = parser.parse_args()

print(args)
print("Running {} simulations on separate threads...".format(args.simulation_count))
all_statistics = multiprocessing.queues.SimpleQueue()
sims = []
for i in range(0, args.simulation_count):
    sim = FiberOpticSimulation(
        node_count=args.node_count,
        lambda_parameter=args.lambda_parameter,
        mu_parameter=args.mu_parameter,
        wavelength_mode=args.wavelength_mode,
        wavelength_count=args.wavelength_count,
        transient_count=args.transient_count,
        target_count=args.target_count)
    sims.append(sim)
    sim.all_statistics = all_statistics
    sim.start_simulation()

unfinished_sims = list(sims)
while len(unfinished_sims) > 0:
    unfinished_sims[0].wait_for_simulation()
    unfinished_sims.remove(unfinished_sims[0])

print("All simulations complete!")
while all_statistics.empty() == False:
    print(all_statistics.get())
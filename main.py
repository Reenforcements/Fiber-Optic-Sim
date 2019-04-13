from FiberOpticSimulation import *
import argparse


# Sample command:
# python main.py --node_count 10 --lambda 5 --mu 1 --wavelength_count 10 --wavelength_mode between_any

parser = argparse.ArgumentParser(description="Run an optical network simulation.")

parser.add_argument("--simulation_count", type=int, default=8, help="The number of simulations to run and average.")
parser.add_argument("--node_count", type=int, action='store', required=True, default=10, help="The number of nodes on the bus network.")
parser.add_argument("--lambda", type=float, action='store', dest="lambda_parameter", required=True, default=5.0, help="The average arrival rate.")
parser.add_argument("--mu", type=float, action='store', dest="mu_parameter", required=True, default=1.0, help="The average duration of each connection.")
parser.add_argument("--wavelength_count", type=int, action='store', required=True, default=2, help="The number of different wavelengths available to the bus.")

parser.add_argument("--wavelength_mode", action='store', required=True, choices=["between_any", "first_and_last", "wavelength_conversion"],
default=["between_any"], help="""The simulation mode. 
between_any means any node can be a start node and any node can be an end node. 
first_and_last means connections can only originate from node 1 and end at node 10. 
wavelength_conversion allows different wavelengths to be used between nodes.""")


args = parser.parse_args()

print(args)
print("Running {} simulations on separate threads...".format(args.simulation_count))
sims = []
for i in range(0, args.simulation_count):
    sim = FiberOpticSimulation(node_count=args.node_count, lambda_parameter=args.lambda_parameter, mu_parameter=args.mu_parameter, wavelength_count=args.wavelength_count)
    sims.append(sim)
    sim.start_simulation()

while len(sims) > 0:
    sims[0].wait_for_simulation()
    sims.remove(sims[0])

print("All simulations complete!")
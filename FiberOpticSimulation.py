import threading
from Queue import PriorityQueue
import numpy

class Trunk:
    def __init__(self, start, end, wavelength):
        # Trunks always go from left to right (lower to higher value).
        assert start != end, "Start and end cannot be identical."
        self.start = min(start,end)
        self.end = max(start,end)

        self.occupied = False
        self.wavelength = wavelength

    def __str__(self):
        return "Start: {}, End: {}, Occupied: {}, Wavelength: {}".format(self.start, self.end, self.occupied, self.wavelength)


class Connection:
    """
    A single connection spans one or more trunks.
    If wavelength conversion is enabled, a connection's wavelength can vary across it.
    """
    def __init__(self, start_node, end_node, trunks=None):
        assert start_node != end_node, "Start and end nodes cannot be identical."
        self.start_node = min(start_node, end_node)
        self.end_node = max(start_node, end_node)
        self.trunks = trunks

        self.blocked = None

    def has_route(self):
        return self.trunks is not None

    def acquireRoute(self, trunks):
        self.trunks = trunks
        for trunk in trunks:
            assert trunk.occupied == False, "Trying to occupy an occupied trunk: {}".format(trunk)
            trunk.occupied = True

    def releaseRoute(self):
        assert self.trunks is not None, "Trying to release a nonexistant route."
        for trunk in self.trunks:
            assert trunk.occupied == True, "Trying to release an unoccupied trunk: {}".format(trunk)
            trunk.occupied = False
        self.trunks = []

    def __str__(self):
        if self.has_route() is False:
            return "No trunks"

        s = "["
        for t in self.trunks:
            s += " ({}){}->{}, ".format(t.wavelength, t.start, t.end)

        return s + "]"

class ConnectionDirector:
    """
    Handles decisions regarding how and if a connection can be routed (or if it needs to be blocked.)

    Connections are always specified from left to right. If not, they're swapped so they are.
    """

    WavelengthMode_Between_Any = "between_any"
    WavelengthMode_First_and_Last = "first_and_last"
    WavelengthMode_Wavelength_Conversion = "wavelength_conversion"

    def __init__(self, node_count, wavelength_count, wavelength_mode):
        assert node_count >= 2, "Node count must be greater than or equal to 2."
        assert wavelength_count >= 1, "Must have at least one wavelength."
        assert wavelength_mode in [self.WavelengthMode_Between_Any, self.WavelengthMode_First_and_Last, self.WavelengthMode_Wavelength_Conversion], "Invalid wavelength mode."

        self.node_count = node_count
        self.wavelength_count = wavelength_count
        self.wavelength_mode = wavelength_mode

        # Generate trunks between nodes.
        # This will be a list of lists, since we need to account for the different wavelengths.
        self.inter_node_trunks = []
        for t in range(0, node_count-1):
            # Make a new list to hold all the different wavelength trunks between the t and t+1 nodes
            trunks = []
            self.inter_node_trunks.append(trunks)
            # Make trunks between the two nodes for all the wavelengths.
            for w in range(0, wavelength_count):
                trunks.append( Trunk(start=t, end=(t+1), wavelength=w) )

    def generate_connection(self):
        if self.wavelength_mode == self.WavelengthMode_Between_Any:
            # Generate a random start and end node.
            start_node = numpy.random.random_integers(low=0, high=(self.node_count-1))
            # Ensure our end node is different
            end_node = start_node
            while end_node == start_node:
                end_node = numpy.random.random_integers(low=0, high=(self.node_count-1))

            connection = Connection(start_node=start_node, end_node=end_node)
            return connection

        elif self.wavelength_mode == self.WavelengthMode_First_and_Last:
            start_node = 0
            end_node = self.node_count-1
            connection = Connection(start_node=start_node, end_node=end_node)
            return connection

        elif self.wavelength_mode == self.WavelengthMode_Wavelength_Conversion:
            None
        print(self.wavelength_mode, self.WavelengthMode_First_and_Last)
        return None

    def route(self, connection):
        if self.wavelength_mode == self.WavelengthMode_Between_Any or self.wavelength_mode == self.WavelengthMode_First_and_Last:
            trunks = None
            # Attempt all wavelengths
            for w in range(0, self.wavelength_count):
                # Try a path using wavelength w.
                trunks = []
                for i in range(connection.start_node, connection.end_node):
                    t = self.inter_node_trunks[i][w]
                    if t.occupied == False:
                        trunks.append(t)
                    else:
                        # This path definitely won't work.
                        trunks = None
                        break

                if trunks is not None:
                    # We have a valid path through
                    # Give the connection the full route
                    connection.acquireRoute(trunks)
                    return True

            return False
        elif self.wavelength_mode == self.WavelengthMode_Wavelength_Conversion:
            None

class SimulationEvent():
    # The two different event types.
    ConnectionRequested = 1
    ConnectionFinished = 2

    def __init__(self, type, rate, simulation, last_event=None):
        self.type = type
        self.time = SimulationEvent.get_next_event_time(rate)
        if last_event is not None:
            self.absolute_time = last_event.absolute_time + self.time
        else:
            self.absolute_time = self.time

        # Add ourselves to the simulation
        self.simulation = simulation
        simulation.add_event(self)

        self.connection = None

    def set_connection(self, connection):
        self.connection = connection

    @classmethod
    def get_next_event_time(cls, rate):
        return numpy.random.exponential(1.0 / rate)



class FiberOpticSimulation():

    """Runs a single simulation. This was chosen to be a class to allow multiple simulations results to be averaged."""
    def __init__(self, node_count=10, lambda_parameter=5.0, mu_parameter=1.0, wavelength_count=10, wavelength_mode=ConnectionDirector.WavelengthMode_Between_Any, transient_count=100, target_count=800):
        self.node_count = node_count
        self.lambda_parameter = lambda_parameter
        self.mu_parameter = mu_parameter
        self.wavelength_count = wavelength_count
        self.wavelength_mode = wavelength_mode
        self.transient_count = transient_count
        self.target_count = target_count

        # The connection director will validates, blocks, and makes connections.
        self.connectionDirector = ConnectionDirector(node_count=node_count, wavelength_count=wavelength_count, wavelength_mode=wavelength_mode)
        self.event_queue = PriorityQueue()

        self.thread = None
        self.event_index = 0
        self.is_debugging = True

    """Start the simulation from the main thread."""
    def start_simulation(self):
        self.thread = threading.Thread(target=self)
        self.thread.start()

    """Called by the thread to actually run the simulation."""
    def __call__(self, *args, **kwargs):
        # Make the initial event
        initial_event = SimulationEvent(
            type=SimulationEvent.ConnectionRequested,
            rate=self.lambda_parameter,
            simulation=self,
            last_event=None)

        while self.target_count_done() is False:
            assert self.event_queue.empty() == False, "Event queue is empty somehow."

            # Get the next event
            next_event = self.event_queue.get()[1]
            self.debug_print("({}) Got next event of type {}.".format(
                next_event.absolute_time,
                "ConnectionRequested" if next_event.type == SimulationEvent.ConnectionRequested else "ConnectionFinished"))

            if next_event.type == SimulationEvent.ConnectionRequested:
                # Generate the next connection requested event.
                next_connection_requested_event = SimulationEvent(
                    type=SimulationEvent.ConnectionRequested,
                    rate=self.lambda_parameter,
                    simulation=self,
                    last_event=next_event)

                self.debug_print("({}) Generated next ConnectionRequest for {}.".format(next_event.absolute_time, next_connection_requested_event.absolute_time))

                # Generate a connection
                new_connection = self.connectionDirector.generate_connection()

                self.debug_print("({}) Attempting to route a connection from {} to {}.".format(next_event.absolute_time, new_connection.start_node, new_connection.end_node))

                if self.connectionDirector.route(new_connection):
                    # Successfully found a route.
                    new_connection.blocked = False
                    self.debug_print("({}) Successfully routed the connection: {}".format(next_event.absolute_time, new_connection))
                    # Create a "finished" event for the future.
                    finished_event = SimulationEvent(
                        type=SimulationEvent.ConnectionFinished,
                        rate=self.mu_parameter,
                        simulation=self,
                        last_event=next_event)
                    finished_event.connection = new_connection
                    self.debug_print("({}) Generated the ConnectionFinished event for {}.".format(next_event.absolute_time, finished_event.absolute_time))
                else:
                    # Couldn't route the connection. It must be dropped.
                    new_connection.blocked = True
                    self.debug_print("({}) Blocked connection.".format(next_event.absolute_time))

            elif next_event.type == SimulationEvent.ConnectionFinished:
                assert next_event.connection is not None, "Connection for ConnectionFinished event is None."
                self.debug_print("({}) Releasing connection route: {}".format(finished_event.absolute_time, next_event.connection))
                next_event.connection.releaseRoute()



        print("Completed a simulation.")

    """Will \"join\" the thread to wait for it to finish."""
    def wait_for_simulation(self):
        while self.thread.is_alive():
            self.thread.join()
        for s in self.debug_print_statements:
            print(s)
        return

    def transient_done(self):
        return self.event_index > self.transient_count

    def target_count_done(self):
        return (self.event_index - self.transient_count) > self.target_count

    def add_event(self, event):
        self.event_queue.put( (event.absolute_time, event) )
        self.event_index += 1

    debug_print_statements = []
    def debug_print(self, text):
        if self.is_debugging:
            self.debug_print_statements.append(text)


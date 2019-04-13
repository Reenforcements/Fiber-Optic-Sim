import threading

class Trunk:
    def __init__(self, start, end, wavelength):
        # Trunks always go from left to right (lower to higher value).
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
    def __init__(self, trunks):
        self.trunks = None

    def aquireRoute(self, trunks):
        self.trunks = trunks
        for trunk in trunks:
            assert trunk.occupied == False, "Trying to occupy an occupied trunk: {}".format(trunk)
            trunk.occupied = True

    def releaseRoute(self):
        assert self.trunks is not None, "Trying to release a nonexistant route."
        for trunk in self.trunks:
            assert trunk.occupied == True, "Trying to release an unoccupied trunk: {}".format(trunk)
            trunk.occupied = False


class ConnectionDirector:
    """
    Handles decisions regarding how and if a connection can be routed (or if it needs to be blocked.)

    Connections are always specified from left to right. If not, they're swapped so they are.
    """
    def __init__(self, node_count, wavelength_count):
        assert node_count >= 2, "Node count must be greater than or equal to 2."
        assert wavelength_count >= 1, "Must have at least one wavelength."

        self.node_count = node_count
        self.wavelength_count = wavelength_count

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


class FiberOpticSimulation():
    """Runs a single simulation. This was chosen to be a class to allow multiple simulations results to be averaged."""
    def __init__(self, node_count=10, lambda_parameter=5.0, mu_parameter=1.0, wavelength_count=10):
        self.node_count = node_count
        self.lambda_parameter = lambda_parameter
        self.mu_parameter = mu_parameter
        self.wavelength_count = wavelength_count

        # The connection director will validates, blocks, and makes connections.
        self.connectionDirector = ConnectionDirector(node_count=node_count, wavelength_count=wavelength_count)

        self.thread = None

    """Start the simulation from the main thread."""
    def start_simulation(self):
        self.thread = threading.Thread(target=self)
        self.thread.start()

    """Called by the thread to actually run the simulation."""
    def __call__(self, *args, **kwargs):
        print("Did the simulation.")

    """Will \"join\" the thread to wait for it to finish."""
    def wait_for_simulation(self):
        while self.thread.is_alive():
            self.thread.join()
        return


import threading

class Connection:
    """A single connection is made up of one or more links."""

class ConnectionDirector:
    """
    Handles decisions regarding how and if a connection can be routed (or if it needs to be blocked.)

    Connections are always specified from left to right. If not, they're swapped so they are.
    """
    def __init__(self, links):
        self.links = []

class FiberOpticSimulation():
    """Runs a single simulation. This was chosen to be a class to allow multiple simulations results to be averaged."""
    def __init__(self, node_count=10, lambda_parameter=5.0, mu_parameter=1.0, wavelength_count=10):
        self.node_count = node_count
        self.lambda_parameter = lambda_parameter
        self.mu_parameter = mu_parameter
        self.wavelength_count = wavelength_count

        # Generate the links between nodes.
        links = []
        self.connectionDirector = ConnectionDirector(links)

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


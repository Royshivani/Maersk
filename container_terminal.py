import simpy
import random

# Constants
AVG_ARRIVAL_TIME = 5  # Average time between vessel arrivals (hours)
CONTAINERS_PER_VESSEL = 150  # Number of containers per vessel
BERTHS = 2  # Number of berths
CRANES = 2  # Number of quay cranes
TRUCKS = 3  # Number of trucks
CRANE_MOVE_TIME = 3  # Time to move one container (minutes)
TRUCK_TRIP_TIME = 6  # Time for truck to drop off container and return (minutes)
SIMULATION_TIME = 1000  # Total simulation time (minutes)

class Terminal:
    def __init__(self, env, num_berths, num_cranes, num_trucks):
        self.env = env
        self.berths = simpy.Resource(env, num_berths)
        self.cranes = simpy.Resource(env, num_cranes)
        self.trucks = simpy.Resource(env, num_trucks)

    def log(self, message):
        print(f"Time {self.env.now}: {message}")

class Vessel:
    def __init__(self, env, name, terminal):
        self.env = env
        self.name = name
        self.terminal = terminal
        self.process = env.process(self.arrive())

    def arrive(self):
        self.terminal.log(f"Vessel {self.name} arrives")
        with self.terminal.berths.request() as request:
            yield request
            self.terminal.log(f"Vessel {self.name} berths")
            yield self.env.process(self.unload())
            self.terminal.log(f"Vessel {self.name} leaves")

    def unload(self):
        for i in range(CONTAINERS_PER_VESSEL):
            with self.terminal.cranes.request() as request_crane:
                yield request_crane
                self.terminal.log(f"Crane starts unloading container {i+1} from Vessel {self.name}")
                yield self.env.timeout(CRANE_MOVE_TIME)

                with self.terminal.trucks.request() as request_truck:
                    yield request_truck
                    self.terminal.log(f"Truck starts moving container {i+1} from Vessel {self.name}")
                    yield self.env.timeout(TRUCK_TRIP_TIME)
                    self.terminal.log(f"Truck delivers container {i+1} from Vessel {self.name} to yard")

class VesselGenerator:
    def __init__(self, env, terminal, avg_arrival_time):
        self.env = env
        self.terminal = terminal
        self.avg_arrival_time = avg_arrival_time
        self.vessel_count = 0
        self.process = env.process(self.run())

    def run(self):
        while True:
            yield self.env.timeout(random.expovariate(1 / self.avg_arrival_time) * 60)  # Convert hours to minutes
            self.vessel_count += 1
            Vessel(self.env, f"Vessel_{self.vessel_count}", self.terminal)

def run_simulation(simulation_time):
    env = simpy.Environment()
    terminal = Terminal(env, BERTHS, CRANES, TRUCKS)
    VesselGenerator(env, terminal, AVG_ARRIVAL_TIME)
    env.run(until=simulation_time)

# Run the simulation
run_simulation(SIMULATION_TIME)

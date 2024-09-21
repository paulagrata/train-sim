import sys

class Passenger:
    def __init__(self, passenger_id, p_type, arrival_time, destination, start_station):
        self.passenger_id = passenger_id                # passenger id
        self.p_type = p_type                            # passenger type A or type B
        self.arrival_time = arrival_time                # passenger arrival time
        self.destination = destination                  # passenger destination station
        self.start_station = start_station              # passenger starting station

class Train:
    def __init__(self, train_id, current_station, direction, capacity, num_stations):
        self.train_id = train_id                        # train id
        self.current_station = current_station          # current station where train is
        self.direction = direction                      # 1 for forward, -1 for backward
        self.capacity = capacity                        # max number of passengers train can hold
        self.passengers = []                            # list of passengers currently on train
        self.num_stations = num_stations                # number of total stations
        self.current_time = 0                           # current time

    def move(self):
        # moves the current station based on direction 
        if self.direction == 1 and self.current_station < self.num_stations:
            self.current_station += 1
        elif self.direction == -1 and self.current_station > 1:
            self.current_station -= 1

    def board(self, passenger):
        # checks passenger's conditions

        # checks passenger's destination and current station
        if (self.direction == 1 and passenger.destination < self.current_station) or \
        (self.direction == -1 and passenger.destination > self.current_station):
            return
        
        # checks passenger arrival time
        if passenger.arrival_time > self.current_time:
            return
        
        # checks train capacity
        half_capacity = self.capacity / 2
        if len(self.passengers) < self.capacity:
            if passenger.p_type == 'B' and len(self.passengers) > half_capacity:
                return False  # Skip type B passengers if train is more than half full.
            self.passengers.append(passenger)
            return True
        return False

    def disembark(self):
        # removes passenger if they have arrived at destination
        arriving_passengers = [p for p in self.passengers if p.destination == self.current_station]
        self.passengers = [p for p in self.passengers if p.destination != self.current_station]
        return arriving_passengers
    
    def update_time(self, time):
        # updates time
        self.current_time = time 

class Station:
    def __init__(self, station_id):
        self.station_id = station_id                    # station id
        self.waiting_passengers = []                    # passengers waiting

    def add_passenger(self, passenger):
        # adds passenger to waiting passengers
        self.waiting_passengers.append(passenger)

    def board_passengers(self, train):
        # board passengers

        # filter passengers by arrival time
        ready_passengers = [p for p in self.waiting_passengers if p.arrival_time <= train.current_time]

        # sort passengers by distance to destination
        ready_passengers.sort(
            key=lambda p: (-abs(p.destination - train.current_station), p.p_type), 
            reverse=False 
        )

        # board based on conditions
        successful_boardings = [p for p in ready_passengers if train.board(p)]

        # remove only passengers that boarded
        self.waiting_passengers = [p for p in self.waiting_passengers if p not in successful_boardings]

class TrainSimulation:
    def __init__(self, num_stations, travel_time, train_frequency, train_capacity, passengers):
        self.num_stations = num_stations                # total number of stations
        self.travel_time = travel_time                  # train travel time
        self.train_frequency = train_frequency          # train frequency (time between trains)
        self.train_capacity = train_capacity            # max number of passengers each train can hold
        self.stations = [Station(i) for                 # create station objects with id corresponding to its position
                          i in range(1, num_stations + 1)]
        self.passengers = passengers                    # list of passengers in the simulation
        self.trains = []                                # list to keep track of trains
        self.time = 0                                   # current simulation time
        self.next_train_id = 1                          # ID for the next train to be created
        self.last_train_time = -train_frequency         # time the last train was spawned (initialized to allow immediate spawning)
        self.finished_passengers = []                   # list to track passengers who have completed their journey

    def spawn_train(self):
        # two trains spawn: station 1 and last station
        if self.time % self.train_frequency == 0 and self.time >= self.last_train_time + self.train_frequency:
            for train_id, start_station, direction in [(self.next_train_id, 1, 1), (self.next_train_id + 1, self.num_stations, -1)]:
                self.trains.append(Train(train_id, start_station, direction, self.train_capacity, self.num_stations))
            self.next_train_id += 2
            self.last_train_time = self.time

    def board_passengers(self, train):
        # checks if train is valid and boards passengers
        if 1 <= train.current_station <= self.num_stations:
            station = self.stations[train.current_station - 1]
            station.board_passengers(train)

    def disembark_passengers(self, train):
        # disembarks passengers
        arriving_passengers = train.disembark()
        self.finished_passengers.extend(arriving_passengers)

        # check if all passengers have arrived after disembarking and displays console message
        if len(self.finished_passengers) == len(self.passengers):
            print(f"Finished at: t={train.current_time} minutes")
            sys.exit(0)

    def simulate(self):
        # main simulation loop, runs until all passengers reach their destination
        while not len(self.finished_passengers) == len(self.passengers):
            self.spawn_train()

            # move each train and handle boarding/disembarking at the appropriate time
            if self.time % self.travel_time == 0:
                for train in self.trains:
                    train.update_time(self.time)        # update time for each train
                    self.disembark_passengers(train)
                    self.board_passengers(train)
                for train in self.trains:
                    train.move()
                self.time += self.travel_time           # increment time after all trains have moved

def read_input(file_path):
    with open(file_path, 'r') as file:
        # reads first line -> stations, travel time, train frequency, train capacity
        first_line = file.readline().strip().split()
        num_stations = int(first_line[0])
        travel_time = int(first_line[1])
        train_frequency = int(first_line[2])
        train_capacity = int(first_line[3])

        # initialize passengers and stations list
        passengers = []
        passenger_id = 1
        stations = [Station(i) for i in range(1, num_stations + 1)]  # Define local stations list

        # reads next lines -> passenger type, arrival time, destination, starting station
        for line in file:
            parts = line.strip().split()
            p_type = parts[0]
            arrival_time = int(parts[1])
            destination = int(parts[2])
            start_station = int(parts[3])

            # create passenger objects and add to appropriate  station 
            passenger = Passenger(passenger_id, p_type, arrival_time, destination, start_station)
            passengers.append(passenger)
            station = stations[start_station - 1]
            station.add_passenger(passenger)
            passenger_id += 1

    return num_stations, travel_time, train_frequency, train_capacity, passengers, stations 

if __name__ == "__main__":
    # check for correct number of command-line arguments
    if len(sys.argv) != 2:
        print("format: python train.py <input_file>")
        sys.exit(1)

    # read input data from the specified file
    input_file = sys.argv[1]
    num_stations, travel_time, train_frequency, train_capacity, passengers, stations = read_input(input_file)

    # initialize the train simulation with the provided parameters + start simulation
    simulation = TrainSimulation(num_stations, travel_time, train_frequency, train_capacity, passengers)
    simulation.stations = stations

    simulation.simulate()

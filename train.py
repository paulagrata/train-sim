import sys

class Passenger:
    def __init__(self, passenger_id, p_type, arrival_time, destination, start_station):
        self.passenger_id = passenger_id
        self.p_type = p_type
        self.arrival_time = arrival_time
        self.destination = destination
        self.start_station = start_station

class Train:
    def __init__(self, train_id, current_station, direction, capacity, num_stations):
        self.train_id = train_id
        self.current_station = current_station
        self.direction = direction
        self.capacity = capacity
        self.passengers = []
        self.num_stations = num_stations
        self.current_time = 0  # Add a current_time attribute

    def move(self):
        previous_station = self.current_station
        if self.direction == 1 and self.current_station < self.num_stations:
            self.current_station += 1
        elif self.direction == -1 and self.current_station > 1:
            self.current_station -= 1
        #print(f"t={self.current_time}: Train #{self.train_id} arrived at station {self.current_station} from station {previous_station}")

    def board(self, passenger):
        # Check if the passenger's destination is in the correct direction or at the current station
        if (self.direction == 1 and passenger.destination < self.current_station) or \
        (self.direction == -1 and passenger.destination > self.current_station):
            print(f"t={self.current_time}: Passenger #{passenger.passenger_id} cannot board Train #{self.train_id}, destination {passenger.destination} is in the wrong direction.")
            return
        
        # Ensure passenger arrival time is less than or equal to the current time
        if passenger.arrival_time > self.current_time:
            print(f"t={self.current_time}: Passenger #{passenger.passenger_id} is not ready to board Train #{self.train_id}, they arrived at the station too late.")
            return

        # Check if the train has enough capacity
        if len(self.passengers) < self.capacity:
            self.passengers.append(passenger)
            print(f"t={self.current_time}: Passenger #{passenger.passenger_id} boarded Train #{self.train_id}")
        else:
            print(f"t={self.current_time}: Train #{self.train_id} is full, cannot board Passenger #{passenger.passenger_id}")



    def disembark_passengers(self):
        arriving_passengers = [p for p in self.passengers if p.destination == self.current_station]
        for passenger in arriving_passengers:
            print(f"t={self.current_time}: Passenger #{passenger.passenger_id} disembarked from Train #{self.train_id} at station {self.current_station}")

        self.passengers = [p for p in self.passengers if p.destination != self.current_station]

        return arriving_passengers
    
    def update_time(self, time):
        self.current_time = time 

class Station:
    def __init__(self, station_id):
        self.station_id = station_id
        self.waiting_passengers = []

    def add_passenger(self, passenger):
        self.waiting_passengers.append(passenger)

    def board_passengers(self, train):
        # Filter only passengers who are ready (i.e., have arrived by current time)
        ready_passengers = [p for p in self.waiting_passengers if p.arrival_time <= train.current_time]
        
        
        # Sort passengers by distance to destination, prioritizing farther destinations first
        ready_passengers.sort(
            key=lambda p: (-abs(p.destination - train.current_station), p.p_type),  # Negative for descending distance
            reverse=False  # Keep this as False
        )

        half_capacity = train.capacity / 2

        # Only allow passengers to board if the train has space and their destination is in the correct direction
        successful_boardings = []
        for passenger in ready_passengers:
            print(f"t={train.current_time}: Passenger #{passenger.passenger_id} attempting to board Train #{train.train_id} (destination: {passenger.destination}, distance: {abs(passenger.destination - train.current_station)}).")
            if len(train.passengers) < train.capacity:  # Check if there's space on the train

                if passenger.p_type == 'B' and len(train.passengers) > half_capacity:
                    print(f"t={train.current_time}: Train #{train.train_id} is more than half full, Passenger #{passenger.passenger_id} ({passenger.p_type}) cannot board.")
                    continue  # Skip to the next passenger

                if (train.direction == 1 and passenger.destination > train.current_station) or \
                (train.direction == -1 and passenger.destination < train.current_station):
                    successful_boardings.append(passenger)  # Add to successful boardings
                    train.board(passenger)
        
        # Remove only passengers that successfully boarded
        self.waiting_passengers = [p for p in self.waiting_passengers if p not in successful_boardings]




class TrainSimulation:
    def __init__(self, num_stations, travel_time, train_frequency, train_capacity, passengers):
        self.num_stations = num_stations
        self.travel_time = travel_time
        self.train_frequency = train_frequency
        self.train_capacity = train_capacity
        self.stations = [Station(i) for i in range(1, num_stations + 1)]
        self.passengers = passengers
        self.trains = []
        self.time = 0
        self.next_train_id = 1
        self.last_train_time = -train_frequency
        self.finished_passengers = []

    def spawn_train(self):
        if self.time % self.train_frequency == 0 and self.time >= self.last_train_time + self.train_frequency:
            if self.time == 0:
                print("t=0: Simulation starts.")
            # Spawn two trains
            self.trains.append(Train(self.next_train_id, 1, 1, self.train_capacity, self.num_stations))
            self.trains.append(Train(self.next_train_id + 1, self.num_stations, -1, self.train_capacity, self.num_stations))
            for train in self.trains[-2:]:
                direction = "forward" if train.direction == 1 else "backward"
                print(f"t={self.time}: Train #{train.train_id} spawned at station {train.current_station} moving {direction}.")
            self.next_train_id += 2
            self.last_train_time = self.time


    def board_passengers(self, train):
        if 1 <= train.current_station <= self.num_stations:
            station = self.stations[train.current_station - 1]
            station.board_passengers(train)  # Always attempt to board passengers at the current station


    def disembark_passengers(self, train):
        arriving_passengers = train.disembark_passengers()
        self.finished_passengers.extend(arriving_passengers)

        # Check if all passengers have arrived after disembarking
        if self.all_passengers_arrived():
            print(f"Finished at: t={train.current_time} minutes")
            sys.exit(0)  # Exit the program immediately

    def all_passengers_arrived(self):
        return len(self.finished_passengers) == len(self.passengers)

    def simulate(self):
        while not self.all_passengers_arrived() and self.time < 15:  # Increase max time limit for testing
            self.spawn_train()
            
            # Move each train and handle boarding/disembarking at the appropriate time
            if self.time % self.travel_time == 0:
                for train in self.trains:
                    train.update_time(self.time)  # Update time for each train

                    # Disembark and board passengers
                    self.disembark_passengers(train)
                    self.board_passengers(train)

                # Move each train
                for train in self.trains:
                    train.move()

                # Increment time after all trains have moved
                self.time += self.travel_time
                #print(f"Time incremented to t={self.time}")

        print("All passengers have arrived at their destinations." if self.all_passengers_arrived() else "Simulation ended without all passengers arriving.")

def read_input(file_path):
    with open(file_path, 'r') as file:
        first_line = file.readline().strip().split()
        num_stations = int(first_line[0])
        travel_time = int(first_line[1])
        train_frequency = int(first_line[2])
        train_capacity = int(first_line[3])

        passengers = []
        passenger_id = 1
        simulation_stations = [Station(i) for i in range(1, num_stations + 1)]  # Define local stations list

        for line in file:
            parts = line.strip().split()
            p_type = parts[0]
            arrival_time = int(parts[1])
            destination = int(parts[2])
            start_station = int(parts[3])
            passenger = Passenger(passenger_id, p_type, arrival_time, destination, start_station)
            passengers.append(passenger)

            # Add passenger to the appropriate station
            station = simulation_stations[start_station - 1]  # 1-based index
            station.add_passenger(passenger)
            print(f"Added passenger ID {passenger.passenger_id} to Station {start_station}")
            passenger_id += 1

    return num_stations, travel_time, train_frequency, train_capacity, passengers, simulation_stations  # Return the stations

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("format: python train.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    num_stations, travel_time, train_frequency, train_capacity, passengers, stations = read_input(input_file)
    simulation = TrainSimulation(num_stations, travel_time, train_frequency, train_capacity, passengers)
    simulation.stations = stations  # Assign the stations to the simulation
    simulation.simulate()

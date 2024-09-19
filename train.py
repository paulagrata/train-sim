import sys

class Passenger:
    def __init__(self, p_type, arrival_time, destination, start_station):
        self.p_type = p_type                    # passenger type A or type B
        self.arrival_time = arrival_time        # passenger arrival time
        self.destination = destination          # passenger destination station
        self.start_station = start_station      # passenger starting station


def read_input(file_path):
    with open(file_path, 'r') as file:
        # reads first line -> stations, travel time, train frequency, train capacity
        first_line = file.readline().strip().split()
        num_stations = int(first_line[0])
        travel_time = int(first_line[1])
        train_frequency = int(first_line[2])
        train_capacity = int(first_line[3])

        # initialize passengers list and add passenger data from next lines
        passengers = []

        for line in file:
            parts = line.strip().split()
            p_type = parts[0]
            arrival_time = int(parts[1])
            destination = int(parts[2])
            start_station = int(parts[3])
            passengers.append(Passenger(p_type,arrival_time,destination,start_station))
    
    return num_stations, travel_time, train_frequency, train_capacity, passengers

if __name__ == "__main__":
        
        # error handling
        if len(sys.argv) != 2:
            print("format: python train.py <input_file>")
            sys.exit(1)

        input_file = sys.argv[1]

        num_stations, travel_time, train_frequency, train_capacity, passengers = read_input(input_file)

        # testing
        print(f"Stations: {num_stations}, Travel Time: {travel_time}, Train Frequency: {train_frequency}, Train Capacity: {train_capacity}")
        for passenger in passengers:
            print(f"Passenger: Type={passenger.p_type}, Arrival={passenger.arrival_time}, Destination={passenger.destination}, Start Station={passenger.start_station}")


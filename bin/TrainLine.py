# HRDSOR001 08/14/2022
class TrainLine:                            # TrainLine class to identify which dictionary to read in for a transfer
    def __init__(self, name, station_dict):
        self.name = name 
        self.stations_dict = station_dict
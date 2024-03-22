#Station/Node/Vertex class
class Station:
    #Constructor - WBK
    def __init__(self, name, schedule = None, trainLineName = None, order = None, state = None, lines = None, prev_line=None, direction=None): #Schedule is optional - WBK
        self.name = name #Name of the station - WBK
        self.schedule = schedule #Train departure times from the station (now only for th CPT-Wynberg-SimonsTown train lin from Mon-Fri) - WBK
        self.neighbours = []  # A list of nodes directly accessible from the station - WBK
        self.trainLineName = trainLineName
        self.order = 0      # How many lines a station has
        self.lines = []     # All the lines a station is apart of
        self.prev_line = 0  # The line previous station
        self.direction = direction

    #Adds new edge into list of neighbours - WBK
    def add_Neighbour(self, edge):
        self.neighbours.append(edge)

    #Locates a name given the name of a destination
    def find_Neighbour(self, name):
        try:
            for i in self.neighbours:
                if i.destination.name == name:
                    found = i
        except: 
            print('Neighbour does not exist.')
            return -1
        return found
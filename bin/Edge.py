#Edge class - WBK
#Path from one node to another - WBK
class Edge:

    #Constructor - WBK
    def __init__(self, destination, cost, orientation = None):
        self.destination = destination #Second node in the edge - WBK
        self.cost = cost #The weight of the edge - WBK
        self.orientation = orientation
    
    def setCost(self, newCost):
        self.cost = newCost
    
    def addCost(self, newCost):
        self.cost = self.cost + newCost

    #ToString - WBK
    def toString(self):
        return ('Destination: ' + self.destination.name + ', Cost: ' + str(self.cost) + ', Orientation: ' + self.orientation)
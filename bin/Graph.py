from unicodedata import name
from matplotlib import scale
from matplotlib.ft2font import BOLD
import matplotlib.pyplot as plt
import networkx as nx
from bin.Interface import *
from datetime import timedelta
from PIL import Image
import matplotlib
matplotlib.use('Agg')


class Graph:
    def __init__(self, num_stations, stations_array, turn_off_targets = None, turn_off_line = None, delay_line = None, delay_time=None):  # Initilize graph
        self.V = num_stations
        self.nodes = stations_array  # Array of stations,  stations have an array of their edges(name, cost)
        self.map = []
        self.path = []
        self.targets = turn_off_targets
        self.trainLine = turn_off_line
        if self.targets==None:
            self.targets=[]
        if self.trainLine==None:
            self.trainLine=[]
        self.trainLine = turn_off_line
        self.target_graph = nx.Graph()
        self.small_graph = nx.Graph()
        self.path_graph = nx.Graph()
        self.labels = {}
        self.target_labels= {}
        self.pos = {}
        self.pos.update({'':[0,0]})
        self.delay_time = delay_time
        self.delay_line = delay_line
        self.off_graph = nx.Graph()

    def addNode(self, station):  # Add a station object to the list of nodes
        self.nodes.append(station)

    def turn_off(self, targets): # Replaces a given set of node's cost with a high value
        try:
            for targetNode in targets:
                for station in self.nodes:
                    if targetNode == station.name:
                        for edge in station.neighbours:
                            edge.setCost(str_to_time('24:00'))
            self.genMap()
        except:
            pass
    
    def turn_off_line(self, trainLine): #Given a trainline name, replaces a given set of node's cost with a high value
        try:
            for line in trainLine:
                for station in self.nodes:
                    if station.trainLineName == line:
                        for edge in station.neighbours:
                            edge.setCost(str_to_time('24:00'))
                self.genMap()
        except:
            pass
    
    def add_delay(self, delay_line, delay_time):
        try:
            for station in self.nodes:
                if station.trainLineName == delay_line:
                    for edge in station.neighbours:
                        edge.addCost(timedelta(minutes=delay_time))
            self.genMap()
        except:
            pass
        

    def genMap(self):  # Creates node map, connection for every station with its nearby nodes.
        for station in self.nodes:
            for edge in station.neighbours:
                self.map.append([station, edge])

    #Creates a representation of the node map gightling the route and any turned of stations and trainlines
    def drawMap(self, shortest_path):
        plt.clf()
        for station in self.nodes:
            self.small_graph.add_node(station.name) #Create station nodes with their names as key in a node graph
            self.labels.update({station.name:station.name}) #Add associated labels to the nodes
            for edge in station.neighbours:
                self.small_graph.add_edge(station.name,edge.destination.name) #Add edges to the graph

        #Format the output to show details of the first and the last stations given the shortest route between the two
        start_end_labels = {shortest_path[0].name:shortest_path[0].name,shortest_path[-1].name:shortest_path[-1].name,}
        start_end_graph = nx.Graph()
        start_end_graph.add_node(shortest_path[0].name)
        start_end_graph.add_node(shortest_path[-1].name)
        path_index = 1

        #Create a visual represntation of the optimatal route as another node graph
        for dest in shortest_path:
            self.path_graph.add_node(dest.name)
            try:
                self.path_graph.add_edge(dest.name, shortest_path[path_index].name)
                path_index+=1
            except:
                pass
        
        #Create a visual representation of the turned of train lines as another node graph
        try:
            for line in self.trainLine:
                for station in self.nodes:
                    if station.trainLineName == line:
                        self.off_graph.add_node(station.name)
                        for edge in station.neighbours:
                            if edge.destination.trainLineName == station.trainLineName:
                                self.off_graph.add_edge(station.name, edge.destination.name)
        except:
            pass

        #Create a visual representation of the turned of stations as another node graph
        for station in self.targets:
            self.target_graph.add_node(station)
            self.target_labels.update({station:station})
        self.pos = {'CAPE TOWN': [550.0,110.0],
        'ESPLANADE': [555.0,115.0],
        'YSTERPLAAT':[560.0,117.0],
        'KENTEMADE':[580.0,125.0],
        'CENTURY CITY':[586.0,125.0],
        'AKASIA PARK':[592.0,125.0],
        'MONTE VISTA':[598.0,125.0],
        'DE GRENDEL':[604.0,125.0],
        'AVONDALE':[610.0,125.0],
        'OOSTERZEE':[616.0,125.0],
        'WOODSTOCK': [556.0,110.0],
        'SALT RIVER':[563.0,110.0],
        'OBSERVATORY': [565.0,109.0],
        'KOEBERG RD': [570.0,110.0],
        'MAITLAND':[575.0,110.0],
        'WOLTEMADE':[580.0,112.0],
        'MUTUAL':[585.0,112.0],
        'THORNTON':[590.0,112.0],
        'GOODWOOD':[595.0,112.0],
        'VASCO':[600.0,112.0],
        'ELSIES RIVER':[605.0,112.0],
        'PAROW':[610.0,112.0],
        'TYGERBERG':[615.0,112.0],
        'BELLVILLE A':[622.0,112.0],
        'BELLVILLE D':[622.0,112.0],
        'BELLVILLE':[622.0,112.0],
        'STIKLAND':[627.0,112.0],
        'BRACKENFELL':[632.0,112.0],
        'EIKENFONTEIN':[638.0,112.0],
        'KRAAIFONTEIN':[645.0,112.0],
        'MULDERSVLEI':[663.0,112.0],
        'KOELENHOF':[659.0,108.0],
        'DU TOIT':[657.0,107.0],
        'STELLENBOSCH':[655.0,106.0],
        'VLOTTENBURG':[653.0,105.0],
        'LYNEDOCH':[651.0,104.0],
        'FAURE':[651.0,100.0],
        'EERSTE RIVER A':[642.0,104.0],
        'EERSTE RIVER D':[642.0,104.0],
        'EERSTE RIVER':[642.0,104.0],
        'MELTONROSE':[640.0,106.0],
        'BLACKHEATH':[638.0,107.0],
        'KUILS RIVER':[636.0,108.0],
        'SAREPTA':[615.0,101.0],
        'PENTECH':[613.0,100.0],
        'UNIBELL':[611.0,99.0],
        'BELHAR':[609.0,98.0],
        'LAVISTOWN':[607.0,97.0],
        'BONTEHEUWEL A':[605.0,96.0],
        'BONTEHEUWEL D':[605.0,96.0],
        'BONTEHEUWEL':[605.0,96.0],
        'LANGA':[603.0,95.0],
        'NETREG':[609.0,95.0],
        'HEIDEVELD':[611.0,94.0],
        'NYANGA':[613.0,93.0],
        'PHILIPPI':[615.0,92.0],
        'LENTEGEUR A':[615.0,88.0],
        'LENTEGEUR D':[615.0,88.0],
        "MITCHELLS PL.":[615.0,87.0],
        'KAPTEINSKLIP':[615.0,86.0],
        'STOCK ROAD':[640.0,86.0],
        'MANDALAY A':[642.0,85.0],
        'MANDALAY D':[642.0,85.0],
        'MANDALAY':[642.0,85.0],
        'NOLUNGILE':[644.0,84.0],
        'NONKQUBELA':[645.0,84.0],
        'KHAYELITSHA':[646.0,83.0],
        'KUYASA':[648.0,82.0],
        'CHRIS HANI':[650.0,81.0],
        'FIRGROVE':[652.0,99.0],
        'SOMERSET WEST':[653.0,98.0],
        'VAN DER STEL':[654.0,97.0],
        'STRAND':[655.0,96.0],
        'KLAPMUTS':[665.0,113.0],
        'PAARL':[667.0,115.0],
        'HUGUENOT':[669.0,116.0],
        'DAL JOSAFAT':[671.0,117.0],
        "MBEKWENI":[673.0,118.0],
        'WELLINGTON':[675.0,119.0],
        'MALAN':[677.0,120.0],
        'SOETENDAL':[679.0,121.0],
        'HERMON':[681.0,122.0],
        'VOELVLEI':[683.0,123.0],
        'GOUDA':[683.0,127.0],
        'TULBAGHWEG':[681.0,128.0],
        'ARTOIS':[679.0,129.0],
        'WOLSELEY':[677.0,130.0],
        'ROMANS RIVER':[675.0,131.0],
        'BREE RIVER':[673.0,132.0],
        'BOTHA':[671.0,133.0],
        'GOUDINI RD':[669.0,134.0],
        'CHAVONNES':[667.0,135.0],
        'WORCESTER':[665.0,136.0],
        'FISANTKRAAL':[655.0,116.0],
        'MELLISH':[657.0,117.0],
        'MIKPUNT':[659.0,118.0],
        'KLIPHEUWEL':[661.0,119.0],
        'WINTEVOGEL':[663.0,120.0],
        'KALBASKRAAL':[665.0,121.0],
        'ABBOTSDALE':[667.0,122.0],
        'MALMESBURY':[669.0,123.0],
        'NDABENI':[585.0,108.0],
        'PINELANDS':[586.0,107.0],
        'HAZENDAL':[587.0,106.0],
        'ATHLONE':[588.0,105.0],
        'CRAWFORD':[589.0,104.0],
        'LANSDOWNE':[590.0,103.0],
        'WETTON':[591.0,102.0],
        'OTTERY':[589.0,100.0],
        'SOUTHFIELD':[588.0,98.0],
        'MOWBRAY':[565.0,108.5],
        'ROSEBANK':[565.0,108.0],
        'RONDEBOSCH':[565.0,107.5],
        'NEWLANDS':[565.0,107.0],
        'CLAREMONT':[565.0,106.0],
        'HARFIELD RD':[565.0,105.0],
        'KENILWORTH':[565.0,104.0],
        'WYNBERG':[565.0,103.0],
        'WITTEBOME':[570.0,102.0],
        'PLUMSTEAD':[572,101.0],
        'STEURHOF':[574.0,100.0],
        'DIEPRIVIER':[576.0,99.0],
        'HEATHFIELD':[578.0,97.5],
        'RETREAT':[580.0,97.0],
        'STEENBERG':[582.0,96.0],
        'LAKESIDE':[584.0,95.0],
        'FALSE BAY':[586.0,94.0],
        'MUIZENBERG':[588.0,93.0],
        'ST JAMES':[590.0,92.0],
        'KALK BAY':[592.0,91.0],
        'FISH HOEK':[594.0,90.0],
        'SUNNY COVE':[596.0,89.0],
        'GLENCAIRN':[598.0,88.0],
        "SIMON'S TOWN":[600.0,87.0]}

        #Format the pallet output
        plt.figure(3,figsize=(30,15)) 
        nx.draw_networkx_nodes(self.small_graph,pos=self.pos,node_size=150,node_color='black',alpha=.5)
        if (self.targets[0]!=''):
            nx.draw_networkx_nodes(self.target_graph,pos=self.pos,node_size=150,node_color='red',alpha=1)
            nx.draw_networkx_labels(self.target_graph,pos=self.pos,labels=self.target_labels, font_size=15, font_color='red', font_weight = 'bold',verticalalignment="bottom")
        nx.draw_networkx_nodes(start_end_graph,pos=self.pos,node_size=400,node_color='green',alpha=1)
        nx.draw_networkx_edges(self.small_graph,pos=self.pos,edge_color='black', alpha=.7, width=2)
        nx.draw_networkx_edges(self.path_graph,pos=self.pos,edge_color='blue', alpha=1, width=6)
        nx.draw_networkx_edges(self.off_graph,pos=self.pos,edge_color='red', alpha=1, width=6)
        nx.draw_networkx_labels(self.target_graph,pos=self.pos,labels=start_end_labels, font_size=15, font_color='green', font_weight = 'bold', verticalalignment="bottom")
        
        if len(self.targets)>0:
            out_targets = ','.join(self.targets)
        else:
            out_targets = ['None']
        if len(self.trainLine)>0:
            out_lines = ','.join(self.trainLine)
        else:
            out_lines = ['None']

        plt.savefig("static/images/output_figure_"+shortest_path[-1].name+"_"+shortest_path[0].name+"_"+out_targets+"_"+out_lines+".jpeg")
        image = Image.open("static/images/output_figure_"+shortest_path[-1].name+"_"+shortest_path[0].name+"_"+out_targets+"_"+out_lines+".jpeg")
        width, height = image.size
        left = 375
        top =  200
        right = 2700
        bottom = 1320
        image = image.crop((left, top, right, bottom))

        #Save the output image to the current directory and name it according to its attributes
        image.save("static/images/output_figure_"+shortest_path[-1].name+"_"+shortest_path[0].name+"_"+out_targets+"_"+out_lines+".jpeg")

    #Print distances to all stations from the source
    def sourceToDest(self, dist):
        print("Distances from Source")
        for station, cost in dist.items():
            print(' ' + station.name, ': ', timedelta(minutes=cost / 60))  # Convert cost into int - WBK

    #Compute all the modifications to the node map and return the stations along the shortest path 
    def getPath(self, src, dest):
        self.turn_off(self.targets)
        self.turn_off_line(self.trainLine)
        self.add_delay(self.delay_line, self.delay_time)
        self.bellmanFord(src,dest)
        
        start = src  # Source node
        endpoint = dest  # Destination node
        shortest_path = [endpoint]


        while endpoint != start:  # Loop until source node
            endpoint = self.path[endpoint]  # Obtain previous node
            shortest_path.append(endpoint)
        
        self.drawMap(shortest_path)

        return shortest_path  # Source --> Destination

    def bellmanFord(self, src, dest):  # Bellman ford takes in a station
        dist = {i: float("Inf") for i in self.nodes}  # Creates a distance dictionary with all elements as infinity except the start point
        self.path = {k: None for k in self.nodes}  # Dictionary to store the routes during the cost algorithm
        dist[src] = 0

        for temp in range(
                self.V - 1):  # Loop checks if a distance is infinity or not. And whether the start dist+edge cost < edges distance value. (0)A--(5)--B--(inf)--C.
            for station, edge in self.map:  # 0+5 < inf
                if dist[station] != float("Inf") and dist[station] + int(edge.cost.total_seconds()) < dist[edge.destination]:
                    dist[edge.destination] = dist[station] + int(edge.cost.total_seconds())
                    self.path[edge.destination] = station  # Each node has 1 optimal neighbour node

        for station, edge in self.map:
            if dist[station] != float("Inf") and dist[station] + int(edge.cost.total_seconds()) < dist[edge.destination]:
                print("Graph contains negative cycle")
                return

#if __name__ == '__main__':

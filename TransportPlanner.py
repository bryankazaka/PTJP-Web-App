from hashlib import new
from json.tool import main
from datetime import timedelta
from bin.Station import Station
from bin.Edge import Edge
from bin.TrainLine import TrainLine
from bin.Graph import Graph
from bin.Interface import *

#Add trainline to node list - WBK
 #Takes name of trainline file, the node list and the available index of the array - WBK
def loadMap(trainLine, stations_array,start_point, trainLineName = None):
    #open trainLine file - WBK
    stations_file = open(trainLine,"r") 
    
    #Count current line - WBK
    i = 0 

    #For each line in file, create a station object and add its neighbours - WBK
    for x in stations_file: 
        pos_zero = x.index('0')
        #Sepereate schedule from string - WBK
        schedule = x[pos_zero:].strip().split() 

        #Create station object passing name and schedule - WBK
        node = Station(x[:pos_zero].strip(),schedule, trainLineName)
        
        #Add station object to list - WBK
        stations_array.append(node) 
        
        #If its the first station to be added to the list do nothing - WBK
        if i == 0: 
            pass
        else:
            #Calculate the cost between the current station and the one before it - WBK
            cost = str_to_time(stations_array[start_point].schedule[0]) - str_to_time(stations_array[start_point-1].schedule[0]) 
            
            #Add to the previous station, the current station as a neighbour - WBK
            stations_array[start_point-1].add_Neighbour(Edge(node,cost,0)) 

            #Add to the current station, the previous station as a neighbour - WBK
            stations_array[start_point].add_Neighbour(Edge(stations_array[start_point-1],cost,1)) 

        #Next line - WBK    
        i+=1 
        start_point+=1

#HRDSOR001 - Initializes and populates the schedule data structure
def makeSchedule(filename, area_dict, operating_day=None, trainLineName=None, orientation=None):
    times=[]
    pos_num = None
    stream_index = 0
    data_file = open(filename, 'r')
    for line in data_file:
        line = line.strip()
        if 'DAY' in line: operating_day = operationDay(line)

        elif (' - ' in line):
            if '$' in line: 
                continue

            trainLineName = line
            try:
                if (upstreamLine == trainLineName): 
                    pass
                else: 
                    stream_index = 1
            except: 
                upstreamLine = line
        elif ':' in line:
                #Cleans data into stations and their times
                data = timeFilter(line)
                station = data[0]
                
                if 'MITCHELL' in station: 
                    continue
                if 'PAARDEN' in station: 
                    continue
                
                times = data[1]

                try:
                    #Loads the schedule array [up/down stream][op_days]
                    area_dict[station][stream_index][operating_day] += times    
                    
                except: 
                        if station=='D':
                            g=station
                            station = prev[:-1] + 'A'
                            area_dict[station][stream_index][operating_day] += times
                        else: 
                            station = station[:-1].strip() 
                            area_dict[station][stream_index][operating_day] += times
                prev = station

    #Cleans the dictionary of empties (not in trainline)
    area_dict = {station:area_dict[station] for station in area_dict if area_dict[station]!=[[[],[],[]],[[],[],[]]]}    
    return area_dict

def makeSchedule2(filename, area_dict, operating_day=None, trainLineName=None, orientation=None):
    times=[]
    pos_num = None
    stream_index = 0
    data_file = open(filename, 'r')
    line_num=0
    for line in data_file:
        line = line.strip() 
        line_num+=1

        if ' - ' in line and 'CAPE TOWN' in line:
            trainLineName = line
            try:
                if (upstreamLine == trainLineName): 
                    pass
                else: 
                    stream_index = 1
            except: 
                upstreamLine = line

        # Create function getLineData, pass in condition and line returns
        if 'MONDAY' in line: 
            operating_day=line
        if 'SATURDAYS' in line: 
            operating_day=line         
        if 'SUNDAYS' in line: 
            operating_day=line
        if ':' in line:

                # Finds the first element of schedule - HRDSOR001
                for char in line:  
                    if char.isdigit(): 
                        #pos_zero to pos_digit - HRDSOR001
                        pos_num = line.index(char)   
                        break
                station = line[:pos_num].strip()

                try:    
                    station = (station[:station.index('.')]).strip()
                except: 
                    pass
                times = line[pos_num:].strip().split()

                #Removes unwanted text from times array
                times = [e for e in times if ':' in e]  
                ## Temporary hard coded fix for timetable inconsistencies
                try:                                                               
                    for n in station:
                        if n.isupper():pass
                        else:
                            if n==' ':continue
                            station = station[:station.index(n)-1].strip()
                            break
                except: pass

                if 'EERSTE RIVER' in station: 
                    station = 'EERSTE RIVER D'            ## End
        
        #Loads the schedule array [up/down stream][op_days]
                try:
                    if ('MONDAY' in operating_day):
                        area_dict[station][stream_index][0] += times
                        
                    if 'SATURDAY' in operating_day:
                        area_dict[station][stream_index][1] += times
                    else: area_dict[station][stream_index][2] += times
                except Exception as e:
                    print("ERROR: ",e,'\n')
                    print('Line:', line)
                    print('Station:', station)
                    print('Times:', times)
                    print('Days:', operating_day)
                    print(line_num)
                
    area_dict = {station:area_dict[station] for station in area_dict if area_dict[station]!=[[[],[],[]],[[],[],[]]]}      
    return area_dict

#Load in trainlines - WBK
def loadLines(stations_array, stations_dict):

    #Loads in stations from the text files
    loadMap('./CorrectTrainLines/Southern_Suburbs_Line.txt', stations_array, len(stations_array), 'CAPE TOWN - WYNBERG - SIMON`S TOWN')
    loadMap('./CorrectTrainLines/Cape_Flats_Line.txt', stations_array, len(stations_array), 'CAPE TOWN - RETREAT - VIA CAPE FLATS')
    loadMap('./CorrectTrainLines/Central_Line_One.txt', stations_array, len(stations_array), 'CAPE TOWN - LANGA - LAVISTOWN - KAPTEINSKLIP - KHAYELITSHA - CHRIS HANI')
    loadMap('./CorrectTrainLines/Central_Line_Two.txt', stations_array, len(stations_array), 'CAPE TOWN - LANGA - LAVISTOWN - KAPTEINSKLIP - KHAYELITSHA - CHRIS HANI')
    loadMap('./CorrectTrainLines/Central_Line_Three.txt', stations_array, len(stations_array), 'CAPE TOWN - LANGA - LAVISTOWN - KAPTEINSKLIP - KHAYELITSHA - CHRIS HANI')
    loadMap('./CorrectTrainLines/Central_Line_Four.txt', stations_array, len(stations_array), 'CAPE TOWN - LANGA - LAVISTOWN - KAPTEINSKLIP - KHAYELITSHA - CHRIS HANI')
    loadMap('./CorrectTrainLines/Northern_Line_One.txt', stations_array, len(stations_array), 'CAPE TOWN - BELLVILLE - WELLINGTON - STELLENBOSCH - STRAND')
    loadMap('./CorrectTrainLines/Northern_Line_Two.txt', stations_array, len(stations_array), 'CAPE TOWN - BELLVILLE - WELLINGTON - STELLENBOSCH - STRAND')
    loadMap('./CorrectTrainLines/Northern_Line_Three.txt', stations_array, len(stations_array),'CAPE TOWN - BELLVILLE - WELLINGTON - STELLENBOSCH - STRAND')
    loadMap('./CorrectTrainLines/Northern_Line_Four.txt', stations_array, len(stations_array), 'CAPE TOWN - BELLVILLE - WELLINGTON - STELLENBOSCH - STRAND')
    loadMap('./CorrectTrainLines/Northern_Line_Five.txt', stations_array, len(stations_array), 'CAPE TOWN - BELLVILLE - WELLINGTON - STELLENBOSCH - STRAND')
    loadMap('./CorrectTrainLines/Northern_Line_Six.txt', stations_array, len(stations_array), 'CAPE TOWN - BELLVILLE - VIA MONTE VISTA')
    loadMap('./CorrectTrainLines/Malmesbury-Worcester_One.txt', stations_array, len(stations_array), 'CAPE TOWN - MALMESBURY - WORCESTER')
    loadMap('./CorrectTrainLines/Malmesbury-Worcester_Two.txt', stations_array, len(stations_array), 'CAPE TOWN - MALMESBURY - WORCESTER')

    #These are special transfer points and exceptions that have to be hard coded - WBK
    #These need added schedules since they are part of > 1 trainline or you can use neighbour schedule, find arrival time and minus travel time to get current departure time
    stations_array[find_Station('HEATHFIELD',stations_array)].add_Neighbour(Edge(stations_array[find_Station('SOUTHFIELD',stations_array)],timedelta(minutes=4),1))
    stations_array[find_Station('SOUTHFIELD',stations_array)].add_Neighbour(Edge(stations_array[find_Station('HEATHFIELD', stations_array)], timedelta(minutes=4),0))
    stations_array[find_Station('SALT RIVER',stations_array)].add_Neighbour(Edge(stations_array[find_Station('KOEBERG RD',stations_array)],timedelta(minutes=2),0))
    stations_array[find_Station('KOEBERG RD',stations_array)].add_Neighbour(Edge(stations_array[find_Station('SALT RIVER', stations_array)], timedelta(minutes=2),1))
    stations_array[find_Station('CAPE TOWN',stations_array)].add_Neighbour(Edge(stations_array[find_Station('ESPLANADE',stations_array)],timedelta(minutes=4),0))
    stations_array[find_Station('ESPLANADE',stations_array)].add_Neighbour(Edge(stations_array[find_Station('CAPE TOWN', stations_array)], timedelta(minutes=4),1))
    stations_array[find_Station('YSTERPLAAT',stations_array)].add_Neighbour(Edge(stations_array[find_Station('KENTEMADE',stations_array)],timedelta(minutes=4),0))
    stations_array[find_Station('KENTEMADE',stations_array)].add_Neighbour(Edge(stations_array[find_Station('YSTERPLAAT', stations_array)], timedelta(minutes=4),1))
    stations_array.append(Station('WOLTEMADE','','CAPE TOWN - BELLVILLE - WELLINGTON - STELLENBOSCH - STRAND'))
    stations_array[find_Station('WOLTEMADE',stations_array)].add_Neighbour(Edge(stations_array[find_Station('MAITLAND',stations_array)],timedelta(minutes=3),1))
    stations_array[find_Station('MAITLAND',stations_array)].add_Neighbour(Edge(stations_array[find_Station('WOLTEMADE', stations_array)], timedelta(minutes=3),0))
    stations_array[find_Station('WOLTEMADE',stations_array)].add_Neighbour(Edge(stations_array[find_Station('MUTUAL',stations_array)],timedelta(minutes=2),0))
    stations_array[find_Station('MUTUAL',stations_array)].add_Neighbour(Edge(stations_array[find_Station('WOLTEMADE', stations_array)], timedelta(minutes=2),1))
    stations_array[find_Station('THORNTON',stations_array)].add_Neighbour(Edge(stations_array[find_Station('MUTUAL',stations_array)],timedelta(minutes=3),1))
    stations_array[find_Station('MUTUAL',stations_array)].add_Neighbour(Edge(stations_array[find_Station('THORNTON', stations_array)], timedelta(minutes=3),0))
    stations_array[find_Station('PINELANDS',stations_array)].add_Neighbour(Edge(stations_array[find_Station('LANGA',stations_array)],timedelta(minutes=5),0))
    stations_array[find_Station('LANGA',stations_array)].add_Neighbour(Edge(stations_array[find_Station('PINELANDS', stations_array)], timedelta(minutes=5),1))
    stations_array[find_Station('BONTEHEUWEL A',stations_array)].add_Neighbour(Edge(stations_array[find_Station('LANGA',stations_array)],timedelta(minutes=3),1))
    stations_array[find_Station('LANGA',stations_array)].add_Neighbour(Edge(stations_array[find_Station('BONTEHEUWEL A', stations_array)], timedelta(minutes=3),0))
    stations_array[find_Station('BONTEHEUWEL A',stations_array)].add_Neighbour(Edge(stations_array[find_Station('LAVISTOWN',stations_array)],timedelta(minutes=4),0))
    stations_array[find_Station('LAVISTOWN',stations_array)].add_Neighbour(Edge(stations_array[find_Station('BONTEHEUWEL A', stations_array)], timedelta(minutes=4),1))
    stations_array[find_Station('STOCK ROAD',stations_array)].add_Neighbour(Edge(stations_array[find_Station('PHILIPPI',stations_array)],timedelta(minutes=4),1))
    stations_array[find_Station('PHILIPPI',stations_array)].add_Neighbour(Edge(stations_array[find_Station('STOCK ROAD', stations_array)], timedelta(minutes=4),0))
    stations_array[find_Station('BELLVILLE',stations_array)].add_Neighbour(Edge(stations_array[find_Station('BELLVILLE A',stations_array)],timedelta(minutes=1),1))
    stations_array[find_Station('BELLVILLE A',stations_array)].add_Neighbour(Edge(stations_array[find_Station('BELLVILLE', stations_array)], timedelta(minutes=1),0))
    stations_array[find_Station('BELLVILLE',stations_array)].add_Neighbour(Edge(stations_array[find_Station('BELLVILLE D',stations_array)],timedelta(minutes=1),1))
    stations_array[find_Station('BELLVILLE D',stations_array)].add_Neighbour(Edge(stations_array[find_Station('BELLVILLE', stations_array)], timedelta(minutes=1),0))
    stations_array[find_Station('LYNEDOCH',stations_array)].add_Neighbour(Edge(stations_array[find_Station('EERSTE RIVER D',stations_array)],timedelta(minutes=6),1))
    stations_array[find_Station('EERSTE RIVER D',stations_array)].add_Neighbour(Edge(stations_array[find_Station('LYNEDOCH', stations_array)], timedelta(minutes=6),0))
    stations_array[find_Station('STIKLAND',stations_array)].add_Neighbour(Edge(stations_array[find_Station('BELLVILLE D', stations_array)], timedelta(minutes=4),1))
    stations_array[find_Station('BELLVILLE D',stations_array)].add_Neighbour(Edge(stations_array[find_Station('STIKLAND',stations_array)],timedelta(minutes=4),0))
    stations_array[find_Station('KRAAIFONTEIN',stations_array)].add_Neighbour(Edge(stations_array[find_Station('MULDERSVLEI', stations_array)], timedelta(minutes=11),0))
    stations_array[find_Station('MULDERSVLEI',stations_array)].add_Neighbour(Edge(stations_array[find_Station('KRAAIFONTEIN',stations_array)],timedelta(minutes=11),1))
    stations_array[find_Station('KRAAIFONTEIN',stations_array)].add_Neighbour(Edge(stations_array[find_Station('FISANTKRAAL', stations_array)], timedelta(minutes=11),0))
    stations_array[find_Station('FISANTKRAAL',stations_array)].add_Neighbour(Edge(stations_array[find_Station('KRAAIFONTEIN',stations_array)],timedelta(minutes=11),1))
    stations_array[find_Station('KOELENHOF',stations_array)].add_Neighbour(Edge(stations_array[find_Station('MULDERSVLEI', stations_array)], timedelta(minutes=6),1))
    stations_array[find_Station('MULDERSVLEI',stations_array)].add_Neighbour(Edge(stations_array[find_Station('KOELENHOF',stations_array)],timedelta(minutes=6),0))
    stations_array[find_Station('WELLINGTON',stations_array)].add_Neighbour(Edge(stations_array[find_Station('MALAN', stations_array)], timedelta(minutes=7),0))
    stations_array[find_Station('MALAN',stations_array)].add_Neighbour(Edge(stations_array[find_Station('WELLINGTON',stations_array)],timedelta(minutes=7),1))
    
    for i in stations_array:
        stations_dict[i.name] = None

#Reverses trainline name for different direction
def reverseLine(lineName):
    temp = lineName.split(' - ')
    temp.reverse()
    temp=' - '.join(temp)
    return temp

# Returns the route based off an arrival time
def arrivalPath(line_dict, route, start, schedule_index):
    departure_stack = {}
    str_out = []

    for i in range(len(route)-1,0,-1):
        Current = route[i]
        Next = route[i-1]
        
        orientation_current = getOrientation(Current)
        orientation_next = getOrientation(Next)
        if orientation_current==None: orientation_current=orientation_next
        
        try:
            current_schedule= line_dict[Current.trainLineName].stations_dict[Current.name][orientation_current][schedule_index]
            next_schedule= line_dict[Next.trainLineName].stations_dict[Next.name][orientation_next][schedule_index]
        except:
            continue
        
        edge_cost = Current.find_Neighbour(Next.name).cost

        depart_option = findDeparture(current_schedule,start,'Arrival')
        next_depart = findDeparture(next_schedule, depart_option-edge_cost,'Arrival')
        
        str_out.append('    '+Current.name + ': '+ str(depart_option))

        if depart_option == -1 or next_depart == -1: 
            return 'Sorry trip is not available !'

        trivial_depart = depart_option-edge_cost
        if Current.trainLineName != Next.trainLineName: 
            trivial_depart -= timedelta(minutes=5)
        
        start = next_depart
        departure_stack[Current.name] = depart_option

        Current.prev_line = Next.trainLineName
        
        if Current.prev_line != Current.trainLineName and Current.prev_line!=0:
            if orientation_next==1:
                temp = reverseLine(Current.trainLineName)
                str_out.append(temp)
            else:str_out.append('Transfer to '+Current.trainLineName)

    # The first station you leave from
    start_sched= line_dict[route[0].trainLineName].stations_dict[route[0].name][orientation_current][schedule_index]
    leave_time = findDeparture(start_sched,next_depart,'Departure')
    
    str_out.append('    '+route[0].name + ': '+str(leave_time))
    
    if orientation_current==1:
        temp = reverseLine(route[0].trainLineName)
        str_out.append(temp)
    else: str_out.append(route[0].trainLineName)
    
    departure_stack[route[0].name] = leave_time
    resetDirection(route)
    
    str_out.reverse()
    x = '\n\n'.join(str_out)
     
    return x

def departurePath(line_dict, route, start, schedule_index):
    str_out = '' 

    transferLog=[]
    for i in range(len(route)-1):
        # Current station
        Current = route[i]
        # Next station
        Next = route[i+1]   

        # The edge weight betweeen the stations
        COST = Current.find_Neighbour(Next.name).cost 
       
       # Direction along the map
        orientation = Current.find_Neighbour(Next.name).orientation 

        # If your orientation is NONE, look to the Next stations neighbour
        if orientation==None:   
            nextStation = Current.find_Neighbour(Next.name).destination
            nextNeighbour = nextStation.find_Neighbour(route[i+2].name)
            orientation = nextNeighbour.orientation

        if Current.order == 1:
                if Next.trainLineName == None: 
                    Next.prev_line = Current.trainLineName
                    
                else: 
                    pass
        elif Next.order == 1:
                if Current.prev_line != Next.trainLineName: 
                    COST += timedelta(minutes=5)
                    
                Current.trainLineName = Next.trainLineName
                
            
        elif Current.trainLineName == None:
            
            if Current.prev_line in Next.lines:
                transferLog.append(Current)
                Current.trainLineName=Current.prev_line
                Next.prev_line=Current.trainLineName
               
            else:
                com = commonLines(route[i:])
                depart_dict={}
               
                for k in com:
                    sched = line_dict[k].stations_dict[Current.name][orientation][schedule_index]
                    
                    depart_opt = findDeparture(sched,start,"Departure")
                    if depart_opt==None: 
                        continue
                    depart_dict[depart_opt]=k
                
                if depart_dict=={}: 
                    print('No Stop')
                    continue
                else:best_depart = min(depart_dict)
                LINE = depart_dict[best_depart]

                Current.trainLineName=LINE
                Next.prev_line = LINE

        #and Current.name == route[0].name:
        elif Current.trainLineName != None: 
            if Current.prev_line in Next.lines:
                transferLog.append(Current)
                Current.trainLineName=Current.prev_line
                Next.prev_line=Current.trainLineName
            if Current.trainLineName in Next.lines:
                Next.prev_line = Current.trainLineName

        if Current.name == 'BELLVILLE': 
            continue
        # The schedule of that trainline name
        AREA = line_dict[Current.trainLineName]      
        
        # The stations schedules
        current_schedule = AREA.stations_dict[Current.name] 

     # Finds the departure time of the current station given its schedule and time requested
        departure = findDeparture(current_schedule[orientation][schedule_index], start, 'Departure') 

        if i==0: 
            if orientation==1:
                temp = (Current.trainLineName).split(' - ')
                temp.reverse()
                temp=' - '.join(temp)
                str_out+= temp+'\n'

            else: str_out += Current.trainLineName+'\n'

        str_out += '    '+Current.name + ': '+ str(departure) +'\n\n'
        if Current.prev_line != Current.trainLineName and Current.prev_line!=0:
            if orientation==1:
                temp = (Current.trainLineName).split(' - ')
                temp.reverse()
                ' - '.join(temp)
                str_out+= 'Transfer to '+temp+'\n'
            else: str_out+= 'Transfer to '+Current.trainLineName+'\n'

        start = departure+COST

    str_out += '  Arrive in  '+route[-1].name + ': '+ str(start+route[-2].find_Neighbour(route[-1].name).cost)
    return str_out

# Finds which departure to take (many departures at different times) - HRDSOR001
def findDeparture(schedule, time, time_type, path_cost=None):
    if time_type == 'Arrival':
        bound = time                    
        if schedule==[]:return
        # Iterates through station times and selects based on Arrival or Departure
        try: 
            if bound < str_to_time(schedule[0]): 
                print('Earliest depart -', str_to_time(schedule[0]))
                return -1
        except:pass
        for i in range(len(schedule)):
            if bound > str_to_time(schedule[i]): continue
            elif bound==str_to_time(schedule[i]): return str_to_time(schedule[i])
            else: return str_to_time(schedule[i-1])
        return str_to_time(schedule[-1])
    else:
        try:
            for i in range(len(schedule)):
                if time > str_to_time(schedule[i]): continue
                elif time==str_to_time(schedule[i]): return str_to_time(schedule[i])
                else: return str_to_time(schedule[i])
        except:
            pass
            
# Returns station orientation - HRDSOR001
def getOrientation(Node):
    return Node.direction

def getOutput_shortest(start_dest, final_dest, turned_off = None, turned_off_line = None):  
    current_time = getCurrentTime()
    str_output = ''
    stations_array = []
    stations_dict = {}
    # Loads the nodes into the dictonary
    loadLines(stations_array, stations_dict)    
    
    graph = Graph(len(stations_array),stations_array, turned_off, turned_off_line, 0)
    graph.genMap() 
    if find_Station(start_dest,stations_array) == None:
        start_dest += ' D'
    if find_Station(final_dest, stations_array) == None:
        final_dest += ' A'
    arr_output = graph.getPath(stations_array[find_Station(start_dest,stations_array)],stations_array[find_Station(final_dest,stations_array)])
    arr_output.reverse()
    total_cost = timedelta(minutes=0)
    
    str_output+= ('Line: ' + arr_output[1].trainLineName + '\n')
    for i in range(len(arr_output)-1):
        trainLineName = arr_output[i+1].trainLineName
        if arr_output[i].find_Neighbour(arr_output[i+1].name).orientation == 0:
            temp = trainLineName.split(' - ')
            temp.reverse()
            trainLineName = ' - '.join(temp)
        
        if arr_output[i].trainLineName != arr_output[i+1].trainLineName:
            if i ==0: 
                continue
            str_output+=('\n*Transfer*\n')
            str_output+=(arr_output[i+1].trainLineName+'\n')
        
        str_output+= ('\n'+arr_output[i].name + ' to ' + arr_output[i+1].name)
        total_cost += arr_output[i].find_Neighbour(arr_output[i+1].name).cost
        if total_cost > str_to_time('23:59'):
            print('Apologies, this trip is not possible due to complications at '+ arr_output[i].name + ' station.')
            return

    return arr_output

    ### Make Schedule - Functions ###

# Cleans the input to return a station name with corresponding schedule - HRDSOR001
def timeFilter(line):
    pivot = line.index(':')-2
    times = line[pivot:].split(' ')
    times = [i for i in times if ':' in i]

    station = line[:pivot].strip()
    try:    
        station = (station[:station.index('.')]).strip()
    except: 
        pass

    return [station, times]

#Filters for operating day - HRDSOR001
def operationDay(str_input):
    key = str_input.upper()
    if ('MONDAY' in key):      return 0
    if ('MON-FRI' in key):     return 0
    elif ('SATUR' in key):     return 1 
    elif ('SUNDAY' in key):     return 2

# Returns total fixed cost of Path - HRDSOR001
def totalCost(arr_output):
    edge_weights = []
    total_cost = timedelta(minutes=0)
    for i in range(len(arr_output)-1):   
        edge_cost = arr_output[i].find_Neighbour(arr_output[i+1].name).cost
        total_cost += edge_cost 
        edge_weights.append(edge_cost)

   
    return total_cost

# Returns the lines two stations have in common
def commonLines(arr_output):
    common = list(set(arr_output[0].lines).intersection(arr_output[1].lines))
    return common

# Returns the fasted route to take from transfer to destination - HRDSOR001
def getFastest(line_dict, route, input_time):
    route_cost = {}
    space = '   '
    cost_array, path_array, transferLog = [],[],[]
    common = commonLines(route)
    
    weight = 0
    track_time=input_time 
    cost = timedelta(minutes=0)

    #Check journey for each line option at a transfer point

    for lineName in common:
        route[0].trainLineName = lineName
    
        for station in range (len(route)-1):
            Current = route[station]
            Next = route[station+1]
            schedule_index = 0
            orientation = Current.find_Neighbour(Next.name).orientation
            
            if orientation==None:   # Finds orientation of the transfer station and selects correct schedule - HRDSOR001
                nextStation = Current.find_Neighbour(Next.name).destination
                nextNeighbour = nextStation.find_Neighbour(route[station+2].name)
                orientation = nextNeighbour.orientation
            
            #Saves orientations for the path
            Current.direction = orientation

            if Current.order == 1:
                if Next.trainLineName == None: 
                    Next.prev_line = Current.trainLineName
                    
                else: 
                    pass

            # Else if your next neighbour is a station, take its Trainline name. The elif assumes you are a transfer
            elif Next.order == 1:
                if Current.prev_line != Next.trainLineName: 
                    cost += timedelta(minutes=5)
                Current.trainLineName = Next.trainLineName
                
            
            elif Current.trainLineName == None:
              
                if Current.prev_line in Next.lines:
                    transferLog.append(Current)
                    Current.trainLineName=Current.prev_line
                    Next.prev_line=Current.trainLineName

                else: 
                    trainLineData = getOptimalLine(Next, orientation, schedule_index, line_dict, input_time)
                    Current.trainLineName = trainLineData[0]
                    Next.prev_line = Current.trainLineName
                    cost += timedelta(minutes=5)

            elif Current.trainLineName != None:
                if Current.prev_line in Next.lines:
                    transferLog.append(Current)
                    Current.trainLineName=Current.prev_line
                    Next.prev_line=Current.trainLineName
                if Current.trainLineName in Next.lines:
                    Next.prev_line = Current.trainLineName

            path_array.append(Current.trainLineName)
            weight = Current.find_Neighbour(Next.name).cost
            cost += weight
            track_time+=weight

            if Current.trainLineName!=Current.prev_line:
                if Current.prev_line != 0:
                    cost += timedelta(minutes=5)

        # Configures the orientation of the destination in case of an arrival search
        route[-1].direction = route[-2].direction

        transferLog  = resetStationMemory(transferLog)

        route_cost[cost] = path_array
       
        cost = timedelta(minutes=0)
        
        path_array = []
        track_time= input_time

    try:
        journey = min(route_cost)
       
    except:
        if route_cost == {}: 
            return('No time available')

    for i in range(len(route)-1): route[i].trainLineName=route_cost[journey][i]
    if route[-1].order > 1:
        if route[-1].trainLineName==None:
            route[-1].trainLineName=route[-2].trainLineName
   
    return route

# Determines the best route with lines to take
def calcRoute(line_dict,route,input_time):
    correct_route = []
    for i in range(len(route)):
        if route[i].order==1: 
            correct_route.append(route[i])
            continue
        else:
            #If a transfer appears, compute the rest of the trip using getFastest
            from_trans = getFastest(line_dict, route[i:],input_time)
            #Join the route of stations and transfers
            return correct_route+from_trans
    return correct_route

# Returns the best departure time and its trainline - HRDSOR001
def getOptimalLine(Next, orientation, schedule_index, line_dict, input_time, time_type=None):
    candidate_times = {}
    depart_time = input_time
   
    for i in Next.lines:
        schedule = line_dict[i].stations_dict[Next.name][orientation][schedule_index]
        departure = findDeparture(schedule, depart_time, time_type)
        if departure == None: 
            continue
        candidate_times[departure] = i
    
    m = min(candidate_times)
    return [candidate_times[m],m]

# Clears the memory of transfer stations -HRDSOR001
def resetStationMemory(transferLog=None):
    for i in transferLog:
        i.prev_line = None 
        i.trainLineName = None
    return []

# Clears the direction of each station changed
def resetDirection(route):
    for i in route: 
        i.direction=None

# Returns a string of the final journey to be displayed - HRDSOR001
def getOutput_schedule(TRAINLINES, start_dest, final_dest, operating_day, time_type, input_time, turned_off = None, turned_off_line = None):
    
    #TRAINLINES = dictFunction() 
    
    operating_day = operating_day.strip()
    time_type = time_type.strip()
    input_time = str_to_time(input_time.strip())
    orientation = None
    
    schedule_index = operationDay(operating_day)

    stations_array = TRAINLINES[1]
    stations_dict = TRAINLINES[2]
    line_dict = TRAINLINES[0]
    
    graph = Graph(len(stations_array),stations_array, turned_off, turned_off_line)
    graph.genMap()
    
    if find_Station(start_dest,stations_array) == None:
        start_dest += ' D'
    if find_Station(final_dest, stations_array) == None:
        final_dest += ' A'
    
    #Shortest Path - Returns -1 for an incorrect Station entry
    try:
        arr_output = graph.getPath(stations_array[find_Station(start_dest,stations_array)], stations_array[find_Station(final_dest,stations_array)])
        arr_output.reverse()
    except Exception as e:
        return -1

    #Iterate through shortest path to set the total cost - HRDSOR001
    total_cost = totalCost(arr_output)

    dest = arr_output[-1]
    dest_orientation = arr_output[-2].find_Neighbour(dest.name).orientation
    try:
        if time_type == 'Arrival':
            for i in range(len(arr_output)-1):
                Current = arr_output[i]
                Next = arr_output[i+1]
                orientation = Current.find_Neighbour(Next.name).orientation

                # Finds orientation of the transfer station and selects correct schedule - HRDSOR001
                if orientation==None:  
                    nextStation = Current.find_Neighbour(Next.name).destination
                    nextNeighbour = nextStation.find_Neighbour(arr_output[i+2].name)
                    orientation = nextNeighbour.orientation
                
                Current.direction = orientation
            
            new_path = calcRoute(line_dict,arr_output,input_time)        
            arrive_path = arrivalPath(line_dict, new_path, input_time, schedule_index)

            return arrive_path

        elif time_type == 'Departure':
            output = departurePath(line_dict, arr_output, input_time,schedule_index)
            return output
    except:
        message = 'Sorry, something went wrong. Try another route!'
        return message

# Sets up the map of stations to be searched - HRDSOR001
def calibrateStations(trainLine_dict, node_dict):
    for i in trainLine_dict:
        for j in trainLine_dict[i].stations_dict:
            # If station found, increases its order (number of trainlines)
            node_dict[j].order += 1 
            # Adds all trianlines of each station
            node_dict[j].lines.append(i)        
        for node in node_dict:
            #If station is a transfer, its default trainline is None
            if node_dict[node].order > 1:
                node_dict[node].trainLineName=None     

# Creates schedule data structre - HRDSOR001
def dictFunction():
    stations_array = []
    stations_dict = {}   

    # Loads the nodes into the dictonary and array
    loadLines(stations_array, stations_dict)    

    node_dict = {node.name:node for node in stations_array}

    stations_south = {(i):([[[],[],[]],[[],[],[]]]) for i in stations_dict}
    stations_north = {(i):([[[],[],[]],[[],[],[]]]) for i in stations_dict}
    stations_central = {(i):([[[],[],[]],[[],[],[]]]) for i in stations_dict}
    stations_flats = {(i):([[[],[],[]],[[],[],[]]]) for i in stations_dict}
    stations_monte = {(i):([[[],[],[]],[[],[],[]]]) for i in stations_dict}

    # Populates dict with specific schedule
    central_line = makeSchedule('./trainLines/chris_hani.txt', stations_central)
    south_line = makeSchedule('./trainLines/southern.txt',stations_south) 
    north_line = makeSchedule2('./trainLines/northern.txt',stations_north)
    flats_line = makeSchedule('./trainLines/cpt_retreat(via cape flats).txt',stations_flats)
    cpt_monte = makeSchedule('./trainLines/cpt_bellville_monte_vista.txt',stations_monte)
   
    #Loads trainline object with full dict
    AREA_SOUTH = TrainLine("CAPE TOWN - WYNBERG - SIMON`S TOWN", south_line) 
    AREA_FLATS = TrainLine('CAPE TOWN - RETREAT - VIA CAPE FLATS', flats_line)
    CPT_MONTE = TrainLine("CAPE TOWN - BELLVILLE - VIA MONTE VISTA", cpt_monte)
    AREA_NORTH = TrainLine('CAPE TOWN - BELLVILLE - WELLINGTON - STELLENBOSCH - STRAND', north_line)
    AREA_CENTRAL = TrainLine('CAPE TOWN - LANGA - LAVISTOWN - KAPTEINSKLIP - KHAYELITSHA - CHRIS HANI', central_line)

    trainLine_dict = {
            AREA_SOUTH.name:AREA_SOUTH,
            AREA_FLATS.name: AREA_FLATS,
            CPT_MONTE.name: CPT_MONTE,
            AREA_NORTH.name: AREA_NORTH,
            AREA_CENTRAL.name: AREA_CENTRAL,
        }

    calibrateStations(trainLine_dict, node_dict)
    
    return [trainLine_dict,stations_array, stations_dict]

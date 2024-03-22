from datetime import timedelta
from datetime import datetime
#Convert the pdf time syntax into timedelta object - WBK
def str_to_time(s_time):
    s_time = s_time.lstrip("0")
    posColon = s_time.index(':')
    hours = s_time[:posColon]
    minutes = s_time[posColon+1:]
    t_time = timedelta(hours=int(hours), minutes=int(minutes))
    return t_time

#Locate the index of a station is the node list given the name - WBK
def find_Station(name,stations_array):
    for x in stations_array:
        if x.name == name:
            return stations_array.index(x)

def getCurrentTime():
    current_time = timedelta(hours = datetime.now().time().hour, minutes = datetime.now().time().minute)
    return current_time
import sys

import arrow
import csv


class WeData:
    def __init__(self, data, index):
        self.data = data
        self.index = index


class oneWe:
    def __init__(self, all):
        self.all = all
        self.station = all[0]
        self.time = arrow.get(all[1], 'YYYY-MM-DD HH:mm')


class OneFlight:

    def __init__(self, orig, dest, depT, arrT, all, numDiv, divList):
        self.orig = orig
        self.dest = dest
        self.depT = depT
        self.arrT = arrT
        self.all = all
        self.useable = True;
        self.divs = divList
        self.numDiv = int(numDiv)


def formatDate(toForm):
    month = str(toForm.date().month)
    if month.__len__() < 2:
        month = '0' + month
    day = str(toForm.date().day)
    if day.__len__() < 2:
        day = '0' + day
    return 'weData/' + str(toForm.date().year) + month + day + '.txt'


def findData(place, inTime, allWe, timeIndex):
    min = inTime.time().hour * 60 + inTime.time().minute
    return recurData(min, allWe, timeIndex, 0, place)


def recurData(min, allWe, timeIndex, offset, place):
    try:
        index = timeIndex[min]
        while allWe[index].date().day == allWe[index - 1].date().day:
            if allWe[index].station == place:
                return allWe[index]
            index = index + 1
    except:
        return 0
    if min == 0:
        return 0
    if offset > 0:
        offset = offset * -1
    else:
        offset = offset * -1 + 1
    return (recurData(min + offset, allWe, timeIndex, place))


def toUTC(airport, time):
    file3 = open("AirportTZ.csv", 'r')
    csvreader3 = csv.reader(file3)
    tz = ''
    found = 0
    for pair in csvreader3:
        if airport == pair[0]:
            tz = pair[1]
            break
        ret = time
        ret = ret.replace(tzinfo=tz)
        ret = ret.to('utc')
    return ret


def getWeData(file, writer):
    try:
        file = open(file, 'r')
    except:
        print("DONE :)")
        quit()
    reader = csv.reader(file)
    reader.__next__()
    reader.__next__()
    reader.__next__()
    reader.__next__()
    reader.__next__()
    reader.__next__()
    allWe = []
    timeIndex = [0]
    new = oneWe(next(reader))
    allWe.append(new)
    i = 0
    for row in reader:
        new = oneWe(row)
        if new.time != allWe[allWe.__len__() - 1].time:
            timeIndex.append(i + 1)
        allWe.append(new)
        i = i + 1
    return WeData(allWe, timeIndex)


class OneFlight:

    def __init__(self, orig, dest, depT, arrT, all, numDiv, divList):
        self.orig = orig
        self.dest = dest
        self.depT = depT
        self.arrT = arrT
        self.all = all
        self.useable = True;
        self.divs = divList
        self.numDiv = int(numDiv)


class Diver:

    def __init__(self, port, arr, dep):
        self.port = port
        self.arr = arr
        self.dep = dep


file2 = open('Raw_Monthly_Data/' + sys.argv[1], 'r')
endfile = open(sys.argv[1][:-4]+'out.csv', 'w')
writer = csv.writer(endfile)

flights = []
csvreader2 = csv.reader(file2)
csvreader2.__next__()

done = False
its = 0
i = 0
if its < 1:
    if i < 5701:
        i = i + 1
        csvreader2.__next__()
i = 0
with endfile as file:
    for row in csvreader2:
        if row[118] != 'N':
            continue
        if i % 1000 == 0:
            print(i)
        try:
            deptime = row[38]
            arrtime = row[49]
            while deptime.__len__() != 4:
                deptime = '0' + deptime
            while arrtime.__len__() != 4:
                arrtime = '0' + arrtime
            sdep = row[5] + deptime
            sarr = row[5] + arrtime
            try:
                dep = arrow.get(sdep, 'YYYY-MM-DDhhmm')
            except:
                print(row[5], row[39], i)
                quit()
            try:
                arr = arrow.get(sarr, 'YYYY-MM-DDhhmm')
            except:
                print(row[5], row[50], i)
                quit()
            dep = toUTC(row[23], dep)
            arr = toUTC(row[32], arr)
            if (arr < dep):
                arr.shift(days=1)
            divList = []
            divnum = int(row[73])
            if divnum > 0:
                divport = row[78]
                divarr = row[81]
                divdep = row[84]
                while divarr.__len__() < 4:
                    divarr = '0' + deptime
                while divdep.__len__() < 4:
                    divdep = '0' + arrtime
                divarr = row[5] + divarr
                divdep = row[5] + divdep
                divarr = arrow.get(divarr, 'YYYY-MM-DDhhmm')
                divdep = arrow.get(divdep, 'YYYY-MM-DDhhmm')
                divarr = toUTC(divport, divarr)
                divdep = toUTC(divport, divdep)
                if (divarr < divdep):
                    divarr.shift(days=1)
                divList.append(Diver(divport, divarr, divdep))
                if divnum > 1:
                    divport = row[86]
                    divarr = row[89]
                    divdep = row[92]
                    while divarr.__len__() != 4:
                        divarr = '0' + deptime
                    while divdep.__len__() != 4:
                        divdep = '0' + arrtime
                    divarr = row[5] + divarr
                    divdep = row[5] + divdep
                    divarr = arrow.get(divarr, 'YYYY-MM-DDhhmm')
                    divdep = arrow.get(divdep, 'YYYY-MM-DDhhmm')
                    divarr = toUTC(divport, divarr)
                    divdep = toUTC(divport, divdep)
                    if (divarr < divdep):
                        divarr.shift(days=1)
                    divList.append(Diver(divport, divarr, divdep))
                    if divnum > 2:
                        divport = row[95]
                        divarr = row[97]
                        divdep = row[100]
                        while divarr.__len__() != 4:
                            divarr = '0' + deptime
                        while divdep.__len__() != 4:
                            divdep = '0' + arrtime
                        divarr = row[5] + divarr
                        divdep = row[5] + divdep
                        divarr = arrow.get(divarr, 'YYYY-MM-DDhhmm')
                        divdep = arrow.get(divdep, 'YYYY-MM-DDhhmm')
                        divarr = toUTC(divport, divarr)
                        divdep = toUTC(divport, divdep)
                        if (divarr < divdep):
                            divarr.shift(days=1)
                        divList.append(Diver(divport, divarr, divdep))
                        if divnum > 3:
                            divport = row[102]
                            divarr = row[105]
                            divdep = row[108]
                            while divarr.__len__() != 4:
                                divarr = '0' + deptime
                            while divdep.__len__() != 4:
                                divdep = '0' + arrtime
                            divarr = row[5] + divarr
                            divdep = row[5] + divdep
                            divarr = arrow.get(divarr, 'YYYY-MM-DDhhmm')
                            divdep = arrow.get(divdep, 'YYYY-MM-DDhhmm')
                            divarr = toUTC(divport, divarr)
                            divdep = toUTC(divport, divdep)
                            if (divarr < divdep):
                                divarr.shift(days=1)
                            divList.append(Diver(divport, divarr, divdep))
                            if divnum > 4:
                                divport = row[110]
                                divarr = row[113]
                                divdep = row[116]
                                while divarr.__len__() != 4:
                                    divarr = '0' + deptime
                                while divdep.__len__() != 4:
                                    divdep = '0' + arrtime
                                divarr = row[5] + divarr
                                divdep = row[5] + divdep
                                divarr = arrow.get(divarr, 'YYYY-MM-DDhhmm')
                                divdep = arrow.get(divdep, 'YYYY-MM-DDhhmm')
                                divarr = toUTC(divport, divarr)
                                divdep = toUTC(divport, divdep)
                                if (divarr < divdep):
                                    divarr.shift(days=1)
                                divList.append(Diver(divport, divarr, divdep))
            new = OneFlight(row[23], row[32], dep, arr, row, row[73], divList)
            depd = dep.format('YYYY-MM-DD')
            arrd = arr.format('YYYY-MM-DD')
            flights.append(new)
            i = i + 1
        except:
            continue

        print('done')
        #

        print('done')

        outHeader = ["Year", "Quarter", "Month", "DayofMonth", "DayOfWeek", "FlightDate", "Marketing_Airline_Network",
                     "Operated_or_Branded_Code_Share_Partners", "DOT_ID_Marketing_Airline",
                     "IATA_Code_Marketing_Airline",
                     "Flight_Number_Marketing_Airline", "Originally_Scheduled_Code_Share_Airline",
                     "DOT_ID_Originally_Scheduled_Code_Share_Airline",
                     "IATA_Code_Originally_Scheduled_Code_Share_Airline",
                     "Flight_Num_Originally_Scheduled_Code_Share_Airline", "Operating_Airline ",
                     "DOT_ID_Operating_Airline", "IATA_Code_Operating_Airline", "Tail_Number",
                     "Flight_Number_Operating_Airline", "OriginAirportID",
                     "OriginAirportSeqID", "OriginCityMarketID", "Origin", "OriginCityName", "OriginState",
                     "OriginStateFips", "OriginStateName", "OriginWac",
                     "DestAirportID", "DestAirportSeqID", "DestCityMarketID", "Dest", "DestCityName", "DestState",
                     "DestStateFips", "DestStateName", "DestWac",
                     "CRSDepTime", "DepTime", "DepDelay", "DepDelayMinutes", "DepDel15", "DepartureDelayGroups",
                     "DepTimeBlk", "TaxiOut", "WheelsOff", "WheelsOn",
                     "TaxiIn", "CRSArrTime", "ArrTime", "ArrDelay", "ArrDelayMinutes", "ArrDel15", "ArrivalDelayGroups",
                     "ArrTimeBlk", "Cancelled", "CancellationCode",
                     "Diverted", "CRSElapsedTime", "ActualElapsedTime", "AirTime", "Flights", "Distance",
                     "DistanceGroup", "CarrierDelay", "WeatherDelay", "NASDelay",
                     "SecurityDelay", "LateAircraftDelay", "FirstDepTime", "TotalAddGTime", "LongestAddGTime",
                     "DivAirportLandings", "DivReachedDest",
                     "DivActualElapsedTime", "DivArrDelay", "DivDistance", "Div1Airport", "Div1AirportID",
                     "Div1AirportSeqID", "Div1WheelsOn", "Div1TotalGTime",
                     "Div1LongestGTime", "Div1WheelsOff", "Div1TailNum", "Div2Airport", "Div2AirportID",
                     "Div2AirportSeqID", "Div2WheelsOn", "Div2TotalGTime",
                     "Div2LongestGTime", "Div2WheelsOff", "Div2TailNum", "Div3Airport", "Div3AirportID",
                     "Div3AirportSeqID", "Div3WheelsOn", "Div3TotalGTime",
                     "Div3LongestGTime", "Div3WheelsOff", "Div3TailNum", "Div4Airport", "Div4AirportID",
                     "Div4AirportSeqID", "Div4WheelsOn", "Div4TotalGTime",
                     "Div4LongestGTime", "Div4WheelsOff", "Div4TailNum", "Div5Airport", "Div5AirportID",
                     "Div5AirportSeqID", "Div5WheelsOn", "Div5TotalGTime",
                     "Div5LongestGTime", "Div5WheelsOff", "Div5TailNum", "Duplicate"]

        weHeader = ['station', 'valid', 'lon', 'lat', 'tmpf', 'dwpf', 'relh', 'drct', 'sknt', 'p01i',
                    'alti', 'mslp', 'vsby', 'gust', 'skyc1', 'skyc2', 'skyc3', 'skyc4', 'skyl1', 'skyl2',
                    'skyl3', 'skyl4', 'wxcodes', 'ice_accretion_1hr', 'ice_accretion_3hr',
                    'ice_accretion_6hr', 'peak_wind_gust', 'peak_wind_drct', 'peak_wind_time', 'feel',
                    'metar', 'snowdepth']

        arrhe = []
        dephe = []
        div1deph = []
        div1arrh = []
        div2deph = []
        div2arrh = []
        div3deph = []
        div3arrh = []
        div4deph = []
        div4arrh = []
        div5deph = []
        div5arrh = []
        for line in weHeader:
            arrhe.append('Arrival ' + line)
            dephe.append('Departure ' + line)
            div1arrh.append('Div 1 Arrival ' + line)
            div1deph.append('Div 1 Departure' + line)
            div2arrh.append('Div 2 Arrival ' + line)
            div2deph.append('Div 2 Departure' + line)
            div3arrh.append('Div 3 Arrival ' + line)
            div3deph.append('Div 3 Departure' + line)
            div4arrh.append('Div 4 Arrival ' + line)
            div4deph.append('Div 4 Departure' + line)
            div5arrh.append('Div 5 Arrival ' + line)
            div5deph.append('Div 5 Departure' + line)

        outHeader = outHeader + dephe + arrhe + div1arrh + div1deph + div2arrh + div2deph + div3arrh + div3deph + div4arrh + div4deph
        outHeader = outHeader + div5arrh + div5deph
        hi = 0
        count = 0

        print('part 2 with len', flights.__len__())
        if its == 0:
            writer.writerow(outHeader)
        w = 0
        today = flights[0].depT
        todayWeather = getWeData(formatDate(today), writer)
        tomorrow = today.shift(days=1)
        tomorrowWeather = getWeData(formatDate(tomorrow), writer)
        for flight in flights:
            if flight.useable:
                if w % 1000 == 0:
                    print(w)
                if flight.depT.date().day != today.date().day:
                    today = tomorrow
                    todayWeather = tomorrowWeather
                    tomorrow = today.shift(days=1)
                    tomorrowWeather = getWeData(formatDate(tomorrow), writer)
                depw = findData(flight.orig, flight.depT, todayWeather.data, todayWeather.index)
                if flight.arrT.date().day != today.date().day:
                    arrw = findData(flight.dest, flight.arrT, tomorrowWeather.data, tomorrowWeather.index)
                else:
                    arrw = findData(flight.dest, flight.arrT, todayWeather.data, todayWeather.index)
                if depw == 0 or arrw == 0:
                    w = w + 1
                    continue
                fullLine = flight.all + depw.all + arrw.all
                divloaded = 0

                while divloaded < flight.numDiv:
                    div = flight.divs[divloaded]
                    if div.arr.date().day != today.date().day:
                        divarrwe = findData(div.port, div.arr, tomorrowWeather.data, tomorrowWeather.index)
                    else:
                        divarrwe = findData(flight.port, div.arr, todayWeather.data, todayWeather.index)
                    if div.dep.date().day != today.date().day:
                        divdepwe = findData(div.port, div.dep, tomorrowWeather.data, tomorrowWeather.index)
                    else:
                        divdepwe = findData(flight.port, div.dep, todayWeather.data, todayWeather.index)
                    fullLine = fullLine + divarrwe.all + divdepwe.all
                    divloaded = divloaded + 1
                writer.writerow(fullLine)
                w = w + 1
        print('end of part 2')
    print(hi)
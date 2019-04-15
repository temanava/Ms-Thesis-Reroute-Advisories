# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 13:17:48 2019

@author: teman
"""

import csv
import pandas as pd
import time 
import os
start_time = time.time()
from datetime import datetime
date_format = "%Y-%m-%dT%H:%M:%SZ" 
import math
import numpy as np
import matplotlib.path as mpltPath
from math import sqrt,atan,pi,acos,cos, sin, tan
import pyproj
geod = pyproj.Geod(ellps='WGS84')
from bokeh.plotting import figure, output_file
from bokeh.io import show, curdoc
from bokeh.tile_providers import CARTODBPOSITRON
from bokeh.models import Title, Label
from bokeh.layouts import column, row

RADIUS = 6378137.0 # in meters on the equator
R = 6372.795477598  #mean quadratic radius

def lat2y(a):
  return math.log(math.tan(math.pi / 4 + math.radians(a) / 2)) * RADIUS

def lon2x(a):
  return math.radians(a) * RADIUS

def GPStoMercator(liste,outx,outy):
    for element in liste:
        if type(element) == str and element != ' ':
            outx.append(lon2x(float(element.split(' ')[1])))
            outy.append(lat2y(float(element.split(' ')[0])))
        elif type(element) == list:
            outx.append(lon2x(element[1]))
            outy.append(lat2y(element[0]))
            
def Routestrtofloat(route):
    liste = []
    for element in route:
        liste.append([float(element.split(' ')[0]),float(element.split(' ')[1])])
    return liste
            
def buildCircle(lat,lon,radius,N,circlePoints):
    for k in range(N):
        # compute
        angle = math.pi*2*k/N
        dx = radius*math.cos(angle)
        dy = radius*math.sin(angle)
        point = []
        point.append(lat + (180/math.pi)*(dy/6378137))
        point.append(lon + (180/math.pi)*(dx/6378137)/math.cos(lat*math.pi/180))
        # add to list
        circlePoints.append(point)
        
def buildCorridor(trajectory, width, height,polygon1,polygon2):
    rect_diag = sqrt( width**2 + height**2 )
    azimuth1 = atan(width/height)*180/pi
    azimuth2 = (atan(-width/height)+pi)*180/pi
    azimuth3 = (atan(width/height)+pi)*180/pi # first point + 180 degrees
    azimuth4 = atan(-width/height)*180/pi # second point + 180 degrees
    polygon3 = []
    for i in range (len(trajectory)-1):
        if trajectory[i] != trajectory[i+1]:
            center_lat1 = trajectory[i].split(' ')[0]
            center_lon1 = trajectory[i].split(' ')[1]
            center_lat2 = trajectory[i+1].split(' ')[0]
            center_lon2 = trajectory[i+1].split(' ')[1]
            if float(center_lat2) < float(center_lat1) and float(center_lon2)>float(center_lon1):
                angle = 180+atan((float(center_lon2)-float(center_lon1))/(float(center_lat2) - float(center_lat1)))*180/pi            
            elif float(center_lon2) < float(center_lon1) and float(center_lat2) < float(center_lat1):
                angle = 180+atan((float(center_lon2)-float(center_lon1))/(float(center_lat2) - float(center_lat1)))*180/pi
            else:
                angle = atan((float(center_lon2)-float(center_lon1))/(float(center_lat2) - float(center_lat1)))*180/pi
            #print(angle)
            pt1_lon, pt1_lat, _ = geod.fwd(center_lon1, center_lat1, azimuth1+angle, rect_diag)
            pt2_lon, pt2_lat, _ = geod.fwd(center_lon1, center_lat1, azimuth2+angle, rect_diag)
            pt3_lon, pt3_lat, _ = geod.fwd(center_lon1, center_lat1, azimuth3+angle, rect_diag)
            pt4_lon, pt4_lat, _ = geod.fwd(center_lon1, center_lat1, azimuth4+angle, rect_diag)
            polygon1.append([pt2_lat, pt2_lon])
            polygon1.append([pt1_lat, pt1_lon])
            polygon3 = [[pt4_lat, pt4_lon]]+[[pt3_lat, pt3_lon]]+polygon3
    for element in polygon3:
        polygon2.append(element)

def distanceGPS(traj2): #calculate the distance of a trajectory in km
    total = 0
    if len(traj2) > 1:
        for i in range(len(traj2)-1):
            lata = float(traj2[i].split(' ')[0])*pi/180
            lona = float(traj2[i].split(' ')[1])*pi/180
            latb = float(traj2[i+1].split(' ')[0])*pi/180
            lonb = float(traj2[i+1].split(' ')[1])*pi/180
            try:
                dist = R*acos(sin(lata)*sin(latb)+cos(lata)*cos(latb)*cos(lona-lonb))
            except ValueError:
                dist = 0
            total = total+dist
    return total

def bubbleSort2(alist,metric):
    liste = alist
    for passnum in range(len(liste)-1,0,-1):
        for i in range(passnum):
            if liste[i][metric]<liste[i+1][metric]:
                temp = liste[i]
                liste[i] = liste[i+1]
                liste[i+1] = temp
    return liste

def bubbleSortAllMetrics(alist):
    liste = alist
    for passnum in range(len(liste)-1,0,-1):
        for i in range(passnum):
            metric = liste[i][8]*liste[i][9]*liste[i][10]
            metric2 = liste[i+1][8]*liste[i+1][9]*liste[i+1][10]
            if metric < metric2:
                temp = liste[i]
                liste[i] = liste[i+1]
                liste[i+1] = temp
    return liste

## Files from FAA have all flights affected by reroutes during all month, flights are not ordered day per day, everything is mixed
# There is a need to analyse all month in once 
MonthInput = '03'
outputFolder = 'C:\\Users\\teman\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\Route Comparison\\Results\\Results_2017'+MonthInput+'\\'
#### Open file fro m FAA containing reroutes and affected flights #############################    
path = 'C:\\Users\\teman\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\FilesToFAA\\Files From FAA\\within_tracks_2017'    

flights = pd.read_csv(path+MonthInput+'_reduced.csv')

polygons = [] ## this last will gather all reroute polygons. Made of sublist for each day of the month with reroutes. Each sublist is made of lists of polygons
circles = [] #gather all circles around fixes of reroutes. Made of sublist for each day of the month with reroutes Each sublist is made of lists of lists of circle coordinates
LengthReroute = [] ##This list has the same format than polygons. Each sublist is made of distances of each reroute
header = ['Flight ID', 'Reroute Number', 'Start Date', 'End Date', 'Origin', 'Destination', 'Departure Time', 'Arrival Time','Route','PosIN/TotPos','DistIN/DistFlight','DistIN/DistReroute','Ratio Circles','ValidatedCircles','Flight Coordinates']
final = [] ##This list will gather all flights. Made of sublists for each day. Each sublist made of flights lists.
metricdist = [] ## Same format than final. Used to calculate the distance run by flight within the polygon. Made of lists of sequence of positions run in the polygon in a row
NonSenseReroute = [] ## Gather all reroutes that should not be treated because origin and destination are very close, e.g. EWR to JFK.
folder = 'C:\\Users\\teman\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\TFMS\\Results\\With Coordinates\\TFMS_FLOW_2017'+MonthInput+'\\With Updates'
for title in os.listdir(folder):
    final.append([[title[16:18],0]])
    metricdist.append([[int(title[16:18]),0]])
    NonSenseReroute.append([[title[16:18],0]])
    print(title)
    polygons.append([])
    circles.append([])
    LengthReroute.append([])
    with open(folder+'\\'+title, 'r') as f:
        reader = csv.reader(f)
        reroutes = list(reader) 
    f.close()
    for item in reroutes[1:]:
        traj = item[9:]
        LengthReroute[-1].append([item[6], item[7],distanceGPS(traj)])
        if distanceGPS(traj) > 5*distanceGPS([item[9],item[-1]]):
            NonSenseReroute[-1].append([reroutes.index(item),item[2],item[3],item[6],item[7],item[8]])
        polygon1 = []
        polygon2 = []
        #try:
        buildCorridor(traj, 20000 ,1000,polygon1,polygon2)
    #buildCorridor(traj[int(len(traj)/4)-1:int(3*len(traj)/4)+1], 15000,1000,polygon1,polygon2)
        corridor = polygon1+[[float(traj[-1].split()[0]),float(traj[-1].split()[1])]]+polygon2
        corridor.insert(0,[item[6], item[7], item[2],item[3]])
        #corridor = polygon1+polygon2
        polygons[-1].append(corridor)
        circles[-1].append([])
        for item2 in traj[1:-1]: ## first element of traj is original airport, last element is destination airport. We don't need those circles that are always validated
        #for item2 in traj[int(len(traj)/4)-1:int(3*len(traj)/4)]:
            circlepoints = []
            buildCircle(float(item2.split(' ')[0]),float(item2.split(' ')[1]),20000,15,circlepoints)
            circles[-1][-1].append(circlepoints)
        #except ZeroDivisionError:
           # pass

print('Files are read',"--- %s seconds ---" % (time.time() - start_time)) 

flights2 = flights.groupby(['callsign','Reroute Number','Start Time', 'End Time'])

print('Flights are grouped by Id and Reroute#',"--- %s seconds ---" % (time.time() - start_time))
      
skipped = []
for name,group in flights2:   
#    print(name)
    index = int(name[1].replace('REROUTE_',''))
    index2 = 100
    day = group.iloc[0,1][8:10]
    day2 = group.iloc[0,2][8:10]
    departureTime = group.iloc[0,8].split(' ')[0]+'T'+group.iloc[0,8].split(' ')[1]+'Z'
    arrivalTime = group.iloc[-1,8].split(' ')[0]+'T'+group.iloc[-1,8].split(' ')[1]+'Z'
    for i in range (len(final)):
        try:
            if day == final[i][0][0] and group.iloc[0,3] == polygons[i][index-1][0][0] and group.iloc[0,4] == polygons[i][index-1][0][1]:         
                index2 = i
                break
            elif day2 == final[i][0][0] and group.iloc[0,3] == polygons[i][index-1][0][0] and group.iloc[0,4] == polygons[i][index-1][0][1]:
                index2 = i
        except:
            pass
#    if day == '02' and day2 == '02':
#        if group.iloc[0,3] == polygons[0][index-1][0][0] and group.iloc[0,4] == polygons[0][index-1][0][1]:
#            index2 = 0
    if index2 != 100:
        starttime = datetime.strptime(polygons[index2][index-1][0][2], date_format)
        endtime = datetime.strptime(polygons[index2][index-1][0][3], date_format)
        if endtime > starttime:
            if any(index == NonSenseReroute[index2][i][0] for i in range (len(NonSenseReroute[index2]))) == False:
                final[index2].append([name[0],name[1],polygons[index2][index-1][0][2],polygons[index2][index-1][0][3],group.iloc[0,3],group.iloc[0,4],departureTime,arrivalTime,group.iloc[0,5],0,0,0,0,[]])
                metricdist[index2].append([name[0],name[1], []])
                corridor = polygons[index2][index-1][1:]
                bbPath = mpltPath.Path(np.asarray(corridor))
                circlereroute = circles[index2][index-1]
                for i in range (len(group)):
                    final[index2][-1].append(str(group.iloc[i,10])+' '+str(group.iloc[i,11]))
                    if bbPath.contains_point((group.iloc[i,10], group.iloc[i,11])) == True:
                        metricdist[index2][-1][-1].append(str(group.iloc[i,10])+' '+str(group.iloc[i,11]))
                        final[index2][-1][9] = (final[index2][-1][9]*(len(final[index2][-1][14:])-1)+1)/len(final[index2][-1][14:])
                        for k in range (len(circlereroute)):
                            bbPath2 = mpltPath.Path(np.asarray(circlereroute[k]))
                            if bbPath2.contains_point((group.iloc[i,10], group.iloc[i,11])) == True:
                                if k not in final[index2][-1][13]:
                                    final[index2][-1][13].append(k)
                        final[index2][-1][12] = len(final[index2][-1][13])/len(circlereroute)
                    else:
                        if metricdist[index2][-1][-1] != []:
                            metricdist[index2][-1].append([])
                        final[index2][-1][9] = (final[index2][-1][9]*(len(final[index2][-1][14:])-1))/len(final[index2][-1][14:])
                        for k in range (len(circlereroute)):
                            bbPath2 = mpltPath.Path(np.asarray(circlereroute[k]))
                            if bbPath2.contains_point((group.iloc[i,10], group.iloc[i,11])) == True:
                                if k not in final[index2][-1][13]:
                                    final[index2][-1][13].append(k)
                        final[index2][-1][12] = len(final[index2][-1][13])/len(circlereroute)
    else:
        skipped.append([name[0],name[1],group.iloc[0,1],group.iloc[0,2],group.iloc[0,3],group.iloc[0,4],departureTime,arrivalTime,group.iloc[0,5],0,0,0,0,[]])

print('First list is computed and two metrics are calculated out of four',"--- %s seconds ---" % (time.time() - start_time))
#             
final2 = []## final2 do not separate flights per day. Take all flights for one month together
for k in range (len(final)):
    print(k)
    for j in range (1,len(final[k])):
        departureTime = datetime.strptime(final[k][j][6], date_format)    
        arrivalTime = datetime.strptime(final[k][j][7], date_format) 
        startTime = datetime.strptime(final[k][j][2], date_format)
        endTime = datetime.strptime(final[k][j][3], date_format)
        if (departureTime > endTime) or (arrivalTime < startTime): #if the flight lands before start time of the reroute or takes-off after end time of the reroute, it is not treated
            pass
        else:
            index = int(final[k][j][1].replace('REROUTE_',''))
            distinpoly = 0
            for i in range (2,len(metricdist[k][j])):
                distinpoly = distinpoly+distanceGPS(metricdist[k][j][i])
            final[k][j][10] = distinpoly/distanceGPS(final[k][j][14:]) ### ratio = (distance of flight trajectory within polygon)/(distance of the flight trajectory)
            final[k][j][11] = distinpoly/LengthReroute[k][index-1][2]### ratio = (distance of flight trajectory within polygon)/(total distance of the reroute)
            final2.append(final[k][j])
final2 = bubbleSort2(final2,10)
#    final2[-1] = bubbleSortAllMetrics(final[k][1:])
    
##Next steps are used to remove duplicates cause most of the time same reroutes and same flights appear on two days in a row

header = ['Flight ID', 'Reroute Number', 'Start Date', 'End Date', 'Origin', 'Destination', 'Departure Time', 'Arrival Time','Route','PosIN/TotPos','DistIN/DistFlight','DistIN/DistReroute','Ratio Circles','ValidatedCircles','Flight Coordinates']
#file_sorted.insert(0, header)
df = pd.DataFrame(final2) #convert the list of list to a panda DataFrame
myList = list(df.columns) #next three lines to modify names of 14 first columns
myList[:15] = header
df.columns = myList

df = df.drop_duplicates(subset = ['Flight ID']+df.columns[2:12].tolist()+df.columns[14:30].tolist(),keep='first') #remove duplicate rows based on all columns but the reroute number one

#df = df[~df.iloc[:,2:].duplicated()] #another way of doing it

df.to_csv(outputFolder+'Comparison_2017'+MonthInput+'.csv', sep=',', encoding='utf-8', index = False)

               
print('New comparison file is written',"--- %s minutes ---" % ((time.time() - start_time)/60))      
#   

## VISUALIZATION ###################################

line = 923
percentage = '05'
figures = []  ## store each figure to show it in rows at the end 
for k in range(line-1,line+5):
    routeSelected = df.iloc[k,:].values.tolist()
    index = int(routeSelected[1].replace('REROUTE_',''))
    XMercator = []
    YMercator = []
    GPStoMercator(routeSelected[14:],XMercator,YMercator)
    day = routeSelected[2][8:10]
    day2 = routeSelected[3][8:10]
    for i in range (len(final)):
        if day == final[i][0][0] and routeSelected[4] == polygons[i][index-1][0][0] and routeSelected[5] == polygons[i][index-1][0][1]:         
            index2 = i
            break
        elif day2 == final[i][0][0] and routeSelected[4] == polygons[i][index-1][0][0] and routeSelected[5] == polygons[i][index-1][0][1]:
            index2 = i    
    #corridor = Routestrtofloat(reroutes[index][6:])
    corridor = polygons[index2][index-1][1:]
    x1 = []
    y1 = []
    GPStoMercator(corridor,x1,y1)
    #corridor = reroutes[index][6:]
    #polygon = np.asarray(corridor)
    
    circlesrer = circles[index2][index-1]
    Xcircles = []
    Ycircles = []
    for element in circlesrer:
        Xcircles.append([])
        Ycircles.append([])
        GPStoMercator(element,Xcircles[-1],Ycircles[-1])
        
    colors = ['green', 'indigo', 'red','black', 'cyan','teal', 'gold', 'darkcyan','mediumpurple']
#    output_file(outputFolder+'Flight_'+routeSelected[0]+'_'+routeSelected[1]+'.html')
    #output_file("map_reroute_polygon.html")
    # range bounds supplied in web mercator coordinates
    
    p = figure(tools="pan,box_zoom,wheel_zoom,reset",x_range=(-13000000, -7000000), y_range=(3000000, 5000000),x_axis_type="mercator", y_axis_type="mercator")
    p.add_layout(Title(text=routeSelected[1]+" : "+routeSelected[4]+" to "+routeSelected[5], align="center"), "below")
    p.add_layout(Title(text="Effective period: "+ routeSelected[2] +" to "+ routeSelected[3], align="center"), "below")
    p.add_layout(Title(text="Departure Time: "+ routeSelected[6] +"; Arrival Time: "+ routeSelected[7], align="center"), "below")
    p.add_layout(Title(text="Metric 1 = Number of positions in the polygon / Total number of positions = "+str(routeSelected[9])[0:5], align="center"), "below")
    p.add_layout(Title(text="Metric 2 = distance run by plane within the polygon / total distance run by the plane = "+str(routeSelected[10])[0:5], align="center"), "below")
    p.add_layout(Title(text="Metric 3 = distance run by plane within the polygon / total distance of the reroute = "+str(routeSelected[11])[0:5], align="center"), "below")    
    p.add_layout(Title(text="Metric 4 = Number of circles 'validated' / Total number of circles ="+str(routeSelected[12])[0:5], align="center"), "below")
    p.line(x1, y1, legend="Polygon "+polygons[index2][index-1][0][0]+" to "+polygons[index2][index-1][0][1], line_color="orange", line_dash="4 4")
    for j in range (len(Xcircles)):
        p.circle(Xcircles[j],Ycircles[j],legend="Circles Fixes/Navaids",size = 1, color = 'red')


    p.circle(XMercator,YMercator,legend=routeSelected[0],size = 1, color = colors[0])
        

    p.add_tile(CARTODBPOSITRON)
    figures.append(p)
    #curdoc().add_root(p)
    #show(p)
    
#put the results in a row
output_file(outputFolder+percentage+'%_Compliance_Visualization_2017'+MonthInput+'.html')    
show(row(figures[0],figures[1],figures[2],figures[3],figures[4],figures[5]))
print('Algorithm done',"--- %s minutes ---" % ((time.time() - start_time)/60))   
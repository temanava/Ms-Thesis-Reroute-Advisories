# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 10:20:08 2018

@author: Ghislain Dard
"""
import csv
import numpy as np
import os
import time 

import math

import matplotlib.path as mpltPath
from math import sqrt,atan,pi
import pyproj
geod = pyproj.Geod(ellps='WGS84')


RADIUS = 6378137.0

pathFixNavAir = 'C:\\Users\\gdard3\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\Fixes, Navaids, airports\\subsc_27_Apr_2017_effdate'
pathTFMS = 'C:\\Users\\gdard3\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\TFMS\\Results\\TFMS_FLOW_201704\\'
Day = 'TFMS_FLOW_20170430'
pathResultCoord = 'C:\\Users\\gdard3\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\TFMS\\Results\\With Coordinates\\TFMS_FLOW_201704\\With Updates\\'
pathResultFAA = 'C:\\Users\\teman\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\FilesToFAA\\ReroutesPolygon_201704\\'

def DateFormat(date):
    return(date[0:4]+date[5:7]+date[8:])

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
            
def buildCorridor(trajectory, width, height,polygon1,polygon2):
    rect_diag = sqrt( width**2 + height**2 )
    azimuth1 = atan(width/height)*180/pi
    azimuth2 = (atan(-width/height)+pi)*180/pi
    azimuth3 = (atan(width/height)+pi)*180/pi # first point + 180 degrees
    azimuth4 = atan(-width/height)*180/pi # second point + 180 degrees
    polygon3 = []
    for i in range (len(trajectory)-1):
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

start_time = time.time()  

######### Extract positions of all fixes and store them into a list CSVfix ######################## 
filename = pathFixNavAir +'\\FIX.txt'
src = open(filename, "r")
CSVfix = [['FIX','Latitude','Longitude']]
for line in src:
    if 'FIX1' in line:
        CSVfix.append([])
        line1 = line.rsplit()
        c = 0
        for i in range (len(line1)):
            if '-' in line1[i] and '.' in line1[i] and c==0:
#                latitude = line1[i][-13:]
#                orlat = latitude[-1]
#                latitude = latitude.replace('-','')[:-5]+orlat
#                longitude = line1[i+1][:14]
#                orlon = longitude[-1]
#                longitude = longitude.replace('-','')[:-5]+orlon
                latitude = line1[i][-13:]
                orlat = latitude[-1]
                split = latitude.split('.')
                split = split[0].split('-')
                if orlat == 'N':
                    latitude = float(split[0])+float(split[1])/60+float(split[2])/3600
                elif orlat == 'S':
                    latitude = -(float(split[0])+float(split[1])/60+float(split[2])/3600)
                longitude = line1[i+1][:14]
                orlon = longitude[-1]
                split = longitude.split('.')
                split = split[0].split('-')
                if orlon == 'W':
                    longitude = -(float(split[0])+float(split[1])/60+float(split[2])/3600)
                elif orlon == 'E':
                    longitude = float(split[0])+float(split[1])/60+float(split[2])/3600
                c=c+1
        CSVfix[-1].append(line[4:9])
        CSVfix[-1].append(latitude)
        CSVfix[-1].append(longitude)
src.close()
CSVfix = np.asarray(CSVfix) ## conveart list of lists to a matrix
print('Done with Fixes')
############# Extract positions of all Navaids and store them into a list CSVnav ######################## 
filename = pathFixNavAir +'\\NAV.txt'
src = open(filename, "r")
CSVnav = [['Navaid','Latitude','Longitude']]
for line in src:
    if 'NAV1' in line:
        CSVnav.append([])
        line1 = line.rsplit()
        c = 0
        for i in range (len(line1)):
            if '-' in line1[i] and '.' in line1[i] and c == 0:
                latitude = line1[i]
                orlat = latitude[-1]
                split = latitude.split('.')
                split = split[0].split('-')
                if orlat == 'N':
                    latitude = float(split[0])+float(split[1])/60+float(split[2])/3600
                elif orlat == 'S':
                    latitude = -(float(split[0])+float(split[1])/60+float(split[2])/3600)
                longitude = line1[i+1][11:25]
                orlon = longitude[-1]
                split = longitude.split('.')
                split = split[0].split('-')
                if orlon == 'W':
                    longitude = -(float(split[0])+float(split[1])/60+float(split[2])/3600)
                elif orlon == 'E':
                    longitude = float(split[0])+float(split[1])/60+float(split[2])/3600
                c=c+1
        CSVnav[-1].append(line1[0][4:])
        CSVnav[-1].append(latitude)
        CSVnav[-1].append(longitude)    
src.close()
CSVnav = np.asarray(CSVnav) ## convert list of lists to a matrix
print('Done with Navaids')
################# Extract positions of all airports and store them into a list CSVair ##########################
filename = pathFixNavAir+ '\\WorldAirportsDatabase.txt'
CSVairp = [['Airport','Latitude','Longitude']]
src = open(filename,'r',encoding="utf8")
for row in src:
 #       print(row)
     CSVairp.append([row.split(',')[5][1:-1],row.split(',')[6],row.split(',')[7]])
CSVairp = np.asarray(CSVairp)
        
        



################# Import csv file extracted from TFMS with all reroutes ###############
filename = pathTFMS + Day + '_withUpdates.csv'
with open(filename, 'r') as f:
    reader = csv.reader(f)
    file = list(reader)

final = []
c2 = 0
for element in file:
#    if element != []:
#        if element[-1]=='': # for the origin routes
    route = element[-1].split()
    orig = 'K'+element[-3]
    dest = 'K'+element[-2]
    c = 0
    if orig == 'KUNKNTHROUGH':
        c=1
    if dest == 'KUNKN':
        c=1
    #print(c)
    if c == 0:
        final.append(element)
        if orig in CSVairp[1:,0]:
            ind3 = np.where(CSVairp == orig)[0][0]
            final[-1].append(CSVairp[ind3,1] + ' ' + CSVairp[ind3,2])
            c2+=1
        for element2 in route:
            if (len(element2)==5) and (element2 in CSVfix[1:,0]):
                ind = np.where(CSVfix == element2)[0][0]
                final[-1].append(CSVfix[ind,1] + ' ' + CSVfix[ind,2])
                c2+=1
            elif (len(element2) ==3) and (element2 in CSVnav[1:,0]):
                ind = np.where(CSVnav == element2)[0][0]
                final[-1].append(CSVnav[ind,1] + ' ' + CSVnav[ind,2])  
                c2+=1
            elif len(element2) == 6: ###last fix is always on the format 'CAYSL4' for example where 4 deals with the arrival runway
                if element2[:-1] in CSVfix[1:,0]:
                    ind = np.where(CSVfix == element2[:-1])[0][0]
                    final[-1].append(CSVfix[ind,1] + ' ' + CSVfix[ind,2])
                    c2+=1
                elif element2[:-1] in CSVnav[1:,0]:
                    ind = np.where(CSVnav == element2[:-1])[0][0]
                    final[-1].append(CSVnav[ind,1] + ' ' + CSVnav[ind,2])  
                    c2+=1
        if dest in CSVairp[1:,0]:
            ind2 = np.where(CSVairp == dest)[0][0]
            final[-1].append(CSVairp[ind2,1] + ' ' + CSVairp[ind2,2])
            c2+=1

#

name = os.path.basename(filename)
me = name.split('.')
outputFile = pathResultCoord + me[0] +'_withCoord.csv'            
#
if c2 != 0:
    fh_data = open(outputFile,'w', newline='')        
    writer = csv.writer(fh_data) #write the output file 
    writer.writerows(final) 
    fh_data.close()
    print('Writing CSV with coordinates done', "--- %s seconds---" % (time.time()- start_time))

#
################### This part is the code for the file we are sending to FAA with the polygon for each reroute #################
#
##finalCSV = [['Reroute Number', 'Start Time', 'End Time', 'Origin', 'Destination','Reroute','Polygon' ]]
##c = 1
##for element in file[1:]:
##    d = 0
##    if element[-3] == 'UNKNTHROUGH':
##        d = 1
##    elif element[-2] == 'UNKN':
##        d = 1
##    elif d == 0:
##        finalCSV.append([])
##        polygon1 = []
##        polygon2 = []
##        buildCorridor(element[9:], 15000,1000,polygon1,polygon2)
##        corridor = polygon1+[[float(element[-1].split()[0]),float(element[-1].split()[1])]]+polygon2
##        finalCSV[-1]=['REROUTE_'+str(c),DateFormat(element[2]),DateFormat(element[3]),element[6],element[7],element[8]]
##        c=c+1
##        for element2 in corridor:
##            finalCSV[-1].append(str(element2[0])+' '+str(element2[1]))
##            
##if len(finalCSV)>1:    
##    outputFile2 = pathResultFAA + 'ReroutesPolygon_' + Day[-8:]+'.csv'
##    fh_data2 = open(outputFile2,'w', newline='')        
##    writer = csv.writer(fh_data2) #write the output file 
##    writer.writerows(finalCSV) #each row of the CSV is one list of myData
##    fh_data2.close()
##    print('build CSV for FAA done')
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 09:49:53 2019

@author: Ghislain Dard
"""

import pandas as pd
import random
import numpy as np


reroutes = pd.read_csv('VolumeAdvisories.csv') #Import reroute advisories
artcc = ['ZMP','ZMA','ZTL','ZAB','ZAU','ZBW','ZDC','ZDV','ZFW','ZHU','ZID','ZJX','ZKC','ZLA','ZLC','ZME','ZNY','ZOA','ZOB','ZSE']
artcc2 = ['ZMA','ZTL','ZAU','ZBW','ZDC','ZDV','ZFW','ZHU','ZID','ZJX','ZKC','ZME','ZNY','ZOB']
distrib = [0.054,0.047,0.040,0.033,0.026,0.019,0.012,0.012,0.012,0.012,0.012,0.023,0.033,0.044,0.055,0.065,0.065,0.065,0.065,0.065,0.065,0.065,0.059,0.052]
## distrib is the distribution of daily traffic count per hour 
traffic2 = []
count = pd.read_csv('Traffic_count.csv')#Import daily traffic count per facility
count = count.dropna()
count = count.reset_index(drop=True)
for i in range (1,5): ##create hourly traffic count per facility based on hourly distribution
    if i in [1,3]:
        for k in range (1,32):
            for j in range (24):
                for element in artcc:
                    ind = count.loc[(count['Date'] == str(i)+'/'+str(k)+'/2017') & (count["Facility"] == element)].index[0]                 
                    nb = count.iloc[ind, 4]
                    traffic2.append([i,k,j,element,round(distrib[j]*nb)])
                        
    elif i == 2:
        for k in range (1,29):
            for j in range (24):
                for element in artcc:
                    ind = count.loc[(count['Date'] == str(i)+'/'+str(k)+'/2017') & (count["Facility"] == element)].index[0]                 
                    nb = count.iloc[ind, 4]
                    traffic2.append([i,k,j,element,round(distrib[j]*nb)])
    elif i == 4:
        for k in range (1,31):
            for j in range (24):
                for element in artcc:
                    ind = count.loc[(count['Date'] == str(i)+'/'+str(k)+'/2017') & (count["Facility"] == element)].index[0]                 
                    nb = count.iloc[ind, 4]
                    traffic2.append([i,k,j,element,round(distrib[j]*nb)])
                    
                    
###Inset the issuance of reroute 
traffic2 = pd.DataFrame(traffic2, columns = ['Month', 'Day','Hour','ARTCC','Traffic Count'])
reroutes2 = ['no']* len(traffic2)            

for i,row in enumerate(reroutes.values):
    month = int(row[3][5:7])
    month2 = int(row[4][5:7])
    day = int(row[3][8:10])
    day2 = int(row[4][8:10])
    hour1 = int(row[3][11:13])
    hour2 = int(row[4][11:13])
    if row[6] in artcc:
        constrained = [row[6]]
    elif row[6] in ['JFK', 'ZWY']:
        constrained = ['ZNY']
    elif '/' in row[6]:
        constrained = []
        for element in row[6].split('/'):
            if element in artcc:
                constrained.append(element)
            elif element in ['JFK', 'ZWY']:
                constrained.append('ZNY')
    elif (row[6] == 'EASTCOAST') or (row[6] == 'EAST COAST'):
        constrained = ['ZMA', 'ZJX', 'ZDC', 'ZNY', 'ZBW']
    else:
        constrained = []
        for element in row[6].split(' '):
            if element in artcc:
                constrained.append(element)
            elif element in ['JFK', 'ZWY']:
                constrained.append('ZNY')
    if len(constrained) > 0:
        if day == day2:
            for j in range (hour1,hour2+1):
                for item in constrained:
                    ind = traffic2.loc[(traffic2['Month'] == month) & (traffic2['Day'] == day) & (traffic2['Hour'] == j) & (traffic2['ARTCC'] == item)].index
                    if len(ind) >=1:
                        index = ind[0]
                        reroutes2[index] = row[1]
        elif day2 > day:
            for j in range (hour1,24):
                for item in constrained:
                    ind = traffic2.loc[(traffic2['Month'] == month) & (traffic2['Day'] == day) & (traffic2['Hour'] == j) & (traffic2['ARTCC'] == item)].index
                    if len(ind) >=1:
                        index = ind[0]
                        reroutes2[index] = row[1]
            for j in range (0, hour2+1):
                for item in constrained:
                    ind = traffic2.loc[(traffic2['Month'] == month) & (traffic2['Day'] == day2) & (traffic2['Hour'] == j) & (traffic2['ARTCC'] == item)].index
                    if len(ind) >=1:
                        index = ind[0]
                        reroutes2[index] = row[1]
        elif month2 > month:
            for j in range (hour1,24):
                for item in constrained:
                    ind = traffic2.loc[(traffic2['Month'] == month) & (traffic2['Day'] == day) & (traffic2['Hour'] == j) & (traffic2['ARTCC'] == item)].index
                    if len(ind) >=1:
                        index = ind[0]
                        reroutes2[index] = row[1]
            for j in range (0, hour2+1):
                for item in constrained:
                    ind = traffic2.loc[(traffic2['Month'] == month2) & (traffic2['Day'] == day2) & (traffic2['Hour'] == j) & (traffic2['ARTCC'] == item)].index
                    if len(ind) >=1:
                        index = ind[0]
                        reroutes2[index] = row[1]
            
        
            

traffic2["Reroute"] = reroutes2

traffic2.to_csv('Traffic_and_reroutes_Logic.csv', sep=',', encoding='utf-8', index = False)
    
#            
#        
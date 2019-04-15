# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 10:32:19 2018

@author: Ghislain Dard 
"""

## This code allows the extraction of all TH messages for one day of data divided into hourly files.
import subprocess as sp
tmp = sp.call('cls',shell=True)

import csv
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import time
import ast
import os
#import re
start_time = time.time()

pathResult = 'C:\\Users\\gdard3\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\SFDPS\\Results\\'
path = 'D:\\Master Thesis\\Raw Data\\SFDPS\\'
Day = 'SFDPS_20181114_2'
folder = path + Day
Resultfolder = pathResult + Day[:-2]

counter = 0
error = []
CSV = []
CSV.append(['Msg Type', 'Flight ID', 'Origin', 'Departure Time', 'Destination', 'Arrival Time', 'Generation Time', 'Latitude', 'Longitude', 'Altitude'])
        

for title in os.listdir(folder):
    try:
        print('hour', counter)
################################Insert header and footer and remove xml tag###################################### 
        file1=os.path.join(folder,title)
        src = open(file1, "r")
        fline = "<root>\n"
        oline = src.readlines() # oline s a list where each element is a line of the input file 
        src.close()
        if oline[0] != '<root>\n':
            oline.insert(0, fline) #add <root> as header and footer is needed to parse the entire file with ET.parse()
            oline.append('</root>')
            for i in range (1, len(oline)):
                if '<?xml' in oline[i]: #this loop deletes the xml tags because only one is allowed to parse the file 
                    oline[i] = oline[i][:oline[i].index('<?xml')]
            print('remove xml tag done',"--- %s seconds ---" % (time.time() - start_time))
            src = open(file1, "w")
            src.writelines(oline) # rewrites the file with the new header and footer and without xml tags
            src.close()
            print('Rewriting done',"--- %s seconds ---" % (time.time() - start_time))
        del oline #delete the variable oline to spare memory
        
        
        
        print('step 1 done',"--- %s seconds ---" % (time.time() - start_time))
        
        ############################### PARSING step ##############################################
        A=[]
        B=[]
        C=[]
        ns = ["{org:mitre:swim:smes:v1-0}"] #name of the schema 
        for event, elem in ET.iterparse(file1, events=("start", "end")): #This loop parses the input file and stores the tags in list A, 
            #print(event)                                               #the attributes in B and the text in C
            if event == 'start':
                if elem.tag[0:26] in ns:
                    #print(elem.tag)
                    A.append(elem.tag[26:])
                    C.append(elem.text)
                    B.append(str(elem.attrib))
            elem.clear() 
            
            
        for i in range (0,len(C)): # this loop is just turning the blank fields of C into ''
            if C[i] != None:
                if '\n' in C[i]:
                    C[i] = ''
        
        want = list(zip(A, B,C)) #merge all 3 lists into one list of 3 elements 
        
        print('step 2 done', "--- %s seconds ---" % (time.time() - start_time))
        
        
        line=[]
        loc = [i for i,x in enumerate(A) if x=='flight'] # the tag 'flight' appears when w new message is starting 
        del A,B,C                                        # loc stores the positions of al'flight' tags so we have the starting point 
                                                         # of all messages  
         
        #################################### Sort according on MsgTypes #######################################
              
        WantedMsg = 'TH' # We want only the tracking messages 
        for i in range (len(loc)): #for each message we will read the msg type and add the message into the list line
            if ast.literal_eval(want[loc[i]][1]).get('source') == WantedMsg: #if it corresponds to WantedMsg
                line.append([])
                if i != len(loc)-1:
                    for j in range (loc[i], loc[i+1]-1):
                        line[-1].append(want[j])
                else:
                    for j in range(loc[i], len(want)):
                        line[-1].append(want[j])
                            
        del loc, want 
        # At the end of this step line is a list of lists. Each element of line is a list gathering tags, attributes and text of one entire message
        print('step 3 done', "--- %s seconds ---" % (time.time() - start_time))
           
        
        ################################ Creation of the final CSV ##############
        
        FlightAppear = [[0],[0]]
        for element in line: 
            indexpos = 0
            indexposition = 0
            for i in range (len(element)): #reading all line of the message and if the tags corresponds to an information we are interested in 
                if element[i][0] == 'flightIdentification': # we save the tag and its correspondings attributes and text into the CSV
                    dic = ast.literal_eval(element[i][1])
                    aircraftId = dic.get('aircraftIdentification')
                    if aircraftId not in FlightAppear[0]:
                        FlightAppear[0].append(aircraftId)
                        FlightAppear[1].append(1)
                    else:
                        index1 = FlightAppear[0].index(aircraftId)
                        FlightAppear[1][index1] += 1
                if element[i][0] == 'departure':
                    dic = ast.literal_eval(element[i][1])
                    Origin = dic.get('departurePoint')
                if element[i][0] == 'actual':
                    dic = ast.literal_eval(element[i][1])
                    DepTime = dic.get('time')
                if element[i][0] == 'arrival':
                    dic = ast.literal_eval(element[i][1])
                    Dest = dic.get('arrivalPoint')  
                if element[i][0] == 'estimated':
                    dic = ast.literal_eval(element[i][1])
                    ArrTime = dic.get('time')
                if element[i][0] == 'position' and indexposition == 0: #the tag 'position' sometimes appear several times in one message so we only 
                    dic = ast.literal_eval(element[i][1]) #save the first one because it's the only one carrynig the actual position of the flight
                    GenTime = dic.get('positionTime')# the second one is the target position
                    indexposition = 1
                if element[i][0] == 'pos' and indexpos == 0: 
                    try:
                        latitude = element[i][2].split(' ')[0]
                        longitude = element[i][2].split(' ')[1]
        #                CSV[-1][7] = latitude
        #                CSV[-1][8] = longitude
                    except:
                        latitude = element[i][2]
                        longitude = element[i][2]
                    indexpos = 1
                if element[i][0] == 'altitude':
                    altitude = element[i][2]
            if (FlightAppear[1][FlightAppear[0].index(aircraftId)] % 5) == 0: ###take only one position out of five to have lighter files at the end. 
                CSV.append([WantedMsg, aircraftId, Origin, DepTime, Dest, ArrTime, GenTime, latitude, longitude,altitude])
                    
                
    except:
        error.append(title)
        print('The file', title, 'is not readable')
        pass
    counter += 1


outputFile = Resultfolder + '\\' + Day + '_11_15.csv'

#print('Writing CSV...')
#filename_data = 'DecodedSFDPS.csv'      
fh_data = open(outputFile,'w', newline='')        
writer = csv.writer(fh_data) #write the output file 
writer.writerows(CSV) #each row of the CSV is one list of myData
fh_data.close()

print('step 4 done',"--- %s minutes ---" % ((time.time() - start_time)/60))
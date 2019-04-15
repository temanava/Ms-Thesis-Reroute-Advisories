 # -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 10:10:58 2019

@author: Ghislain Dard
"""
### This code extracts all RMD advisories during one month of TFMS data divided into hourly files 
from lxml import etree as ET
import os
import re
import csv
import time
from datetime import datetime
date_format = "%Y-%m-%dT%H:%M:%SZ" 

def SplitOriginRoute(a,Lorigin):
    if a[0:3] != '   ':
        if a[0] == 'K':
            Lorigin.append(a[0:4])  
            SplitOriginRoute(a.replace(a[0:5],''),Lorigin)  
        else:
            Lorigin.append(a[0:3])  
            SplitOriginRoute(a.replace(a[0:4],''),Lorigin)  
        
def extractchildTFMS(child,A,B,C):         # This function extract all fields of the xml documents: child, subchild, subsubchild...
    line = child.tag
    line = line.strip()
    line = line.strip('\n')
    words = line.split('}')
    field = words[1]
    A.append(field)
    B.append(child.attrib)
    C.append(child.text)
    if child.getchildren != []:
        for element in child:
            extractchildTFMS(element,A,B,C)

start_time = time.time()    
# Path of the output file    

pathResult = 'C:\\Users\\gdard3\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\TFMS\\Results\\TFMS_FLOW_201704\\'
path = 'C:\\Users\\gdard3\\Documents\\MsThesis\\Raw Data\\TFMS\\TFMS_FLOW_201704\\'
#path = 'C:\\Users\\teman\\OneDrive - Georgia Institute of Technology\\Master Thesis\\Data Processing\\TFMS\\'
#Day = 'TFMS_FLOW_20170220'
#folder = path + Day
folder = path


error = []
for title2 in os.listdir(folder):
    print(title2)
    CSV = []
    CSVb = []
    headers = ['Adv number', 'dateSent', 'startTime','endTime','Reason','probability of Extension','Origin','Route Origin','Destination','Route Destination']
    CSV.append(headers)
    counter = 0
    EndOrigin = [1] # will store the line of separation between two messages in the final CSV
    EndDest = []
    AdvUpdate = [] #will store all advzy number updating and updated durinh one day in the format [[updating, updated], [updating,updated],...] It is used in the last loop just before writing the file
    EffPeriod = [] # stores all effective period of rmd reroutes in the format [[advzy number, start period, end period], [...],...]
    for title in os.listdir(folder+title2):
        try:
            print('hour', counter)
            filename=os.path.join(folder+title2,title) ## this section modifies the input file by adding a root tag at the beginning and end 
            src = open(filename, "r")
            fline = "<root>\n"
            oline = src.readlines()
            src.close()
            if oline[0] != '<root>\n':
                oline.insert(0, fline)
                oline.append('</root>')
                for i in range (1, len(oline)):
                    if '<?xml' in oline[i]:
                        oline[i] = oline[i][:oline[i].index('<?xml')]
                    if '<SWIMClient-File version="2.0.1-SNAPSHOT">' in oline[i]:  ## checks if the schema is well specified
                        oline[i] = oline[i][:oline[i].index('<SWIMClient-File version="2.0.1-SNAPSHOT">')] + '<SWIMClient-File xmlns="org:mitre:swim:smes:v1-0" version="4.0.157-SNAPSHOT">'
                src = open(filename, "w")
                src.writelines(oline)
                src.close()
                #print('Rewriting done')
            del oline
            #print('add footer and header and remove xml tag done', "--- %s seconds---" % (time.time()- start_time))
            ####################### Step 2: Parse the file #####################################################
            
            if path[-7:-1] == '201702':
                if int(title[16:18]) < 22:
                    ns = {"ghislain": "org:mitre:swim:smes:v1-0"}
                elif int(title[16:18]) > 22:
                    ns = {"ghislain": "org:mitre:swim:tais:v1-0"}
                elif int(title[16:18]) == 22:
                    if int(title[19:]) <= 20:
                        ns = {"ghislain": "org:mitre:swim:smes:v1-0"}
                    else:
                        ns = {"ghislain": "org:mitre:swim:tais:v1-0"}
            elif path[-7:-1] == '201701':
                ns = {"ghislain": "org:mitre:swim:smes:v1-0"}
            else:
                ns = {"ghislain": "org:mitre:swim:tais:v1-0"}
            tree = ET.parse(filename)
            
            root = tree.getroot()
            A = []
            B = []
            C = []
            s = []
            for child in root:
                s.append(child.tag[26::])
            
            for msg in root.findall('ghislain:' + 'SWIMClient-File', ns):
                for child in msg:
                    extractchildTFMS(child,A,B,C)
            ## At this moment, A and B are two lists with all information of the input file 
            
            for i in range (0,len(C)): # this loop is just turning the blank fields into ''
                if C[i] != None:
                    if '\n' in C[i] and A[i] != 'advisoryText' :
                        C[i] = ''
            
            
            want = list(zip(A, B, C)) #make one list of two columns instead of 2 lists
        
            line = []
            loc = [i for i, x in enumerate(A) if x == 'fiMessage'] #find positions of all 'fiMessage' which is the opening field of each messages. 
            # L= [i for i,x in enumerate(A) if x=='fiMessage']
            del A,B,C
            for i in range (len(loc)):
                if want[loc[i]][1].get('msgType') == 'GADV':
                    line.append([])
                    if i != len(loc)-1:
                        for j in range (loc[i], loc[i+1]-1):
                            line[-1].append(want[j])
                    else:
                        for j in range(loc[i], len(want)):
                            line[-1].append(want[j])
                            
            
            for element in line:  
                for i in range (len(element)):
                    if element[i][0] == 'advisoryTitle' and 'ROUTE RMD' in element[i][2]:
                        #print(element[i])
                        EffPeriod.append([0,0,0,0])
                        for j in range (len(element)):
                            if element[j][0] == 'advisoryNumber':
                                advisoryNum = element[j][2]
                                EffPeriod[-1][0] = element[j][2]
                            if element[j][0] == 'dateSent':
                                dateSent = element[j][2]
                                EffPeriod[-1][1] = element[j][2]
                            if element[j][0] == 'startTime':
                                startTime = element[j][2]
                                EffPeriod[-1][2] = element[j][2]
                            if element[j][0] == 'endTime':
                                endTime = element[j][2]
                                EffPeriod[-1][3] = element[j][2]
                            if element[j][0] == 'advisoryText':
                                text = element[j][2]
                                split = text.split('\n')
                                origin = []
                                destination = []
                                routeOrigin = []
                                routeDest = []
                                index3 = 0
                                for element2 in split:
                                    if 'REASON' in element2:
                                        reason = element2[7:]
                                    elif 'PROBABILITY OF EXTENSION' in element2:
                                        probExt = element2[25:]
                                    elif ('REMARKS REPLACES ADVZY' in element2) or ('REMARKS REPLACES ADVISORY' in element2) or ('REMARKS REPLACES/AMENDS ADVZY' in element2):
                                        if [advisoryNum, '0'+element2.split(' ')[3]] not in AdvUpdate:
                                            AdvUpdate.append([advisoryNum,'0'+element2.split(' ')[3]])
                                    elif 'ORIG' in element2 and 'DEST' in element2 and 'ROUTE' in element2:
                                        index3 = split.index(element2)
                                    elif 'ORIG' in element2:
                                        index = split.index(element2)
                                        #print('index = ', index)
                                    elif 'DEST' in element2:
                                        index2 = split.index(element2)
                                        #print('index2 = ', index2)
                                if index3 != 0: ## if the format is orig dest route
                                    #print('yes there is a case')
                                    origin = []
                                    destination= []
                                    route = []
                                    for i in range (index3+2, split[index3+2:].index('')+index3+2):
                                        liste = [i for i in split[i].split('  ') if i != '']
                                        if len(liste) > 2:
                                            origin.append(liste[0].split(' '))
                                            destination.append([i for i in liste[1].split(' ') if i != ''])
                                            route.append(liste[2])
                                        else: 
                                            if split[i][0:3]!='   ':
                                                origin[-1].append(liste[0])
                                            elif split[i][0:20] == '                    ' and split[i][20] != ' ':
                                                destination[-1].append(liste[0])
                                            else:
                                                route[-1]= route[-1] + liste[0]
                                    for j in range (len(origin)):
                                        if len(origin[j])==1 and len(destination[j]) == 1:
                                            CSVb.append([])
                                            CSVb[-1] = [EffPeriod[-1][0], EffPeriod[-1][1], EffPeriod[-1][2],EffPeriod[-1][3],reason,probExt,origin[j][0],destination[j][0],route[j]]
                                        elif len(origin[j])>1 and len(destination[j]) == 1:
                                            for bb in origin[j]:
                                                CSVb.append([])
                                                CSVb[-1] = [EffPeriod[-1][0], EffPeriod[-1][1], EffPeriod[-1][2],EffPeriod[-1][3],reason,probExt,bb,destination[j][0],route[j]]
                                        elif len(origin[j])==1 and len(destination[j]) > 1:
                                            for bb in destination[j]:
                                                CSVb.append([])
                                                CSVb[-1] = [EffPeriod[-1][0], EffPeriod[-1][1], EffPeriod[-1][2],EffPeriod[-1][3],reason,probExt,origin[j][0],bb,route[j]]
                                    
                                        elif len(origin[j])>1 and len(destination[j]) > 1:
                                            for bb in origin[j]:
                                                for cc in destination[j]:
                                                    CSVb.append([])
                                                    CSVb[-1] = [EffPeriod[-1][0], EffPeriod[-1][1], EffPeriod[-1][2],EffPeriod[-1][3],reason,probExt,bb,cc,route[j]]
             
                                else: ## if the format is orig origin routes, dest dest routes
                                    try:
                                        for i in range (index+2, index2-3):#analyse the origin airport and origin routes
                                            #print(i)
                                            routeOr = ''
                                            route3 = []
                                            route4 = []
                                            if split[i][0:3] != '   ':
                                                airport = []
                                                SplitOriginRoute(split[i],airport)
                                                route3 = re.sub(r'\W+',' ',split[i]).split(' ')
                                                route3 = [i for i in route3 if i != '']
                                                for element3 in airport:
                                                    if element3 in route3[0:len(airport)*3]:
                                                        route3.remove(element3)
                                                    origin.append(element3)    
                                                routeOr = route3[0]
                                                for element4 in route3[1:]:
                                                    routeOr = routeOr + ' ' + element4
                                                for j in range (0, len(airport)):
                                                    routeOrigin.append(routeOr)
                                            elif split[i][0] == ' ':
                                                route4 = re.sub(r'\W+',' ',split[i]).split(' ')
                                                route4 = [i for i in route4 if i != '']
                                                routeOr = route4[0]
                                                for element5 in route4[1:]:
                                                    routeOr = routeOr + ' ' + element5
                                                for i in range (0,len(airport)):
                                                    routeOrigin[-1-i] = routeOrigin[-1-i] + ' ' + routeOr
                                                    
                                        for k in range (index2+2, split[index2+2:].index('')+index2+2): #analyse the destination part of the text
                                            routeOr = ''
                                            route3 = []
                                            route4 = []
                                            if split[k][0:3] != '   ':
                                                airport = []
                                                SplitOriginRoute(split[k],airport)
                                                route3 = re.sub(r'\W+',' ',split[k]).split(' ')
                                                route3 = [i for i in route3 if i != '']
                                                for element6 in airport:
                                                    if element6 in route3[0:len(airport)*3]:
                                                        route3.remove(element6)
                                                    destination.append(element6)    
                                                routeOr = route3[0]
                                                for element7 in route3[1:]:
                                                    routeOr = routeOr + ' ' + element7
                                                for j in range (0, len(airport)):
                                                    routeDest.append(routeOr)
                                            elif split[k][0] == ' ':
                                                route4 = re.sub(r'\W+',' ',split[k]).split(' ')
                                                route4 = [i for i in route4 if i != '']
                                                routeOr = route4[0]
                                                for element8 in route4[1:]:
                                                    routeOr = routeOr + ' ' + element8
                                                for i in range (0,len(airport)):
                                                    routeDest[-1-i] = routeDest[-1-i] + ' ' + routeOr 
                                        for l in range (0,len(origin)):
                                            CSV.append([])
                                            CSV[-1] = [EffPeriod[-1][0], EffPeriod[-1][1], EffPeriod[-1][2],EffPeriod[-1][3],reason,probExt,origin[l],routeOrigin[l],'','']
                                        EndOrigin.append(len(CSV))
                                        for l in range (0,len(destination)):
                                            CSV.append([])
                                            CSV[-1] = [EffPeriod[-1][0], EffPeriod[-1][1], EffPeriod[-1][2],EffPeriod[-1][3],reason,probExt,'','',destination[l],routeDest[l]]
                                        EndDest.append(len(CSV))
                                        EndOrigin.append(len(CSV))
                                    except:
                                        pass
    
            print('Length of the CSV file', len(CSV))
            #print('Done with hour', "--- %s ---" % counter)
            
        except:
            error.append(title)
            print('The file', title, 'is not readable')
            pass
        counter += 1
        
        
    ########### Convert CSV to a format with Origin Dest Required reroute instead of all origins, all destinations and corresponding routes
    
    CSV2 = [['Adv number', 'dateSent', 'startTime','endTime','Reason','probability of Extension','Origin','Destination','Reroute']]
    for element in CSVb:
        CSV2.append(element)
    for k in range (len(EndDest)):
        for i in range (EndOrigin[2*k],EndOrigin[2*k+1]):
            #print(i)
            for j in range (EndOrigin[2*k+1],EndOrigin[2*k+2]):
                #print(j)
                if CSV[i][6] != CSV[j][8]:
                    CSV2.append([])
                    if CSV[i][7].split()[-1] == CSV[j][9].split()[0]:
                        CSV2[-1] = [CSV[i][0], CSV[i][1],CSV[i][2], CSV[i][3], CSV[i][4], CSV[i][5], CSV[i][6], CSV[j][8], CSV[i][7][:-6] +' '+ CSV[j][9]]
                    else:
                        CSV2[-1] = [CSV[i][0], CSV[i][1],CSV[i][2], CSV[i][3], CSV[i][4], CSV[i][5], CSV[i][6], CSV[j][8], CSV[i][7] +' '+ CSV[j][9]]
    
    ######## This loop deletes identical lines and modify the updated advisories############
    CSV3 = []
    for element in CSV2:
        if any(element[0] == x[0] for x in AdvUpdate) == True: #This condition is for updating advisories
            starttime2 = datetime.strptime(element[2], date_format)
            datesent2 = datetime.strptime(element[1], date_format)
            if starttime2 < datesent2:
                element[2] = element[1] # if the sent time is after the start time then start time becomes the sent time  
        for updates in AdvUpdate:
            if element[0] == updates[1]:
                for element2 in EffPeriod:
                    if updates[0] == element2[0]:                
                        starttime3 = datetime.strptime(element2[2], date_format)
                        datesent3 = datetime.strptime(element2[1], date_format)
                        if starttime3 < datesent3:
                            element[3] = element2[1]
                        else:
                            element[3] = element2[2]
        #if any(element[0] == x[1] for x in AdvUpdate) == True: #This condition is for updated advisories           
        if element in CSV3:
            pass
        else:
            CSV3.append(element)
    #del CSV2
        
    name = os.path.basename(filename)
    name = name[:-3]
    outputFile = pathResult + title2 + '_withUpdates.csv'
       
    fh_data = open(outputFile,'w', newline='')        
    writer = csv.writer(fh_data) #write the output file 
    writer.writerows(CSV3) #each row of the CSV is one list of myData
    fh_data.close()     
    
    print('Writing CSV done '+title2, "--- %s seconds---" % (time.time()- start_time))
        

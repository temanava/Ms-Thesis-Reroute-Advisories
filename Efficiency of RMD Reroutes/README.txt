##Assess the Efficiency of Recommended Flight reroutes

The code in this folder has been developped and implemented to assses the compliance of flights to recommended reroutes. The processed data are SFDPS and TFMS datasets provided by the FAA. They are in FIXM format. Steps taken for this part are the following:

1. Parse SFDPS dataset,extract TH messages with the code 'SFDPSparser v5 All Files.py', and store them as CSV files. This code extract all TH messages for one day of data divided into 24 hourly files. 

2. Parse TFMS dataset, extract RMD Reroute messages from GADV messages with the code 'GADV RMD 2017 all month.py' and store them as CSV files. 

3. Include rmd reroute coordinates in csv files with the code 'IncludeCoordinates v2.py'.

4. Fuse datasets, implement compliance metrics and compute compliance metrics for each flight affected by reroute with the code 'Route Comparison v8 One File per month.py'. Create csv files with results per month.

## FavRoute - GPX2CSV.py #################################################
#
#  Jae Hyung Lim
#  05/25/2019
#
#  This code reads in GPS traces in GPX file in ./GPX directory,
#  and convert the GPS traces to CSV file, and save it in ./CSV directory.
#  
#  When a new GPX file is added to ./GPX directory, this file should run.
#  It will compare the contents in ./GPX and ./CSV directories, and work
#  with new files.
#
## #######################################################################


from os import listdir
import os, fnmatch
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from haversine import haversine


def GPX_CSV_list():
    GPX_dir = listdir('./GPX')
    CSV_dir = listdir('./CSV')
    
    GPX_list = []
    CSV_list = []
    
    for entry in GPX_dir:  
        if fnmatch.fnmatch(entry, '*.gpx'):
            GPX_list.append(entry[:-4])
            
    for entry in CSV_dir:  
        if fnmatch.fnmatch(entry, '*.csv'):
            CSV_list.append(entry[:-4])
    
    GPX_unprocessed = []
    
    for i in GPX_list:
        if i not in CSV_list:
            GPX_unprocessed.append(i)
    
    return GPX_unprocessed

def GPX_to_CSV(GPX_to_process):
    for fileName in GPX_to_process:
        # file name mod
        fileName = 'GPX/' + fileName + '.gpx'
        
        # Parse the GPX (XML format)
        root = ET.parse(fileName).getroot()

        # Namespace setting
        ns = {'NameSp': 'http://www.topografix.com/GPX/1/1'}
        firstLastDist = 0.5 # [mile]
        
        # Empty dataframe
        GPS_Log = pd.DataFrame(columns=['Time','Lat','Lon'])
        
        # Parse time,lat,lon
        for TRKSEG in root.findall('NameSp:trk', ns):
            for TRKPT in TRKSEG.find('NameSp:trkseg', ns):
                T = datetime.strptime(TRKPT.find('NameSp:time', ns).text[:-1], '%Y-%m-%dT%H:%M:%S.%f')
                Lat = TRKPT.attrib['lat'][:10]
                Lon = TRKPT.attrib['lon'][:10]
                
                GPS_Log = GPS_Log.append({'Time': T, 'Lat': Lat, 'Lon':Lon}, ignore_index=True)
        
        # Find first entry where the vehicle goes outside of the firstLastDist.
        # Then trim any entries before that.
        startDist = 0.0
        for i in range(len(GPS_Log)-1):
            segmentLength = haversine([float(GPS_Log.Lat[i]),  float(GPS_Log.Lon[i]  )], \
                                      [float(GPS_Log.Lat[i+1]),float(GPS_Log.Lon[i+1])], unit='mi')
            startDist = startDist + segmentLength
            if startDist >= firstLastDist:
                GPS_Log = GPS_Log.loc[i:].reset_index(drop=True)
                break
        
        # Find first entry where the vehicle comes inside of the firstLastDist (counting backward from the end).
        # Then trim any entires after that.
        stopDist = 0.0
        for j in reversed(range(len(GPS_Log)-1)):
            segmentLength = haversine([float(GPS_Log.Lat[j]),  float(GPS_Log.Lon[j]  )], \
                                      [float(GPS_Log.Lat[j+1]),float(GPS_Log.Lon[j+1])], unit='mi')
            stopDist = stopDist + segmentLength
            if stopDist >= firstLastDist:
                GPS_Log = GPS_Log.loc[:j]
                break
        
        # Save it as csv
        GPS_Log.to_csv('CSV/'+fileName[4:-4]+'.csv', sep=',', index=False)
        
    return 0

###### Find out which GPX files still to process.
GPX_to_process =  GPX_CSV_list()
GPX_to_CSV(GPX_to_process)


## Change log ############################################################
#
#  05/25/2019
#  Initical commit.
#
## #######################################################################

import csv
import re
import time
import datetime
import argparse
import os
import sys
from pytz import timezone
from influxdb import InfluxDBClient
from datetime import timedelta
from multiping import MultiPing

def ping(host,n = 0):
    if(n>0):
        avg = 0
        for i in range (n):
            avg += ping(host)
        avg = avg/n
    # Create a MultiPing object to test hosts / addresses
    mp = MultiPing([host])

    # Send the pings to those addresses
    mp.send()

    # With a 1 second timout, wait for responses (may return sooner if all
    # results are received).
    responses, no_responses = mp.receive(1)


    for addr, rtt in responses.items():
        RTT = rtt


    if no_responses:
        # Sending pings once more, but just to those addresses that have not
        # responded, yet.
        mp.send()
        responses, no_responses = mp.receive(1)
        RTT = -1

    return RTT

##
## Check if data type of field is float
##
def isfloat(value):
        try:
            float(value)
            return True
        except:
            return False

##
## Check if data type of field is int
##
def isinteger(value):
        try:
            if(float(value).is_integer()):
                return True
            else:
                return False
        except:
            return False


# parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('--hosts', help='List of hosts to ping, separated with ;', required=True)
parser.add_argument('--dbhost', default="localhost", help='InfluxDb hostname or ip')
parser.add_argument('--dbport', default="8086", help='InfluxDb port number')
parser.add_argument('--dbname', default="influxdb", help='InfluxDb database name')
parser.add_argument('--verbose', type=int, default=0, help='Display all parameters used in the script')

args = parser.parse_args()

if (args.verbose):    
    print("Hosts=%s" %(args.hosts))
    print("Dbhost=%s" %(args.dbhost))
    print("Dbport=%s" %(args.dbport))
    print("Dbname=%s" %(args.dbname))

datapoints = []

# connect to influx
client = InfluxDBClient(host=args.dbhost, port=args.dbport)
client.switch_database(args.dbname)

# ping all hosts
for host in args.hosts.split(";"):    
    timestamp = time.time() *1000*1000*1000
    datapoint = "ping,host=%s,objectname=ping RTT=%f %d\n" %(host, ping(host), timestamp )
    datapoints.append(datapoint)    

# display datapoints if in verbose mode
if (args.verbose):    
    for datapoint in datapoints:
        print (datapoint)


if len(datapoints):
    if (args.verbose): 	
	    print('Inserting %d datapoints...'%(len(datapoints)))

    response = client.write_points(datapoints,  protocol ="line")

    if response == False:
        print('Problem inserting points, exiting...')
        exit(1)

    if (args.verbose): 
        print("Wrote %d, response: %s" % (len(datapoints), response))

    datapoints = []            


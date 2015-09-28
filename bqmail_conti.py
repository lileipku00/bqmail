#!/usr/bin/env python
#
#Author: Mijian Xu at NJU
#
#Revision History:
#   2015/08/19
#   2015/09/23
#

def Usage():
    print('Usage:')
    print('python bqmail_conti.py -Istation.lst -Yyear1/month1/day1/year2/month2/day2 -Hhour [-Cchannel] [-Fformat] head.cfg')
    print('-I   -- Station list. format: Network station')
    print('-Y   -- Date range.')
    print('-C   -- Channel (e.g., ?H?, HHZ, BH?). Default: BH?')
    print('-H   -- Request continuous wave by hour.')
    print('-F   -- File format (SEED or miniseed). Default: SEED')
    print('head.cfg   -- Config file.')
    print('Example: ./bqmail_conti.py -Iex_sta.lst -Y2003/12/3/2003/12/4 -H24 head.cfg')


import datetime
import os, re
import sys, getopt
import time
try:
    import configparser
    config = configparser.ConfigParser()
except:
    import ConfigParser
    config = ConfigParser.ConfigParser()

head = ''
argv = sys.argv[1:]
for o in argv:
    if os.path.isfile(o):
        head = o
        argv.remove(o)
        break

try:
    opts,args = getopt.getopt(argv, "hI:C:Y:H:F:")
except:
    print('Arguments are not found!')
    Usage()
    sys.exit(1)
if opts == []:
    Usage()
    sys.exit(1)
chan = "BH?"
fformat = "seed"
for op, value in opts:
    if op == "-I":
        infile = value
    elif op == "-H":
        timeval = float(value)
    elif op == "-Y":
        yrange = value
        isyrange = 1
    elif op == "-C":
        chan = value
    elif op == "-F":
        fformat = value
    elif op == "-h":
        Usage()
        sys.exit(1)
    else:
        Usage()
        sys.exit(1)

if head == '':
    print("Head file are not exist!")
    Usage()
    sys.exit(1)
    
if isyrange:
   y_split = yrange.split('/')
   year1 = int(y_split[0])
   mon1 = int(y_split[1])
   day1 = int(y_split[2])
   year2 = int(y_split[3])
   mon2 = int(y_split[4])
   day2 = int(y_split[5])
   datemin=datetime.datetime(year1,mon1,day1)
   datemax=datetime.datetime(year2,mon2,day2)


config.read(head)
eventlst = config.get("lst","eventlst")
NAME = config.get("info","NAME")
INST = config.get("info","INST")
EMAIL = config.get("info","EMAIL")
MEDIA = config.get("info","MEDIA")
ALTERNATEMEDIA = MEDIA
if fformat.lower() == 'seed':
    recipient = 'breq_fast@iris.washington.edu'
elif fformat.lower() == 'miniseed':
    recipient = 'miniseed@iris.washington.edu'
else:
    print('Invalid file format!')
    sys.exit(1)

sta = []
fid = open(infile,'r')
for stainfo in fid.readlines():
    stainfo = stainfo.strip()
    stainfo_sp = stainfo.split()
    if len(stainfo_sp) == 3:
        sta.append([stainfo_sp[0], stainfo_sp[1], stainfo_sp[2]])
    else:
        sta.append([stainfo_sp[0], stainfo_sp[1], ''])

nowtime = datemin
while 1:
    if nowtime >= datemax:
        break
    endtime = nowtime + datetime.timedelta(hours=timeval)
    LABEL = 'IRIS_'+nowtime.strftime('%Y')+'.'+nowtime.strftime('%m')+'.'+nowtime.strftime('%d')+'.'+nowtime.strftime('%H')
    msg = ''
    msg += '.NAME '+NAME+'\n'
    msg += '.INST '+INST+'\n'
    msg += '.MAIL\n'
    msg += '.EMAIL '+EMAIL+'\n'
    msg += '.PHONE\n'
    msg += '.FAX\n'
    msg += '.MEDIA '+MEDIA+'\n'
    msg += '.ALTERNATE MEDIA '+ALTERNATEMEDIA+'\n'
    msg += '.ALTERNATE MEDIA '+ALTERNATEMEDIA+'\n'
    msg += '.LABEL '+LABEL+'\n'
    msg += '.END\n'
    for sta_row in sta:
        msg += sta_row[1]+' '+sta_row[0]+' '+nowtime.strftime('%Y %m %d %H %M %S')+' '+endtime.strftime('%Y %m %d %H %M %S')+' 1 '+chan+' '+sta_row[2]+'\n'
    with open('tmp.bq','w') as fid_msg:
        fid_msg.write(msg)
    os.system('mail '+recipient+'<tmp.bq')
    print("Successful sending the mail between "+nowtime.strftime('%Y')+'.'+nowtime.strftime('%m')+'.'+nowtime.strftime('%d')+'.'+nowtime.strftime('%H')+" and "+endtime.strftime('%Y')+'.'+endtime.strftime('%m')+'.'+endtime.strftime('%d')+'.'+endtime.strftime('%H')+"!!!")
    nowtime = nowtime + datetime.timedelta(hours=timeval)
    time.sleep(4.5)
os.system('rm tmp.bq')

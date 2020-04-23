#!/usr/bin/python3.7

import datetime
import getpass
import sys
import telnetlib
import shelve
import MySQLdb

HOST = "192.168.0.XX" #Router IP
user = "admin" #Router User
password = "**************" #Router Password

tn = telnetlib.Telnet(HOST)

tn.read_until(b"Login: ")
tn.write((user + "\n").encode('ascii'))
if password:
    tn.read_until(b"Password: ")
    tn.write((password + "\n").encode('ascii'))

tn.write(b"adsl info --show\n")
tn.write(b"exit\n")
rawtext = tn.read_all()
#print rawtext
values = str.split( rawtext.decode("utf-8") )
print (values)

d = shelve.open('routerstats.db')

if 'LastRSUncorr' not in d:
   LastUncorrected = 0
else:
   LastUncorrected = d['LastRSUncorr']


Status = values[values.index("Status:")+1]
MaxSyncDown = float(values[values.index("Downstream")+3])
MaxSyncUp = float(values[values.index("Upstream")+3])
SyncDown = float(values[values.index("Downstream")+15])
SyncUp = float(values[values.index("Upstream")+15])
RS = float(values[values.index("RS:")+1])
RSCorr = float(values[values.index("RSCorr:")+1])
RSUnCorr = float(values[values.index("RSUnCorr:")+1])
SNRDown = float(values[values.index("SNR")+2])
SNRUp = float(values[values.index("SNR")+3])
PowerDown = float(values[values.index("Pwr(dBm):")+1])
PowerUp = float(values[values.index("Pwr(dBm):")+2])
AttenDown = float(values[values.index("Attn(dB):")+1])
PercentCorrectable =  float(round(float(RSCorr) / float(RS) * 100, 3))
PercentUncorrectable =  float(round(float(RSUnCorr) / float(RS) * 100, 3))

d['LastRSUncorr'] = RSUnCorr
d.close()

values = [Status , SyncDown, SyncUp, RS, RSCorr, RSUnCorr, SNRDown, SNRUp, PowerDown, PowerUp, AttenDown, int( RSUnCorr) - int(LastUncorrected), PercentCorrectable, PercentUncorrectable, MaxSyncUp, MaxSyncDown ]

mydb = MySQLdb.connect(
  host="localhost",
  user="root",
  passwd="******************",
  db="sysops"
)

mycursor = mydb.cursor()

sql = """INSERT INTO dsl_stats (status,SyncDown,SyncUp,RS,RSCorr,RSUnCorr,SNRDown,SNRUp,PowerDown,PowerUp,Attn,UnCorrected,PercentCorrectable,PercentUncorrectable,MaxSyncUp,MaxSyncDown) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

print(values)
mycursor.execute(sql, values)

mydb.commit()

print(mycursor.rowcount, "record inserted.")

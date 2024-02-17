#!/usr/bin/python3

import csv
from datetime import datetime
from datetime import date
from datetime import timedelta

import sys
import jstyleson # run pip3 install jstyleson
import getopt

__doc__ = """NEM12 reader

Copyright (c) 2010-2024 Jean-Yves Avenard

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the Jean-Yves Avenard and Hydrix Pty Ltd nor the names
      of its contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Usage: analysis_power.py [options]

Options:
    -h / --help
        Print this message and exit.

    -d / --date [YYYYMMDD][:YYYMMDD]
        Retrieve data from date DD/MM/YYYY, default is data of yesterday
        or between two provided date (end data is inclusive)

    -f / --file FILENAME.csv
        NEM12 file retrieved from your network operator
    -c / --config TARIF_FILE
        Tarif File
"""

filename = '61022432106_20211017_20230724_20230725214801_CITIPOWER_DETAILED.csv'
config_file = "tariffEV.cfg"

startdate = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
enddate = datetime.strptime(startdate, '%Y%m%d') + timedelta(hours=23, minutes=59, seconds=59)
startdate = datetime.strptime(startdate, '%Y%m%d')

def usage():
    print(__doc__)

try:
    opts, args = getopt.getopt(sys.argv[1:], \
        "hd:f:c:", \
        ["help", "date=", "file=", "config="])
except getopt.GetoptError:
    # print help information and exit:
    print("Unrecognised option: ")
    usage()
    sys.exit(2)

for o, a in opts:
    if o in ["-h", "--help"]:
        usage()
        sys.exit(0)
    elif o in ["-d", "--date"]:   
        dates = a.split(':')
        startdate = datetime.strptime(dates[0], '%Y%m%d')
        if len(dates) == 2:
            enddate = datetime.strptime(dates[1], '%Y%m%d') + timedelta(hours=23, minutes=59, seconds=59)
        else:
            enddate = startdate + timedelta(hours=23, minutes=59, seconds=59)
        days = (enddate-startdate).days
        if days < 0:
            print("Error with dates:", dates[1], "<", dates[0])
            sys.exit(3)

    elif o in ["-f", "--file"]:
        filename = a
    elif o in ["-c", "--config"]:
        config_file = a

## Code starts here, no user data setup.
with open(config_file, 'r') as file:
    configstring = file.read()
config = jstyleson.loads(configstring)

# Check config validity
if len(config['pricing']) != 5:
  print("Invalid pricing array, should be made of 5 numbers")
  exit
if len(config['workday']) != 48:
  print("Invalid workday tariff array, should be made of 48 numbers")
  exit
if len(config['weekend']) != 48:
  print("Invalid weekend tariff array, should be made of 48 numbers")
  exit

def isweekend(date):
  return True if date.weekday() == 5 or date.weekday() == 6 else False

class Day:
  def __init__(self):
    self.tariffs = []

  def tariff(self, index):
    return self.tariffs[index]

class WorkDay(Day):
  def __init__(self):
    self.tariffs = config['workday']

class Weekend(Day):
  def __init__(self):
    self.tariffs = config['weekend']

log = False
totals = { }
days = { }
meter = ''
interval = 0;
with open(filename, 'r') as File:
    reader = csv.reader(File)
    for row in reader:
        if len(row) > 0:
          type = int(row[0])
          if type == 200:
            meter = row[3]
            interval = int(row[8])
            if log:
              print("meter", meter)
            totals[meter] = ([0.0 for x in range(5)])
            days[meter] = 0;

          if type == 300:
            day = datetime.strptime(row[1], '%Y%m%d')
            if day >= startdate and day <= enddate:
              days[meter] += 1
              if (isweekend(day)):
                tariff = Weekend()
              else:
                tariff = WorkDay()
              for i in range(2, len(row) - 5):
                current_interval = int((i - 2) * interval / 30)
                pricing = tariff.tariff(current_interval) - 1
                totals[meter][pricing] += float(row[i])

File.close()

if log:
  for i in totals:
    print("meter", i, '=', totals[i])
print("period is", startdate, "to", enddate, "inclusive")
print("total amount of days: ", days)

numberOfDays = (enddate-startdate).days + 1
for i in totals:
  totalEnergyPeriod = 0
  totalPricePeriod = 0
  for j in range(len(totals[i])):
    energy = totals[i][j]
    if energy > 0:
      price = energy * config['pricing'][j] / 100
      print("Total for meter", i, "tariff", j+1, round(energy, 3), "kWh -> $", round(price, 2))
      totalEnergyPeriod += energy
      totalPricePeriod += price
  print(i, "total", i, "is", round(totalEnergyPeriod, 2),"kWh $", round(totalPricePeriod, 2))
  print(i, 'average usage per day', round(totalEnergyPeriod / numberOfDays,3))
  print(i, 'average cost per day $', round(totalPricePeriod / numberOfDays,2))
  print()
print('number of days in period', numberOfDays)
print('daily charge $', config['daily'] * numberOfDays / 100)

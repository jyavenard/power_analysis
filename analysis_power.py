#!/bin/python

import csv
from datetime import datetime
from datetime import timedelta
import jstyleson # run pip install jstyleson

startdate = '20220724'
enddate = '20230724'
filename = '61022432106_20211017_20230724_20230725205036_CITIPOWER_DETAILED.csv'
config_file = "tariffPeakOffpeak.cfg"
#config_file = "tariffEV.cfg"

## Code starts here, no user data setup.
with open(config_file, 'r') as file:
    configstring = file.read()
config = jstyleson.loads(configstring)

# Check config validity
if len(config['pricing']) != 4:
  print("Invalid pricing array, should be made of 4 numbers")
  exit
if len(config['workday']) != 48:
  print("Invalid workday tariff array, should be made of 48 numbers")
  exit
if len(config['weekend']) != 48:
  print("Invalid weekend tariff array, should be made of 48 numbers")
  exit

startdate = datetime.strptime(startdate, '%Y%m%d')
enddate = datetime.strptime(enddate, '%Y%m%d') + timedelta(hours=23, minutes=59, seconds=59)

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

account = -1
totals = [[0.0], [0.0], [0,0], [0,0]]
for i in range(0, 4):
  totals[i] = ([0.0 for x in range(4)])

days = [0,0,0,0]
with open(filename, 'r') as File:
    reader = csv.reader(File)
    for row in reader:
        if len(row) > 0:
          type = int(row[0])
          if type == 200:
            account += 1
            print("account", account, row[1], row[6])
          if type == 300:
            day = datetime.strptime(row[1], '%Y%m%d')
            if day >= startdate and day <= enddate:
              days[account] += 1
              if (isweekend(day)):
                tariff = Weekend()
              else:
                tariff = WorkDay()
              for i in range(2, len(row) - 5):
                pricing = tariff.tariff(i - 2) - 1
                totals[account][pricing] += float(row[i])

File.close()

print(totals[0])
print(totals[1])
print("period is", startdate, "to", enddate, "inclusive")
print("total amount of days: ", days)

for i in range(account+1):
  totalEnergyPeriod = 0
  totalPricePeriod = 0
  for j in range(len(totals[i])):
    energy = totals[i][j]
    if energy > 0:
      price = energy * config['pricing'][j] / 100
      print("Total for account", i, "tariff", j+1, round(energy, 3), "kWh -> $", round(price, 2))
      totalEnergyPeriod += energy
      totalPricePeriod += price
  print("total for account", i, "is", round(totalEnergyPeriod, 2),"kWh $", round(totalPricePeriod, 2))

numberOfDays = (enddate-startdate).days + 1
print('number of days in period', numberOfDays)
print('daily charge', config['daily'] * numberOfDays / 100)
print('average usage per day', round(totalEnergyPeriod / numberOfDays,3))
print('average cost per day', round(totalPricePeriod / numberOfDays,2))
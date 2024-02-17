Download the NEM12 file from your electricity network provider, 

then you run

['./analysis_power.py -f /Users/jyavenard/Downloads/61022432106_20220216_20240216_20240217150241_CITIPOWER_DETAILED.csv -d 20230217:20240216 -c tariffEV.cfg']

the date there is the last 12 months.

this will output something like:

['total amount of days:  {'B1': 365, 'E1': 365}']
['Total for meter B1 tariff 1 2722.194 kWh -> $ 581.03']
['Total for meter B1 tariff 2 64.914 kWh -> $ 24.13']
['B1 total B1 is 2787.11 kWh $ 605.15']
['B1 average usage per day 7.636']
['B1 average cost per day 1.66']

['Total for meter E1 tariff 1 9044.664 kWh -> $ 1930.49']
['Total for meter E1 tariff 2 4518.329 kWh -> $ 1679.51']
['Total for meter E1 tariff 4 5883.722 kWh -> $ 470.7']
['E1 total E1 is 19446.72 kWh $ 4080.7']
['E1 average usage per day 53.279']
['E1 average cost per day 11.18']

['number of days in period 365']
['daily charge 397.485']

B1 for me is the solar export meter, the tariff will be all wrong, but the kWh will be correct, so I've exported 2787kWh of energy
E1 is the usage meter.
tariff 1 is off-peak
2: peak
3: should
4: super off-peak
5: free period if any

The important bit is creating a config file, there's two tables: weekday and off-peak (I first wrote this tool in 2010 when the charges was weekday vs weekend)

electricity is charged per 30 minutes window, set the tariff type for each window.

For a plain peak/off-peak check the tariffGloBird.cfg ; you only need to enter daily pricing, peak and off-peak price (in cents)

```
  "daily": 99,
  "pricing": [13.2, 24.31, 0, 0, 0],
```

this define a daily pricing of 99c
off-peak of 13.2.2
peak of 24.31

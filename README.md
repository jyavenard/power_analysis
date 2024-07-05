Download the NEM12 file from your electricity network provider, 

then you run

```
./analysis_power.py -f /path/to/CITIPOWER_DETAILED.csv -d 20230217:20240216 -c tariffEV.cfg
```


the date there is the last 12 months.

this will output something like:

```
period is 2023-07-04 00:00:00 to 2024-07-04 23:59:59 inclusive
total amount of days:  {'B1': 367, 'E1': 367}
Total for meter E1 tariff 1 15034.808 kWh -> $ 2133.44
Total for meter E1 tariff 2 5060.587 kWh -> $ 1441.76
E1 total E1 is 20095.4 kWh $ 3575.2
E1 average usage per day 54.756
E1 average cost per day $ 9.74

number of days in period 367
daily charge $ 528.847
Total export solar $ 1775.45
Total cost $ 2328.6
```

B1 for me is the solar export meter, modify config file accordingly.
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

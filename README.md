# Store-Monitoring

A Django Application to trigger report  and generate report of uptime and downtime of Stores.

1. /trigger_report endpoint that will trigger report generation from the data provided (stored in DB)
    1. No input 
    2. Output - report_id (random string) 
    3. report_id will be used for polling the status of report completion
2. /get_report endpoint that will return the status of the report or the csv
    1. Input - report_id
    2. Output
        - if report generation is not complete, return “Running” as the output
        - if report generation is complete, return “Complete” along with the CSV file with the schema described above.

## Demo Link

https://www.loom.com/share/803991f069794fd6b3313009016e1666

## Technologies

**Framework: DJANGO** <br>
**Database: PostgreSQL**

## Approach : Calculation of Uptime and Downtime

At any Point of Time,Store Status can be classfied into one of the three Possibilities: <br>
1. Unconfirmed Inactive
2. Confirmed Inactive
3. Active

From three possibilties of above we can determine the uptime and downtime.Interval between two status is termed as uptime or downtime as below:


1. Unconfirmed Inactive <-> Confirmed Inactive -> downtime
2. Confirmed Inactive <-> Unconfirmed Inactive -> downtime
3. Confirmed Inactive <-> Active -> downtime
4. Confirmed Inactive <-> Confirmed Inactive -> downtime
5. Unconfirmed Inactive <-> Active -> uptime
6. Active <-> Unconfirmed Inactive ->uptime

Dividing the intervals from the data accordingly and uptime ,downtime is calculated.

## Note

1. In the given data,Only active status are present but the application can also handle inactive statuses data.
2. If there are no records of status for a particular interval then it is assumed that store is offline and entire interval is considered as downtime.
3. It is also assumed that the status of stores are directly added into the database.So,importing or updating the polling data is not implemented.
4. For the static data,current timestamp is hard coded as max time from polling observations.

## Limitations and Further Improvements

As of Now,Report Generation takes roughly 6-8 mins but it can be improved using multithreading and caching.

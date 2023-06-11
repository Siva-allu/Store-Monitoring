from datetime import datetime,timedelta
from .models import Store,BusinessHours,PollingObservation,Report
from datetime import datetime,timedelta
from django.utils import timezone
import pytz
import json


class ReportGenerator:
    
    def __init__(self,reportId):
        self.stores=[]
        self.reportCompleted=False
        self.report=[]
        self.reportId=reportId
        self.currentTimestamp=datetime(2023, 1, 25, 18, 13, 22, 479220,tzinfo=pytz.utc)
        self.generateReport()
    
    # Calculates toatl time in a interval in seconds
    def getTimeDifference(self,time1,time2):
        seconds1=time1.hour*3600+time1.minute*60+time1.second
        seconds2=time2.hour*3600+time2.minute*60+time2.second
        return seconds2-seconds1 
        
    
    def generateReport(self):
        
        # Report Entry into the table with status Runinng
        report=Report(reportId=self.reportId,status='R',data='')
        report.save()
        
        # Retrieving all stores
        self.stores=Store.objects.all()
        for store in self.stores:
            # Converting current UTC time to Local Time Zone.
        
            localTimeZone=pytz.timezone(store.timezoneStr)
            endTimestamp=self.currentTimestamp.astimezone(localTimeZone)
            uptimeLastOneHour,downtimeLastOneHour=self.lastOnehourReport(store,localTimeZone,(endTimestamp-timedelta(hours=1)),endTimestamp)
            uptimeLastOneday,downtimeLastOneday=self.lastOneDayReport(store,localTimeZone,(endTimestamp-timedelta(days=1)),endTimestamp)
            uptimeLastOneWeek=[0]
            downtimeLastOneWeek=[0]
            self.lastOneWeekReport(store,localTimeZone,(endTimestamp-timedelta(weeks=1)),endTimestamp,uptimeLastOneWeek,downtimeLastOneWeek)
            self.report.append({
                'store_id':store.storeId,
                'uptime_last_hour':uptimeLastOneHour//60 ,
                'uptime_last_day':uptimeLastOneday,
                'uptime_last_week':uptimeLastOneWeek[0],
                'downtime_last_hour':downtimeLastOneHour//60,
                'downtime_last_day':downtimeLastOneday,
                'downtime_last_week':downtimeLastOneWeek[0]
            })
            
        # Updating Report Status    
        report.status='C'
        
        report.data=json.dumps(self.report)
        
        report.save()
        print("Saving Done")
        
        return report
        
    def lastOnehourReport(self,store,localTimezone,startTimestamp,endTimestamp):
        return self.calculateUptimeDownTime(store,localTimezone,startTimestamp,endTimestamp)
        
    def lastOneDayReport(self,store,localTimezone,startTimestamp,endTimestamp):
        uptimeLastOneDay=0
        downTimeLastOneDay=0
        if startTimestamp.date()<endTimestamp.date():
            temp=self.calculateUptimeDownTime(store,localTimezone,startTimestamp,datetime.combine(startTimestamp.date(),datetime.max.time(),localTimezone))
            uptimeLastOneDay+=temp[0]
            downTimeLastOneDay+=temp[1]
            temp=self.calculateUptimeDownTime(store,localTimezone,datetime.combine(endTimestamp.date(),datetime.min.time(),localTimezone),endTimestamp)
            uptimeLastOneDay+=temp[0]
            downTimeLastOneDay+=temp[1]
        else:
            uptimeLastOneDay,downTimeLastOneDay=self.calculateUptimeDownTime(store,localTimezone,startTimestamp,endTimestamp)
        return [uptimeLastOneDay//3600,downTimeLastOneDay//3600]
    
    # Using Recursive Approach
    def lastOneWeekReport(self,store,localTimezone,startTimestamp,endTimestamp,uptimeLastOneWeek,downtimeLastOneWeek):
        if startTimestamp.date()<endTimestamp.date():
            temp=self.calculateUptimeDownTime(store,localTimezone,startTimestamp,datetime.combine(startTimestamp.date(),datetime.max.time(),localTimezone))
            uptimeLastOneWeek[0]+=temp[0]//3600
            downtimeLastOneWeek[0]+=temp[1]//3600
            self.lastOneWeekReport(store,localTimezone,datetime.combine((startTimestamp+timedelta(days=1)).date(),datetime.min.time(),localTimezone),endTimestamp,uptimeLastOneWeek,downtimeLastOneWeek)
        else:
            temp=self.calculateUptimeDownTime(store,localTimezone,startTimestamp,endTimestamp)
            uptimeLastOneWeek[0]+=temp[0]//3600
            downtimeLastOneWeek[0]+=temp[1]//3600
            
        
    
    def calculateUptimeDownTime(self,store,localTimeZone,startTimestamp,endTimestamp):
        
        # Retrieving current day of the week from current local time.
        currentDay=startTimestamp.weekday()
        
        # Retrieving business hours for the current day of the week.
        businessHours=BusinessHours.objects.filter(storeId=store.storeId,day_of_week=currentDay)
        
        #print(businessHours)
        if businessHours.exists():
            businessHoursObject=businessHours.first()
            localStartTime=businessHoursObject.start_time_local
            localEndTime=businessHoursObject.end_time_local
        else:
            localStartTime=datetime(1990,1,1,0,0,0).time()
            localEndTime=datetime(1990,1,1,23,59,59).time()
        
        # Adjusting limits of last One Hour with local business hours.
        startTime=max(localStartTime,startTimestamp.time())
        endTime=min(localEndTime,endTimestamp.time())
        # print("StartTime",startTime,"End Time",endTime)
        # print("Local Start",localStartTime,"Local End",localEndTime)
        
        # Initializing uptimeLastHour and downtimeLastHour 
        uptime=0
        downtime=0
        
        # Retrieving last one hour observations form polling observations from current UTC time.
        observations=PollingObservation.objects.filter(storeId=store.storeId,timestamp_utc__gte=startTimestamp,timestamp_utc__lte=endTimestamp).order_by('timestamp_utc')
        
        # confirmed variable holdes whether at an instance whether store down or not.
        confirmed=False
        prevTime=startTime
        
        # Calculating uptime and downtime
        if startTime<endTime:
            for observation in observations:
                #print(observation.timestamp_utc.astimezone(localTimeZone))
                observationTime=observation.timestamp_utc.astimezone(localTimeZone).time()
                
                if confirmed:
                    downtime+=self.getTimeDifference(prevTime,observationTime)
                    if observation.status=='active':
                        confirmed=False
                    prevTime=observationTime
                else:
                    if observation.status=='active':
                        uptime+=self.getTimeDifference(prevTime,observationTime)
                        confirmed=False
                    else:
                        #print("down")
                        downtime+=self.getTimeDifference(prevTime,observationTime)
                        confirmed=True
                    prevTime=observationTime
            if observations.exists():
                if confirmed:
                    downtime+=self.getTimeDifference(prevTime,endTime)
                else:
                    uptime+=self.getTimeDifference(prevTime,endTime)
            else:
                downtime+=self.getTimeDifference(startTime,endTime)
        return [uptime,downtime]
        
        
def getReportStatus(reportId):
    try:
        report=Report.objects.get(reportId=reportId)
        print(report)
        return report.status
    except Report.DoesNotExist:
        return None

def getReportData(reportId):
    report=Report.objects.get(reportId=reportId)
    if report is None:
        return None
    return report.data
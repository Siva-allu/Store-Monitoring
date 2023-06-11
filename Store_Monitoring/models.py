from django.db import models

# Tables for storing the data

class Store(models.Model):
    
    storeId = models.BigIntegerField(primary_key=True)
    timezoneStr=models.CharField(max_length=255,default='America/Chicago')
    
    
class BusinessHours(models.Model):
    storeId = models.ForeignKey(Store, on_delete=models.CASCADE)
    day_of_week = models.IntegerField()
    start_time_local = models.TimeField(null=True, blank=True)
    end_time_local = models.TimeField(null=True, blank=True)


class PollingObservation(models.Model):
    storeId = models.ForeignKey(Store, on_delete=models.CASCADE)
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10)
    
class Report(models.Model):
    reportId=models.CharField(max_length=20,unique=True)
    statusChoices=[
        ('R','Running'),
        ('C','Completed')
    ]
    status=models.CharField(max_length=1,choices=statusChoices)
    data=models.TextField()
    
    
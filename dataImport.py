import csv
import django
django.setup()
from Store_Monitoring.models import Store, BusinessHours, PollingObservation
from django.utils import timezone
from datetime import datetime





 # Importing Polling data from CSV
def importPollingObservation(filePath):
    with open(filePath, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            storeID = int(row[0])
            currStatus=row[1]
            timestamp=row[2]
            timestampUTC=timezone.make_aware(datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S.%f %Z"),timezone.utc)
            store,created=Store.objects.get_or_create(storeId=storeID)
            pollingObservation = PollingObservation(
                storeId=store,
                timestamp_utc=timestampUTC,
                status=currStatus
            )
            pollingObservation.save()

importPollingObservation('C:\\Users\\sivaa\\Desktop\\store status.csv')


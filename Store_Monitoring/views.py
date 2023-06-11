# Necessary Imports

import time
import csv
import json
from django.db import models
from django.http import JsonResponse,HttpResponse
from Store_Monitoring.models import Store,BusinessHours,PollingObservation
from datetime import datetime,timedelta
from django.utils import timezone
import pytz
from .reportId import ReportIdGenerator
from .reportGenerator import ReportGenerator,getReportStatus,getReportData
from background_task import background
from django.shortcuts import render


reportIdGenerator = ReportIdGenerator()

# background function to run this asynchronously
@background
def generateReportUtil(reportId):
    try:
        print("Coming Here")
        report=ReportGenerator(reportId)
    except Exception as e:
        print(e)
        return JsonResponse({
            'error_message':"Somethin Went Wrong",
            'error_code':500
        })
        
# POST request  
def triggerReport(request):
    if request.method=='POST':
        try:
            reportId=reportIdGenerator.generateId()
            generateReportUtil(reportId)
            response=JsonResponse({
                "report_id":reportId
            })
        
            return render(request,'report.html',{
                'report_id':reportId,
                'error_message':"Report Triggered SucessFully"
            })
        except Exception as e:
            return JsonResponse({
                'error_message':"Somethin Went Wrong",
                    'error_code':500
            })
    else:
        return render(request,'landing.html',{
            'report_id':None
        })
    
# GET request
def getReport(request):
    try:
        reportId=request.GET.get('report_id')
        if not reportId:
            return render(request,'report.html',{
                'reportId':reportId,
                'error_message':"Report Id Missing",
                'error_code':400
            })
        reportStatus=getReportStatus(reportId)
        if not reportStatus:
            return render(request,'report.html',{
                'report_id':reportId,
                'error_message':"Invalid Report Id",
                'error_code':400
            })
    
        if reportStatus=='R':
            return render(request,'report.html',{
                'report_id':reportId,
                'error_message':"Running......",
                'error_code':200
            })
        elif reportStatus=='C':
            reportData=json.loads(getReportData(reportId))
            if reportData:
                response=HttpResponse(content_type='text/csv')
                fName=f"report_{reportId}.csv"
                response['Content-Disposition']=f'attachment;filename="{fName}"'
            
                writer=csv.writer(response)
            
                writer.writerow(reportData[0].keys())
            
                for row in reportData:
                    writer.writerow(row.values())
                return response
            else:
                return render(request,'report.html', {
                    'report_id':reportId,
                    'error_message':"Unable to retrieve report data",
                    'error_code':400
                })
        else:
            return render(request,'report.html',{
                'report_id':reportId,
                'error_message':"Invalid Report Status",
                'error_code':400
            })
    except Exception as e:
        return render(request,'report.html',{
            'report_Id':reportId,
            'error_message':"Something went Wrong",
            "error_code":500,
        })
        
    
    
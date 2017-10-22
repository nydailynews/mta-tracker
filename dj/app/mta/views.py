from django.shortcuts import render
from django.http import HttpResponse

def mode_index(request):
    return HttpResponse('hi')    

def mode_detail(request, mode):
    return HttpResponse('hi')    

def mode_archive_year(request):
    return HttpResponse('hi')    

def mode_archive_month(request):
    return HttpResponse('hi')    

def mode_archive_day(request):
    return HttpResponse('hi')    

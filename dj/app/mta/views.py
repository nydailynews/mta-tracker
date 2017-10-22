from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

def mode_index(request):
    return HttpResponseRedirect('/project/mta-delays/mta/')

def mode_detail(request, mode):
    return HttpResponse('hi')    

def mode_archive_year(request):
    return HttpResponse('hi')    

def mode_archive_month(request):
    return HttpResponse('hi')    

def mode_archive_day(request):
    return HttpResponse('hi')    

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
#from django.views.generic import TemplateView
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView


class ModeIndex(RedirectView):
    permanent = False
    query_string = True
    pattern_name = 'mode-index'

    def get_redirect_url(self, *args, **kwargs):
        return HttpResponseRedirect('/project/mta-delays/mta/')

class ModeDetail(TemplateView):
    template_name = 'mode/detail.html'

class ModeArchiveYear(RedirectView):
    #(request, mode, year):
    permanent = False
    query_string = True
    pattern_name = 'mode-archive-year'

    def get_redirect_url(self, *args, **kwargs):
        return HttpResponseRedirect('/project/mta-delays/mta/')

def mode_archive_month(request, mode, year, month):
    return HttpResponse('hi')    

def mode_archive_day(request, mode, year, month, day):
    return HttpResponse('hi')    

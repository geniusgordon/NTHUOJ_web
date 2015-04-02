'''
The MIT License (MIT)

Copyright (c) 2014 NTHUOJ team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import time
import random
from django.http import Http404
from django.utils import timezone
from utils.log_info import get_logger
from contest.models import Contest
from django.http import HttpResponse
from datetime import datetime, timedelta
from index.models import Announcement
from users.models import User, Notification
from django.shortcuts import render, redirect
from django.template import RequestContext
from utils.user_info import validate_user
from django.core.urlresolvers import reverse
from django.template import RequestContext
from index.forms import AnnouncementCreationForm

# Create your views here.
logger = get_logger()
def index(request, alert_info='none'):
    present = timezone.now()
    time_threshold = datetime.now() + timedelta(days=1);
    c_runnings = Contest.objects.filter \
        (start_time__lt=present, end_time__gt=present, is_homework=False)
    c_upcomings = Contest.objects.filter \
        (start_time__gt=present, start_time__lt=time_threshold, is_homework=False)
    announcements = Announcement.objects.filter \
        (start_time__lt=present, end_time__gt=present)
    return render(request, 'index/index.html',
                {'c_runnings':c_runnings, 'c_upcomings':c_upcomings,
                'announcements':announcements, 'alert_info':alert_info},
                context_instance=RequestContext(request, processors=[custom_proc]))

def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementCreationForm(request.POST)
        if form.is_valid():
            announcement = form.save()
            announcement.backend = 'django.contrib.auth.backends.ModelBackend'
            return redirect(reverse('index:index'))
    else:
        form = AnnouncementCreationForm()
    return render(request, 'index/announcement_create.html',
                {'form': form},
                context_instance=RequestContext(request, processors=[custom_proc]))

def custom_404(request):
    return render(request, 'index/404.html', status=404)

def custom_500(request):
    return render(request, 'index/500.html',{'error_message':'error'}, status=500)

def base(request):
    return render(request, 'index/base.html',{},
                context_instance=RequestContext(request, processors=[custom_proc]))

def get_time(request):
    t = time.time()
    tstr = datetime.fromtimestamp(t).strftime('%Y/%m/%d %H:%M:%S')
    return HttpResponse(tstr)

def custom_proc(request):

    amount = Notification.objects.filter \
        (receiver=request.user, read=False).count()

    t = time.time()
    tstr = datetime.fromtimestamp(t).strftime('%Y/%m/%d %H:%M:%S')
    people = random.randint(100,999)
    return {
        'tstr': tstr,
        'people': people,
        'amount': amount
    }

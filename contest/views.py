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
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.http import Http404
from django.shortcuts import render,get_object_or_404
from datetime import datetime
from index.views import custom_proc
from django.template import RequestContext
from django.forms.models import model_to_dict

from contest.models import Contest
from contest.models import Contestant
from contest.models import Clarification

from contest.forms import ContestForm

from contest.contest_info import get_contestant_list
from contest.contest_info import get_contest_submission_list
from contest.contest_info import get_penalty_scoreboard
from contest.contest_info import get_testcase_scoreboard
from contest.contest_info import get_contest_problem_passrate

from utils.log_info import get_logger
from utils import user_info


logger = get_logger()

def archive(request):
    #to store contest basic info and contestants
    contest_list = []
    #store contest basic info only
    contest_info_list = Contest.objects.order_by('-start_time')
    for contest in contest_info_list:
        contestants = Contestant.objects.filter(contest = contest)
        contest_list.append({'contest':contest,'contestants':contestants})

    user = request.user

    return render(request, 'contest/contestArchive.html',
        {'contest_list':contest_list,'user':user},
        context_instance = RequestContext(request, processors = [custom_proc]))

def contest(request,contest_id):

    serverTime = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    try:
        contest = Contest.objects.get(id = contest_id)
    except Contest.DoesNotExist: 
        logger.warning('Contest: Can not find contest %s!' % contest_id)
        raise Http404('Contest does not exist')
    
    clarification_list = Clarification.objects.filter(contest = contest)
    contestant_list = get_contestant_list(contest)
    
    ### get penalty scoreboard ###
    scoreboard = get_penalty_scoreboard(contest)

    ### get testcase scoreboard ###
    testcase_scoreboard = get_testcase_scoreboard(contest)

    ### get passrate info ###
    problem_pass_rate = get_contest_problem_passrate(contest)
    
    return render(request, 'contest/contest.html',{'contest':contest,'clarification_list':clarification_list,
        'contestant_list':contestant_list,'contestant_number':contestant_list.__len__(),
        'scoreboard':scoreboard,'testcase_scoreboard':testcase_scoreboard,
        'server_time':serverTime,'problem_pass_rate':problem_pass_rate},
        context_instance = RequestContext(request, processors = [custom_proc]))

def new(request):
    if request.user.has_judge_auth():
        if request.method == 'GET':
            form = ContestForm()
            return render(request,'contest/editContest.html',{'form':form})
        if request.method == 'POST':
            form = ContestForm(request.POST)
            if form.is_valid():
                new_contest = form.save()
                logger.info('Contest: Create a new contest %s!' % new_contest.id)
                return HttpResponseRedirect('/contest/')
    else:
        raise PermissionDenied
    

def edit(request,contest_id):
    try:
        contest = Contest.objects.get(id = contest_id)
    except Contest.DoesNotExist:
        logger.warning('Contest: Can not edit contest %s! Contest not found!' % contest_id)
        raise Http404('Contest does not exist, can not edit.')

    if user_info.has_c_ownership(request.user,contest):
        if request.method == 'GET':        
            contest_dic = model_to_dict(contest)
            form = ContestForm(initial = contest_dic)
            return render(request,'contest/editContest.html',{'form':form})
        if request.method == 'POST':
            form = ContestForm(request.POST, instance = contest)
            if form.is_valid():
                modified_contest = form.save()
                logger.info('Contest: Modified contest %s!' % modified_contest.id)
                return HttpResponseRedirect('/contest/')
    else:
        raise PermissionDenied

def delete(request,contest_id):
    try:
        contest = Contest.objects.get(id = contest_id)
    except Contest.DoesNotExist:
        logger.warning('Contest: Can not delete contest %s! Contest not found!' % contest_id)
        raise Http404('Contest does not exist, can not delete.')
    
    # only contest owner can delete
    if request.user == contest.owner:
        deleted_contest_id = contest.id
        contest.delete()
        logger.info('Contest: Delete contest %s!' % deleted_contest_id)
        return HttpResponseRedirect('/contest/')
    else:
        raise PermissionDenied

def register(request,contest_id):
    #check contest's existance
    try:
        contest = Contest.objects.get(id = contest_id)
    except Contest.DoesNotExist:
        logger.warning('Contest: Can not register contest %s! Contest not found!' % contest_id)
        raise Http404('Contest does not exist, can not register.')

    #check if user is not owner or coowner
    if not user_info.has_c_ownership(request.user,contest):
        #check contestant existance
        if Contestant.objects.filter(contest = contest,user = request.user).exists():
            #if user has attended
            logger.info('Contest: User %s has already attended Contest %s!' % (request.user.username,contest.id))
        else:
            contestant = Contestant(contest = contest,user = request.user)
            contestant.save()
            logger.info('Contest: User %s attends Contest %s!' % (request.user.username,contest.id))
    return HttpResponseRedirect('/contest/')
    

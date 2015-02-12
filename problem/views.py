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
from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect

from users.models import User
from problem.models import Problem, Tag, Testcase
from problem.forms import ProblemForm
from general_tools import log

import os
import json

logger = log.get_logger()

# Create your views here.
def problem(request):
    subjudge = request.user.has_subjudge_auth()
    my_problem = Problem.objects.filter(owner=request.user)
    all_problem = Problem.objects.all()
    return render(request, 'problem/panel.html', 
                  {'my_problem': my_problem, 'all_problem': all_problem, 'subjudge': subjudge})

def volume(request):
    problem_id=[]
    if Problem.objects.count() != 0:
        problems = Problem.objects.latest('id')
        volume_number = (problems.id - 1) // 100
        for i in range(1,volume_number + 2):
            start_id = ((i - 1) * 100 + 1)
            if problems.id < i * 100:
                end_id = problems.id
            else:
                end_id = i * 100
            problem_id.append(str(start_id) + ' ~ ' + str(end_id))

    return render(request, 'problem/category.html', {'problem_id':problem_id})

def detail(request, pid):
    user = request.user
    try:
        problem = Problem.objects.get(pk=pid)
    except Problem.DoesNotExist:
        logger.warning('problem: problem %s not found' % (pid))
        raise Http404("problem %s does not exist" % (pid))
    testcase = Testcase.objects.filter(problem=problem)
    tag = problem.tags.all()
    return render(request, 'problem/detail.html', 
                  { 'problem': problem, 'tag': tag, 'testcase': testcase })

def edit(request, pid):
    try:
        problem = Problem.objects.get(pk=pid)
        if not request.user.is_admin and request.user != problem.owner:
            logger.warning("user %s has no auth to edit problem %s" % (request.user, pid))
            raise Http404("you can't edit the problem")
    except Problem.DoesNotExist:
        logger.warning('problem: problem %s not found' % (pid))
        raise Http404("problem %s does not exist" % (pid))
    testcase = Testcase.objects.filter(problem=problem)
    tags = problem.tags.all()
    if request.method == 'GET':
        form = ProblemForm(instance=problem)
    if request.method == 'POST':
        form = ProblemForm(request.POST, instance=problem)
        if form.is_valid():
            problem = form.save()
            problem.description = request.POST['description']
            problem.input= request.POST['input_description']
            problem.output = request.POST['output_description']
            problem.sample_in = request.POST['sample_input']
            problem.sample_out = request.POST['sample_output']
            problem.save()
            logger.info('edit problem %s' % (pid))
            return redirect('/problem/%d' % (problem.pk))
    if not request.user.is_admin:
        del form.fields['owner']
    return render(request, 'problem/edit.html', 
                  { 'form': form, 'pid': pid, 'is_new': False, 'tags': tags,
                   'description': problem.description,
                   'input': problem.input, 'output': problem.output,
                   'sample_in': problem.sample_in, 'sample_out': problem.sample_out,
                   'testcase': testcase })

def new(request):
    if not request.user.has_subjudge_auth():
        logger.warning("user %s has no auth to add new problem" % (request.user))
        raise Http404("you can't add new problem")
    if request.method == 'GET':
        form = ProblemForm()
    if request.method == 'POST':
        print request.FILES
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save()
            problem.description = request.POST['description']
            problem.input= request.POST['input_description']
            problem.output = request.POST['output_description']
            problem.sample_in = request.POST['sample_input']
            problem.sample_out = request.POST['sample_output']
            problem.save()
            logger.info('post new problem, pid = %d' % (problem.pk))
            return redirect('/problem/%d' % (problem.pk))
    if not request.user.is_admin:
        del form.fields['owner']
    return render(request, 'problem/edit.html', { 'form': form, 'owner': request.user, 'is_new': True })

def tag(request, pid):
    if request.method == 'POST':
        tag = request.POST['tag']
        try:
            problem = Problem.objects.get(pk=pid)
        except Problem.DoesNotExist:
            logger.warning('problem: problem %s not found' % (pid))
            raise Http404("problem %s does not exist" % (pid))
        if not problem.tags.filter(tag_name=tag).exists():
            logger.info('add new tag "%s" to %s' % (request.POST['tag'], pid))
            new_tag, created = Tag.objects.get_or_create(tag_name=tag)
            problem.tags.add(new_tag)
            problem.save()
            return HttpResponse()
        return HttpResponseBadRequest()
    return HttpResponse()

def testcase(request, pid, tid=None):
    if request.method == 'POST':
        if tid == None:
            testcase = Testcase()
        else:
            testcase = Testcase.objects.get(pk=tid)
            logger.info('update test case, tid = %s' % (tid))
        try:
            testcase.problem = Problem.objects.get(pk=pid)
        except Problem.DoesNotExist:
            logger.warning('problem: problem %s not found' % (pid))
            raise Http404("problem %s does not exist" % (pid))
        if 'time_limit' in request.POST:
            testcase.time_limit = request.POST['time_limit']
            testcase.memory_limit = request.POST['memory_limit']
            testcase.save()
            logger.info('test case saved, tid = %s' % (testcase.pk))
        if 't_in' in request.FILES:
            with open('media/testcase/%s.in' % (testcase.pk), 'w') as t_in:
                for chunk in request.FILES['t_in'].chunks():
                    t_in.write(chunk)
            with open('media/testcase/%s.out' % (testcase.pk), 'w') as t_out:
                for chunk in request.FILES['t_out'].chunks():
                    t_out.write(chunk)
        return HttpResponse(json.dumps({'tid': testcase.pk}), content_type="application/json")
    return HttpResponse()

def preview(request):
    return render(request, 'problem/preview.html')

def delete_problem(request, pid):
    try:
        problem = Problem.objects.get(pk=pid)
        print 'request.user', request.user
        print 'problem.owner', problem.owner
        print request.user != problem.owner
        if not request.user.is_admin and request.user != problem.owner:
            logger.warning("user %s has no auth to delete problem %s" 
                           % (request.user, pid))
            raise Http404("you can't delete the problem")
        problem.delete()
        logger.info('problem %s deleted' % (pid))
    except Problem.DoesNotExist:
        logger.warning('problem: problem %s not found' % (pid))
        raise Http404("problem %s does not exist" % (pid))
    return redirect('/problem/')

def delete_tag(request, pid):
    pass

def delete_testcase(request, pid, tid):
    try:
        problem = Problem.objects.get(pk=pid)
        if not request.user.is_admin and request.user != problem.owner:
            logger.warning("user %s has no auth to edit problem %s" 
                           % (request.user, pid))
            raise Http404("you can't delete the testcase")
    except Problem.DoesNotExist:
        logger.warning('problem: problem %s not found' % (pid))
        raise Http404("problem %s does not exist" % (pid))
    try:
        Testcase.objects.get(pk=tid).delete()
        logger.info('testcase %s deleted' % (tid))
    except Testcase.DoesNotExist:
        logger.warning('problem: testcase %s not found' % (tid))
        raise Http404("testcase %s does not exist" % (tid))
    return redirect('/problem/%s/edit/' % (pid))


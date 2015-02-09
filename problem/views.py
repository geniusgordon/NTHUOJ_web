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
from django.http import HttpResponse, HttpResponseBadRequest
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
    a = {'name': 'my_problem', 'pid': 1, 'pass': 60, 'not_pass': 40}
    b = {'name': 'all_problem', 'pid': 1, 'pass': 60, 'not_pass': 40}
    return render(request, 'problem/panel.html', {'my_problem':[a,a,a], 'all_problem':[a,a,a,b,b,b]})

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

def detail(request, problem_id):
    problem = Problem.objects.get(pk=problem_id)
    testcase = Testcase.objects.filter(problem=problem)
    tag = problem.tags.all()
    return render(request, 'problem/detail.html', 
                  { 'problem': problem, 'tag': tag, 'testcase': testcase })

def edit(request, problem_id):
    logger.info('edit problem %s' % (problem_id))
    problem = Problem.objects.get(pk=problem_id)
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
            return redirect('/problem/%d' % (problem.pk))
    return render(request, 'problem/edit.html', 
                  { 'form': form, 'pid': problem_id, 'is_new': False, 'tags': tags,
                   'description': problem.description,
                   'input': problem.input, 'output': problem.output,
                   'sample_in': problem.sample_in, 'sample_out': problem.sample_out,
                   'testcase': testcase })

def new(request):
    if request.method == 'GET':
        form = ProblemForm()
    if request.method == 'POST':
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
    return render(request, 'problem/edit.html', { 'form': form, 'is_new': True })

def tag(request, problem_id):
    if request.method == 'POST':
        tag = request.POST['tag']
        problem = Problem.objects.get(pk=problem_id)
        if not problem.tags.filter(tag_name=tag).exists():
            logger.info('add new tag "%s" to %s' % (request.POST['tag'], problem_id))
            new_tag, created = Tag.objects.get_or_create(tag_name=tag)
            problem.tags.add(new_tag)
            problem.save()
            return HttpResponse()
        return HttpResponseBadRequest()
    return HttpResponse()

def testcase(request, problem_id, tid=None):
    if request.method == 'POST':
        if tid == None:
            logger.info('new test case')
            testcase = Testcase()
        else:
            logger.info('update test case, tid = %s' % (tid))
            testcase = Testcase.objects.get(pk=tid)
        testcase.problem = Problem.objects.get(pk=problem_id)
        if 'time_limit' in request.POST:
            testcase.time_limit = request.POST['time_limit']
            testcase.memory_limit = request.POST['memory_limit']
            testcase.save()
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


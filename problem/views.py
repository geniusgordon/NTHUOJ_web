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
from problem.models import Problem, Tag
from problem.forms import ProblemForm
from general_tools import log

import json

logger = log.get_logger()

# Create your views here.
def problem(request):
    a = {'name': 'my_problem', 'pid': 1, 'pass': 60, 'not_pass': 40}
    b = {'name': 'all_problem', 'pid': 1, 'pass': 60, 'not_pass': 40}
    return render(request, 'problem/panel.html', {'my_problem':[a,a,a], 'all_problem':[a,a,a,b,b,b]})

def detail(request, problem_id):
    logger.info('detail of problem %s' % (problem_id))
    problem = Problem.objects.get(pk=problem_id)
    tag = Tag.objects.all()
    return render(request, 'problem/detail.html', 
                  { 'problem': problem, 'tag': tag })

def edit(request, problem_id):
    logger.info('edit problem %s' % (problem_id))
    problem = Problem.objects.get(pk=problem_id)
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
    print problem.sample_in
    return render(request, 'problem/edit.html', 
                  { 'form': form, 'pid': problem_id, 
                   'description': problem.description,
                   'input': problem.input, 'output': problem.output,
                   'sample_in': problem.sample_in, 'sample_out': problem.sample_out })

def new(request):
    if request.method == 'GET':
        form = ProblemForm()
    if request.method == 'POST':
        logger.info('post new problem')
        form = ProblemForm(request.POST)
        if form.is_valid():
            problem = form.save()
            problem.description = request.POST['description']
            problem.input= request.POST['input_description']
            problem.output = request.POST['output_description']
            problem.sample_in = request.POST['sample_input']
            problem.sample_out = request.POST['sample_output']
            problem.save()
            return redirect('/problem/%d' % (problem.pk))
    return render(request, 'problem/edit.html', { 'form': form })

def tag(request, problem_id):
    if request.method == 'POST':
        logger.info('add new tag "%s" to %s' % (request.POST['tag'], problem_id))
        tag = request.POST['tag']
        if not Tag.objects.filter(tag_name=tag).exists():
            new_tag = Tag(tag_name=tag)
            new_tag.save()
            return HttpResponse()
        return HttpResponseBadRequest()
    return HttpResponse()

def testcase(request, problem_id):
    pass

def preview(request):
    return render(request, 'problem/preview.html')


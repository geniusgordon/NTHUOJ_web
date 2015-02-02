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
from django.shortcuts import render, redirect
from problem.models import Problem
from problem.forms import ProblemForm

# Create your views here.
def problem(request):
    a = {'name': 'my_problem', 'pid': 1, 'pass': 60, 'not_pass': 40}
    b = {'name': 'all_problem', 'pid': 1, 'pass': 60, 'not_pass': 40}
    return render(request, 'problem/panel.html', {'my_problem':[a,a,a], 'all_problem':[a,a,a,b,b,b]})

def detail(request, problem_id):
    print 'problem', problem_id
    problem = Problem.objects.get(pk=problem_id)
    return render(request, 'problem/detail.html', { 'problem': problem })

def edit(request, problem_id):
    return render(request, 'problem/edit.html')

def new(request):
    if request.method == 'GET':
        form = ProblemForm()
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        problem = form.save()
        problem.description = request.POST['description']
        problem.input_description = request.POST['input_description']
        problem.output_description = request.POST['output_description']
        problem.sample_input = request.POST['sample_input']
        problem.sample_output = request.POST['sample_output']
        problem.save()
        if form.is_valid():
            return redirect('/problem/'+str(problem.pk))
    return render(request, 'problem/edit.html', { 'form': form })

def preview(request):
    return render(request, 'problem/preview.html')


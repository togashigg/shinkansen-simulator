import os
import sys
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    # print("\nstart views.index()", file=sys.stderr)
    return html(request, 'index.html')

def html(request, filePath):
    # print("\nstart views.file(), filePath=" + filePath, file=sys.stderr)
    if(filePath == ''):
        filePath = 'index.html'
    contexts = {
        'PROJECT' : '東海道新幹線運行シミュレーター',
        'VL' : '0.1',
    }
    return render(request, filePath, contexts)

def json(request, filePath):
    # print("\nstart views.json(), filePath=" + filePath, file=sys.stderr)
    file_name = os.path.basename(filePath)
    f = open(os.path.join('cache', file_name), 'r')
    response = HttpResponse(f)
    response['content-type'] = 'application/json; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename=' + filePath
    return response

def csv(request, filePath):
    # print("\nstart view.csv(), filePath=" + filePath, file=sys.stderr)
    file_name = os.path.basename(filePath)
    f = open(os.path.join('cache', file_name), 'r')
    response = HttpResponse(f)
    response['content-type'] = 'text/csv; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename=' + filePath
    return response

def text(request, filePath):
    # print("\nstart view.text(), filePath=" + filePath, file=sys.stderr)
    file_name = os.path.basename(filePath)
    f = open(os.path.join('cache', file_name), 'r')
    response = HttpResponse(f)
    response['content-type'] = 'text/text; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename=' + filePath
    return response

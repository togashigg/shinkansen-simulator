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
    file_dict = {f:f for f in os.listdir('cache') if f[-5:] == '.json'}
    file_name = os.path.basename(filePath)
    if file_name not in file_dict:
        return HttpResponse(404)
    file_name = file_dict[file_name]
    f = open(os.path.join('cache', file_name), 'r')
    response = HttpResponse(f)
    response['content-type'] = 'application/json; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename=' + filePath
    return response

def csv(request, filePath):
    # print("\nstart view.csv(), filePath=" + filePath, file=sys.stderr)
    file_dict = {f:f for f in os.listdir('cache') if f[-4:] == '.csv'}
    file_name = os.path.basename(filePath)
    if file_name not in file_dict:
        return HttpResponse(404)
    file_name = file_dict[file_name]
    f = open(os.path.join('cache', file_name), 'r')
    response = HttpResponse(f)
    response['content-type'] = 'text/csv; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename=' + filePath
    return response

def text(request, filePath):
    # print("\nstart view.text(), filePath=" + filePath, file=sys.stderr)
    file_dict = {f:f for f in os.listdir('cache') if f[-4:] == '.txt'}
    file_name = os.path.basename(filePath)
    if file_name not in file_dict:
        return HttpResponse(404)
    file_name = file_dict[file_name]
    f = open(os.path.join('cache', file_name), 'r')
    response = HttpResponse(f)
    response['content-type'] = 'text/text; charset=utf-8'
    response['Content-Disposition'] = 'attachment; filename=' + filePath
    return response

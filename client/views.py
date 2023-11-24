from django.shortcuts import render, redirect
import requests
import json

api_key = "lm4OEj58.DViOKg0gSHE9AHMfSAIDQzRtzX5SBUft"
headers = {
  "Content-Type": "application/json",
  "Authorization": f"Api-Key {api_key}"
}

# Create your views here.
def index(request):
  url = f"{request.build_absolute_uri('/')}api/report"

  response = requests.request("GET", url, headers=headers)
  data = response.json()
  chart_data = []

  for category in data['categories']:
    chart_data.append({
      "name": category['name'],
      "y": category['value'],
      "color": category['color'],
      "formattedValue": category['formattedValue'],
    })

  chart_data[0]['sliced'] = True
  chart_data[0]['selected'] = True

  data.update({
    "chart_data": json.dumps(chart_data),
  })

  context = {
    'data': data
  }

  return render(request, 'client/index.html', context=context)

def update(request):
  url = f"{request.build_absolute_uri('/')}api/report"
  requests.request("POST", url, headers=headers)

  # redirect to index page
  return redirect('client:index')

def sync(request):
  url = f"{request.build_absolute_uri('/')}api/report"
  payload = {
    "incremental_update": True
  }

  requests.request(
    "POST",
    url,
    data=json.dumps(payload),
    headers=headers
  )

  # redirect to index page
  return redirect('client:index')
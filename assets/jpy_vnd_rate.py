import os
import requests

from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from .models import Report

load_dotenv()

class JPYVNDRate:
  def __init__(self):
    self.api_key = os.getenv('CURRENCY_RATE_API_KEY')
    self.url = f'http://api.exchangeratesapi.io/v1/latest?access_key={self.api_key}&symbols=JPY,VND'

  def __str__(self):
    return f'Currencies Exchange Rate API: {self.url}'

  def fetch(self):
    response = requests.request("GET", self.url)
    data = response.json()
    return data

  def get_jpy_vnd_rate(self):
    data = self.fetch()
    rate = round(data['rates']['VND'] / data['rates']['JPY'], 2)

    Report.objects.update_or_create(
      key='jpy_vnd_rate',
      defaults={
        "value": rate
      }
    )

    tzinfo = timezone(timedelta(hours=9))
    Report.objects.update_or_create(
      key='last_jpy_vnd_rate_updated_at',
      defaults={
        "value": datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S")
      }
    )

    return rate
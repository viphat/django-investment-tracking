import os
import requests
import json
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from .models import Category, Tag, InvestmentRecord, Report
from .utils import color_to_hex

load_dotenv()

class NotionClient:
  def __init__(self):
    self.token = os.getenv('NOTION_TOKEN')
    self.database_id = os.getenv('NOTION_DATABASE_ID')
    self.url = f'https://api.notion.com/v1/databases/{self.database_id}'

  def __str__(self):
    return f'NotionClient: {self.url}'

  def __headers(self):
    return {
      "Content-Type": "application/json",
      "Notion-Version": os.getenv('NOTION_API_VERSION'),
      "Authorization": f"Bearer {self.token}"
    }

  def fetch_meta_data_from_notion(self):
    response = requests.request("GET", self.url, headers=self.__headers())
    data = response.json()
    return data

  def fetch_raw_data_from_notion(self, incremental_update=False):
    hasMore = True
    start_cursor = None
    notion_record_ids = []

    while hasMore:
      data = self.fetch_raw_data_by_paging_cursor(start_cursor=start_cursor, incremental_update=incremental_update)
      for record in data['results']:
        notion_record_ids.append(record['id'])

      self.create_or_update_investment_records(data)
      hasMore = data['has_more']
      start_cursor = data['next_cursor']

    # Delete InvestmentRecord objects that are not in notion_record_ids
    if incremental_update == False:
      InvestmentRecord.objects.exclude(notionId__in=notion_record_ids).delete()

    tzinfo = timezone(timedelta(hours=9))
    Report.objects.update_or_create(
      key='last_synced_at',
      defaults={
        "value": datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S")
      }
    )

  def fetch_raw_data_by_paging_cursor(self, page_size=100, start_cursor=None, incremental_update=False):
    # Có thể Filter theo Updated Time
    payload = {
      "page_size": page_size,
      "sorts": [
        {
          "property": "Date",
          "direction": "descending"
        }
      ],
    }

    if incremental_update:
      last_synced_at = Report.objects.get(key='last_synced_at').value

      payload['filter'] = {
        "timestamp": "last_edited_time",
        "last_edited_time": {
          "on_or_after": datetime.strptime(last_synced_at, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
        }
      }

    if start_cursor:
      payload['start_cursor'] = start_cursor

    response = requests.request(
      "POST",
      self.url + '/query',
      data=json.dumps(payload),
      headers=self.__headers()
    )

    data = response.json()
    return data

  def create_or_update_investment_records(self, data):
    tzinfo = timezone(timedelta(hours=9))
    year = datetime.now(tzinfo).year

    for record in data['results']:
      investment, created = InvestmentRecord.objects.update_or_create(
        notionId=record['id'],
        defaults={
          "itemName": record['properties']['Item Name']['title'][0]['plain_text'],
          "itemDescription": record['properties']['Comment']['rich_text'][0]['plain_text'] if record['properties']['Comment']['rich_text'] else "",
          "category": Category.objects.get(notionId=record['properties']['Category']['select']['id']),
          "date": record['properties']['Date']['date']['start'],
          "amount": record['properties']['Amount']['number'],
          "currency": record['properties']['Currency']['select']['name'] or 'VND',
          "profitLoss": record['properties']['Profit/Loss']['number'] or 0,
          "year": record['properties']['Year']['number'] or year
        }
      )

      if not created:
        investment.tags.clear()

      tags = record['properties']['Tags']['multi_select']
      for tag in tags:
        investment.tags.add(Tag.objects.get(notionId=tag['id']))

      investment.save()


  def create_or_update_categories(self, data):
    categories = data['properties']['Category']['select']['options']

    for category in categories:
      try:
        cat = Category.objects.get(notionId=category['id'])
        cat.name = category['name']
        cat.color = color_to_hex(category['color'])
        cat.save()
      except Category.DoesNotExist:
        Category.objects.create(
          notionId=category['id'],
          name=category['name'],
          color=color_to_hex(category['color'])
        )

  def create_or_update_tags(self, data):
    tags = data['properties']['Tags']['multi_select']['options']

    for tag in tags:
      try:
        t = Tag.objects.get(notionId=tag['id'])
        t.name = tag['name']
        t.color = color_to_hex(tag['color'])
        t.save()
      except Tag.DoesNotExist:
        Tag.objects.create(
          notionId=tag['id'],
          name=tag['name'],
          color=color_to_hex(tag['color'])
        )
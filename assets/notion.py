import os
import requests
from dotenv import load_dotenv
from .models import Category, Tag
from .utils import color_to_hex

load_dotenv()

class NotionClient:
  def __init__(self):
    self.token = os.getenv('NOTION_TOKEN')
    self.database_id = os.getenv('NOTION_DATABASE_ID')
    self.url = f'https://api.notion.com/v1/databases/{self.database_id}'

  def __str__(self):
    return f'NotionClient: {self.url}'

  def fetch_data_from_notion(self):
    headers = {
      "Content-Type": "application/json",
      "Notion-Version": os.getenv('NOTION_API_VERSION'),
      "Authorization": f"Bearer {self.token}"
    }

    response = requests.request("GET", self.url, headers=headers)
    data = response.json()
    return data

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
          color=category['color']
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
          color=tag['color']
        )
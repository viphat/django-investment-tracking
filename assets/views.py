from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

from .models import Report, Category
from .notion import NotionClient
from .report import ReportService
from .jpy_vnd_rate import JPYVNDRate

# Create your views here.
class ReportApiView(APIView):
  def get(self, request):
    vnd_currency_format = "{:,} vnđ"

    data = {
      "total_amount": vnd_currency_format.format(
        Decimal(Report.objects.get(key='total_amount_in_vnd').value)
      ),
    }

    categories = Category.objects.all()
    for category in categories:
      data.update({
        f"{category.name}": {
          "value": vnd_currency_format.format(
            Decimal(Report.objects.get(key=f'total_amount_in_vnd_by_category_{category.id}').value)
          ),
          "percent": round(
            Decimal(Report.objects.get(key=f'total_amount_in_vnd_by_category_{category.id}').value) /
            Decimal(Report.objects.get(key='total_amount_in_vnd').value) * 100, 2
          )
        }
      })

    data.update({
      "last_synced_at": Report.objects.get(key='last_synced_at').value,
      "last_jpy_vnd_rate_updated_at": Report.objects.get(key='last_jpy_vnd_rate_updated_at').value,
      "last_report_updated_at": Report.objects.get(key='last_report_updated_at').value,
    })

    return Response(data, status=status.HTTP_200_OK)

  def post(self, request):
    notion_client = NotionClient()
    meta_data = notion_client.fetch_meta_data_from_notion()
    notion_client.create_or_update_categories(meta_data)
    notion_client.create_or_update_tags(meta_data)
    notion_client.fetch_raw_data_from_notion()
    currency_rate = JPYVNDRate()
    currency_rate.update_jpy_vnd_rate()
    report_service = ReportService()
    report_service.call()

    return Response(status=status.HTTP_200_OK)

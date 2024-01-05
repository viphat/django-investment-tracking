from datetime import datetime, timezone, timedelta
from .models import Category, InvestmentRecord, Report
from .jpy_vnd_rate import JPYVNDRate

class ReportService:
  def call(self):
    self.calculate_total_amount()
    self.calculate_total_amount_by_categories()

    tzinfo = timezone(timedelta(hours=9))
    Report.objects.update_or_create(
      key='last_report_updated_at',
      defaults={
        "value": datetime.now(tzinfo).strftime("%Y-%m-%d %H:%M:%S")
      }
    )

  def calculate_total_amount_by_categories(self):
    categories = Category.objects.all()
    jpy_vnd_rate = JPYVNDRate().get_jpy_vnd_rate()

    for category in categories:
      total_amount_in_vnd = 0
      records = InvestmentRecord.objects.filter(category=category)

      for record in records:
        if record.currency == 'JPY':
          total_amount_in_vnd += record.amount * jpy_vnd_rate
        else:
          total_amount_in_vnd += record.amount

      output = round(total_amount_in_vnd, 0)

      Report.objects.update_or_create(
        key=f'total_amount_in_vnd_by_category_{category.id}',
        defaults={
          "value": output
        }
      )

  def calculate_total_amount(self):
    total_amount_in_vnd = 0
    jpy_vnd_rate = JPYVNDRate().get_jpy_vnd_rate()

    for record in InvestmentRecord.objects.all():
      if record.currency == 'JPY':
        total_amount_in_vnd += record.amount * jpy_vnd_rate
      else:
        total_amount_in_vnd += record.amount

    output = round(total_amount_in_vnd, 0)

    Report.objects.update_or_create(
      key='total_amount_in_vnd',
      defaults={
        "value": output
      }
    )

    return output
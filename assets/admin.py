from django.contrib import admin
from django.http.request import HttpRequest
from .models import InvestmentRecord
# Register your models here.

# admin.site.register(InvestmentRecord)
@admin.register(InvestmentRecord)
class InvestmentRecordAdmin(admin.ModelAdmin):
  list_display = ('itemName', 'category', 'date', 'currency', 'formatted_amount', 'formatted_profit_loss', 'year')
  list_filter = ('category', 'year', 'currency')
  ordering = ('-date',)

  def has_delete_permission(self, request, obj=None):
    return False

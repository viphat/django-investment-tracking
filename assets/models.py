from django.db import models

class Category(models.Model):
  notionId = models.CharField(max_length=255, blank=False, null=False)
  name = models.CharField(max_length=255, blank=False, null=False)
  color = models.CharField(max_length=100)

  def __str__(self):
    return self.name

class Tag(models.Model):
  notionId = models.CharField(max_length=255, blank=False, null=False)
  name = models.CharField(max_length=255, blank=False, null=False)
  color = models.CharField(max_length=100)

  def __str__(self):
    return self.name

class InvestmentRecord(models.Model):
  notionId = models.CharField(max_length=255, blank=False, null=False)
  itemName = models.TextField(blank=False, null=False)
  itemDescription = models.TextField(blank=True, null=True)
  category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=False, null=False)
  tags = models.ManyToManyField(Tag)
  date = models.DateField(blank=False, null=False)
  currency = models.CharField(max_length=3, blank=False, null=False)
  amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False, null=False)
  profitLoss = models.DecimalField(max_digits=15, decimal_places=2)
  year = models.IntegerField(blank=False, null=False)

  def __str__(self):
    return "{p1}: {p2}".format(p1=self.itemName, p2=self.amount)

class Report(models.Model):
  key = models.CharField(max_length=255, blank=False, null=False, unique=True)
  value = models.TextField(blank=False, null=False)

  def __str__(self):
    return "{p1}: {p2}".format(p1=self.key, p2=self.value)
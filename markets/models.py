from django.db import models

# Create your models here.
class Stocks(models.Model):
    isin_number = models.CharField(primary_key=True, max_length=15)
    company_name = models.CharField(max_length=100)
    bse_symbol = models.CharField(max_length=6, unique=True, null=True)
    nse_symbol = models.CharField(max_length=20, unique=True, null=True)
    
    class Meta:
        db_table = 'Stocks'


class StockPrice(models.Model):
    stock = models.ForeignKey(Stocks, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    last_price = models.FloatField()
    open = models.FloatField()
    day_high = models.FloatField()
    day_low = models.FloatField()
    previous_close = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('stock', 'datetime')
        db_table = 'StockPrices'
    

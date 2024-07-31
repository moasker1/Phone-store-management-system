from django.db import models
from django.utils import timezone
from django.db.models import Sum ,F, DecimalField , ForeignKey
from decimal import Decimal
from django.contrib.auth.models import User

# ===============================================================================================
class Client(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    notes = models.CharField(max_length=100, blank=True, null=True)

    @property
    def rest(self):
        total_remain = self.sale_set.aggregate(models.Sum('remain'))['remain__sum'] or 0
        return total_remain + self.opening_balance
# ===============================================================================================
class Supplier(models.Model):
    name = models.CharField(max_length=100,blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    for_him = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
# ===============================================================================================
class Kind(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
# ===============================================================================================
class Item(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    kind = models.ForeignKey(Kind, on_delete=models.CASCADE, null=True)
    prand = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
# ===============================================================================================
class Lose(models.Model):
    lose_type = models.CharField(max_length=100, blank=True, null=True)
    lose_money = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=100, blank=True, null=True)
# ===============================================================================================
class Daycome(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    loses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payments = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    win = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cash = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    wallet = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
# ===============================================================================================
class Safe(models.Model):
    wallet = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def wallet_paid(self):
        return Sale.objects.filter(method='محفظة').aggregate(total_paid=Sum('paid'))['total_paid'] or 0  
    
    @property
    def cash_paid(self):
        return Sale.objects.filter(method='نقدية').aggregate(total_paid=Sum('paid'))['total_paid'] or 0
    
    @property
    def wallet_total(self):
        wallet_sum = Sale.objects.filter(method='محفظة').aggregate(total_paid=Sum('paid'))['total_paid'] or 0
        return wallet_sum + self.wallet 
    
    @property
    def cash_total(self):
        cash_sum = Sale.objects.filter(method='نقدية').aggregate(total_paid=Sum('paid'))['total_paid'] or 0
        return cash_sum + self.cash 
    

# ===============================================================================================
class Sale(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    client_name = models.CharField(max_length=100, blank=True, null=True)
    client_phone = models.CharField(max_length=100, blank=True, null=True)
    crash = models.CharField(max_length=100, blank=True, null=True)
    method = models.CharField(max_length=100, choices=(('محفظة', 'محفظة'), ('نقدية', 'نقدية')), default='نقدية')  # Use choices for 'method'
    date = models.DateTimeField(blank=True, null=True)
    sale_quantity = models.PositiveIntegerField(blank=True, null=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paid = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remain = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        price_float = Decimal(self.sale_price)
        quantity_float = Decimal(self.sale_quantity)
        paid_float = Decimal(self.paid)
        self.total = price_float * quantity_float
        total_float = Decimal(self.total)
        self.remain = total_float - paid_float
        super().save(*args, **kwargs)
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
# ===============================================================================================
class Payment(models.Model):
    date = models.DateTimeField(blank=True, null=True)
    paid_money = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
# ===============================================================================================
class RecentAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100,blank=True, null=True)  
    action_sort = models.CharField(max_length=100,blank=True, null=True)  
    model_affected = models.CharField(max_length=100,blank=True, null=True)  
    timestamp = models.DateTimeField(blank=True, null=True)
# ===============================================================================================


from django.db import models
from accounts.models import UserBankAccount # karon okhane balance chilo jeta mader lagbe transaction er por por balance update hbe tai
from .constants import TRANSACTION_TYPE
# Create your models here.

class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, related_name='transactions',
              on_delete=models.CASCADE)#user er multiple transatction hote pare ty one to many=foreigh key use kora
    
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12)
    # transaction_type = models.CharField(max_length=100, choices=TRANSACTION_TYPE, null=True)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null = True)
    timestamp = models.DateField(auto_now_add= True )
    loan_approve = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
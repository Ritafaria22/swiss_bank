from django.db import models
from django.contrib.auth.models import User #django built models theke user model nilam-name,email,password etc.
from .constants import ACCOUNT_TYPE, GENDER_TYPE
# Create your models here.

class UserBankAccount(models.Model):
    user = models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)#ontoone with django builtin models er sate amr add kora extra field gula. city,gender etc.karon User alada ekta model
    account_type = models.CharField(max_length=10, choices = ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True)
    birthdate = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices = GENDER_TYPE)
    initial_deposit_date = models.DateField(auto_now=True) 
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    def __str__(self):
        return str(self.account_no)
    
class UserAddress(models.Model):
    user = models.OneToOneField(User, related_name='address', on_delete=models.CASCADE)#related name er karone address field diye user er baki information access korte parbo
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=100)


    def __str__(self):
        return str(self.user.email)



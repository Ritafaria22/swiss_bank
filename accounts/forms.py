from django.contrib.auth.forms import UserCreationForm
from .constants import ACCOUNT_TYPE, GENDER_TYPE
from django import forms
from django.contrib.auth.models import User
from .models import UserBankAccount, UserAddress



class UserRegistrationForm(UserCreationForm):
    birthdate =  forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField (choices = GENDER_TYPE)
    account_type = forms.ChoiceField(choices = ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    
    class Meta:
        model = User  #User model k anlam
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 
                  'account_type', 'birthdate', 'gender', 'postal_code','city',  'country', 'street_address'] #password2 holo confirm password 
    
    def save(self, commit=True):
        #super keyword diye usermodel er data inherit korlam
        our_user = super().save(commit=False)#ei line er mane ami database a akhn data save korbo na
        if commit == True: #amn hotei pare j user commit false diye rakse mane data save kore ni
            our_user.save() #user model a data save korlam
            account_type = self.cleaned_data.get('account_type') #user form fill er por cleaned data theke accounttype field er data pelam
            gender = self.cleaned_data.get('gender') #user form fill er por cleaned data theke gender field er data pelam
            postal_code = self.cleaned_data.get('postal_code') #cleaned data theke accounttype field er data pelam
            country = self.cleaned_data.get('country') #cleaned data theke country field er data pelam
            birthdate = self.cleaned_data.get('birthdate') #cleaned data theke birthdate field er data pelam
            city = self.cleaned_data.get('city') #cleaned data theke birthdate field er data pelam
            
            street_address = self.cleaned_data.get('street_address') #cleaned data theke birthdate field er data pelam

            
            UserAddress.objects.create( # user er ekta obj toiri korlo
                user = our_user,
                postal_code = postal_code,
                country = country,
                city = city ,
                street_address = street_address
          
            ) 

            UserBankAccount.objects.create(
                user = our_user,
                account_type  = account_type ,
                gender = gender, 
                birthdate = birthdate,
                account_no = 100000 + our_user.id
            )
        return our_user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields: #for design in frontend
            self.fields[field].widget.attrs.update({
                'class' : ( #backend theke class ad kore dilam
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })


# profile ki ki jinis update korte parbe amader user

class UserUpdateForm(forms.ModelForm):
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type':'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length= 100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
        # jodi user er account thake 
        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
            except UserBankAccount.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender
                self.fields['birthdate'].initial = user_account.birthdate
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserBankAccount.objects.get_or_create(user=user) # jodi account thake taile seta jabe user_account ar jodi account na thake taile create hobe ar seta created er moddhe jabe
            user_address, created = UserAddress.objects.get_or_create(user=user) 

            user_account.account_type = self.cleaned_data['account_type']
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()

            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.country = self.cleaned_data['country']
            user_address.save()

        return user




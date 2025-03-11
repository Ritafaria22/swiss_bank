from django.shortcuts import render
from django.views.generic import CreateView, ListView
from .models import Transaction
from django.contrib.auth.mixins import LoginRequiredMixin #sudhu matro login user varify korar jnno
from .forms import DepositForm, WithdrawForm, LoanRequestForm
from .constants import DEPOSIT, WITHDRAWAL,LOAN, LOAN_PAID
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string



def send_transaction_email(user, amount, subject,template ):
      
      message = render_to_string(template, {
            'user' :  user,
            'amount' : amount,
    })
      
      send_email = EmailMultiAlternatives(subject, '', to=[user.email])
      send_email.attach_alternative(message, "text/html")
      send_email.send()



#ei view k use kore deposit,loan ,withdraw request er kaj korbo
class TransactionCreationMixin(LoginRequiredMixin,CreateView):
    template_name = 'transactions/transaction_form.html'
    model = Transaction 
    title = ''
    success_url = reverse_lazy('transaction_report')

    def get_form_kwargs(self):#user k account pass korlam. j account diye form a seta accept kortesi pop kore
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account' : self.request.user.account,
        })
        return kwargs 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title' : self.title
        })

        return context

class DepositMoneyView(TransactionCreationMixin):
    form_class = DepositForm
    title = "Deposit"

    #form a by default form ta deposit er thakbe 
    def get_initial(self):
        initial = {'transaction_type' : DEPOSIT }
        return initial

    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account # j user use korvhe tar account nilam
        account.balance +=  amount #deposit er por balance update korlam
        account.save(
            update_fields = ['balance']
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )

        send_transaction_email(self.request.user, amount, "deposi message", "transactions/deposite_email.html" )
        return super().form_valid(form)

 
class WithdrawMoneyView(TransactionCreationMixin):
    form_class = WithdrawForm
    title = "Withdraw money"

    #form a by default form ta deposit er thakbe 
    def get_initial(self):
        initial = {'transaction_type' : WITHDRAWAL }
        return initial

    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account # j user use korvhe tar account nilam
        account.balance -=  amount #deposit er por balance update korlam
        account.save(
            update_fields = ['balance']
        )

        messages.success(
            self.request,
            f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account'
        )
        send_transaction_email(self.request.user, amount, "Withdrawal Message", "transactions/withdrawal_email.html")
        return super().form_valid(form)
    

class LoanRequestView(TransactionCreationMixin):
    form_class = LoanRequestForm
    title = "Request for loan"

    #form a by default form ta deposit er thakbe 
    def get_initial(self):
        initial = {'transaction_type' : LOAN }
        return initial

    def form_valid(self,form):
        amount = form.cleaned_data.get('amount')
        current_loan_count = Transaction.objects.filter(account = self.request.user.account,
        transaction_type = LOAN , loan_approve = True).count()#loan approve hole loan count barbe ei line diye

        if current_loan_count >= 3:
            return HttpResponse("you cannot take load more than 3 time. limit exceed!")
        
        messages.success(
            self.request,
            f'Loan request for {"{:,.2f}".format(float(amount))}$ submitted successfully'
        )

        send_transaction_email(self.request.user, amount, "Loan Request Message", "transactions/loan_email.html")
        return super().form_valid(form)
    
class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "transactions/transaction_report.html"
    model = Transaction
    balance = 0
    context_object_name = 'report_list'

    #jodi user kono filter mane startdate, enddate select na kore tyle
    #  user er shob transation list dekhabo
    def get_queryset(self):
        queryset = super().get_queryset().filter(
            account = self.request.user.account) # kon user account er seta filter
         
        #get url er maddhome parameter pass korte hy
        start_date_str = self.request.GET.get('start_date')# kono data get korle seta string format ei thake tai str use koresi
        end_date_str = self.request.GET.get('end_date')# kono data get korle seta string format ei thake tai str use koresi
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() #string format k date format a nite strptime use korsi
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() #string format k date format a nite strptime use korsi
            #user jodi filter kore tyle oi timedate er transaction list dekhabo sudu
            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)  #mane 2022 too 2024 data show krbe. 2024 to 2022 show korbena
            
             #user jodi filter kore tyle oi timedate er transaction list dekhabo sudu
            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']
        
        #jodi user kono filter mane startdate, enddate select na kore tyle
        #user er  total balance dekhabo
        else:
            self.balance = self.request.user.account.balance
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account' : self.request.user.account
        })
        return context
    
class PayLoanView(LoginRequiredMixin, View):
    #user kon loan pay korte chaai setar jnno 
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id = loan_id)#jodi loan_id wala kono loan k pai tyle dekhabo.na thakle nai blbo. r id builtin id django er
        print(loan)
        if loan.loan_approve: #mane jodi loan approve hye thake taholei user loan pay korte parbe
            user_account = loan.account 
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
        else:
            messages.error(self.request, f"loan amount is greater than your available balance")
            return redirect('loan_list')


class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transactions/loan_request.html"
    context_object_name = 'loans'

    def get_queryset(self):
         user_account = self.request.user.account
         queryset = Transaction.objects.filter(account = user_account, transaction_type = 3 )
         return queryset






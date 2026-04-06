
from django import forms
from .models import Branch, Fund, Expense, ExpenseCategory, OtherIncome, IncomeCategory, SupplierPayment, CustomerPayment, FundTransfer



class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = "__all__" 


class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        fields= ['fund_name', 'fund_type', 'amount', 'description']



class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'})
        }
        labels = {
            'name': 'Category Name'
        }
        

class ExpenseForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Expense
        fields = ['category', 'fund', 'amount', 'date', 'note']
        
        
class OtherIncomeForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = OtherIncome
        fields = ['category', 'fund', 'amount', 'date', 'note']
        
class IncomeCategoryForm(forms.ModelForm):
    class Meta:
        model = IncomeCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter income category name'})
        }
        labels = {
            'name': 'Income Category Name'
        }
        
class SupplierPaymentForm(forms.ModelForm):
    class Meta:
        model = SupplierPayment
        fields = ['supplier', 'fund', 'amount',  'note']
        
class CustomerPaymentForm(forms.ModelForm):
    class Meta:
        model = CustomerPayment
        fields = ['customer', 'fund', 'amount',  'note']


class FundTransferForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = FundTransfer
        fields = ['from_fund', 'to_fund', 'amount', 'date', 'note']        


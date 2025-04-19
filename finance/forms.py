from django import forms
from .models import Category, Income, Transaction
from django.contrib.auth.models import User

from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1','password2']



class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter category name'})
        }

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'date', 'type', 'category']  # Include 'category' but we will conditionally remove it in the form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If the transaction type is 'income', remove the category field
        if self.instance and self.instance.type == 'income':
            self.fields.pop('category', None)
    
class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'date']  # include 'category' field

class AccountSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email'] 
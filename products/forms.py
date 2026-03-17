
from django import forms
from .models import Category, Product



    #--------------------------- Category and Product ------------------------

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'description': forms.TextInput(attrs={'class':'form-control', 'rows':3}),
        }
        

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__" 

from django import forms
from .models import Document,CustomUser
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username','email','password1','password2')


    def save(self,commit=True):
        user = super().save(commit=False)
        user.role = 'editor'
        if commit:
            user.save()
        return user


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'category', 'file']
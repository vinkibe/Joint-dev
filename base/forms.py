from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Room, User, CodeSnippet, Document

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']

class CodeSnippetForm(forms.ModelForm):
    class Meta:
        model = CodeSnippet
        fields = ['code']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'file')


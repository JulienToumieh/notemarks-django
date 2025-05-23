from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Book, Notemark
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class NotemarkForm(forms.ModelForm):
    class Meta:
        model = Notemark
        fields = [
            'title',
            'chapter',
            'page',
            'color',
            'favourite',
            'tags',
            'contents',
            'book',
        ]
        widgets = {
            'tags': forms.CheckboxSelectMultiple(),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def clean_page(self):
        page = self.cleaned_data.get('page')
        if page < 1:
            raise forms.ValidationError("Page number must be at least 1.")
        return page




class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 
            'description', 
            'authors', 
            'cover_image', 
            'pages', 
            'status', 
            'rating', 
            'favourite', 
            'user', 
            'categories'
        ]
        
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is not None and (rating < 0 or rating > 5):
            raise forms.ValidationError("Rating must be between 0 and 5.")
        return rating


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
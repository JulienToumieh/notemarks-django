from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Book

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
        
    # You can add custom validation here if needed
    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 0 or rating > 5:
            raise forms.ValidationError("Rating must be between 0 and 5.")
        return rating



class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
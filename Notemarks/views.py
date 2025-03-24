from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import BookForm
from .models import Book


def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success_url')  # Replace with the correct redirect URL after saving
    else:
        form = BookForm()

    return render(request, 'books.html', {'form': form})



def books(request):
    # Query all books
    books = Book.objects.all()
    
    # Pass the books to the template
    return render(request, 'books.html', {'books': books})


def book(request, id):
    # Get the book object by its ID or return a 404 if not found
    book = get_object_or_404(Book, id=id)
    
    # Pass the book object to the template
    return render(request, 'book.html', {'book': book})




def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Replace 'home' with your desired redirect target
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import BookForm
from .models import Book, Notemark, Tag
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from .forms import NotemarkForm
from django.db.models import Q


@login_required 
def add_notemark(request):
    if request.method == 'POST':
        print(request.POST)  # Debugging: Check what data is being sent
        form = NotemarkForm(request.POST)

        if form.is_valid():
            book_id = request.POST.get('book_id')
            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                print(f"Book with ID {book_id} does not exist.")  # Debugging
                return render(request, 'book.html', {'form': form, 'tags': Tag.objects.all(), 'error': f"Book with ID {book_id} not found"})

            # Save the Notemark
            notemark = form.save(commit=False)
            notemark.book = book  # Associate with book
            notemark.save()

            # Handle many-to-many field (tags)
            tags = request.POST.getlist('tags')
            notemark.tags.set(tags)  # Set the ManyToMany field properly

            print("Notemark successfully created!")  # Debugging confirmation

            return redirect('book', id=book.id)
        else:
            print("Form is not valid:", form.errors)  # Debugging line

    else:
        form = NotemarkForm()

    return render(request, 'book.html', {'form': form, 'tags': Tag.objects.all()})

@login_required
def delete_notemark(request, notemark_id):
    # Get the notemark by ID
    notemark = get_object_or_404(Notemark, id=notemark_id)
    
    # Check if the logged-in user is the one who added the notemark (optional)
    if notemark.book.user != request.user:
        # Redirect to a page with an error message (optional)
        messages.error(request, "You don't have permission to delete this notemark.")
        return redirect('book', id=notemark.book.id)

    # Delete the notemark
    notemark.delete()

    # Redirect to the book page after deletion
    messages.success(request, "Notemark deleted successfully!")
    return redirect('book', id=notemark.book.id)


@login_required  # Ensure the user is logged in
def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        description = request.POST.get('description')
        cover_image = request.FILES.get('cover_image')  # Handle file upload
        cover_image_path = None

        # Save the uploaded image to the MEDIA_ROOT directory
        if cover_image:
            fs = FileSystemStorage()
            cover_image_path = fs.save(f'cover_images/{cover_image.name}', cover_image)

        # Debugging: Print the values being used to create the book
        print(f"Title: {title}, Authors: {authors}, Description: {description}, Cover Image: {cover_image_path}")

        try:
            # Create the book entry with the saved image path and user
            book = Book.objects.create(
                title=title,
                authors=authors,
                description=description,
                cover_image=cover_image_path,  # Store only the relative path
                user=request.user  # Associate the book with the logged-in user
            )
            print(f"Book Created: {book.title} by {book.authors}")  # Debugging message

            # Success message
            messages.success(request, f'Book "{book.title}" has been added successfully!')

            return redirect('books')  # Adjust to your desired redirect
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debugging message
    return render(request, 'books.html')

@login_required
def delete_book(request, book_id):
    # Get the book by ID
    book = get_object_or_404(Book, id=book_id)
    
    # Check if the logged-in user is the one who added the book (optional)
    if book.user != request.user:
        # Redirect to a page with an error message (optional)
        messages.error(request, "You don't have permission to delete this book.")
        return redirect('books')

    # Delete the book
    book.delete()

    # Redirect to a page (books list or wherever you want after deletion)
    messages.success(request, "Book deleted successfully!")
    return redirect('books')

def books(request):
    search_term = request.GET.get('search', '')  # Get the search term from the query string
    if search_term:
        # Filter books by title or authors containing the search term
        books = Book.objects.filter(
            Q(title__icontains=search_term) | Q(authors__icontains=search_term)
        )
    else:
        # If no search term, return all books
        books = Book.objects.all()

    context = {
        'books': books,
        'MEDIA_URL_BASE': settings.MEDIA_URL_BASE,  # Pass the MEDIA_URL from settings
    }
    
    return render(request, 'books.html', context)


@login_required
def book(request, id):
    # Get the book object by its ID or return a 404 if not found
    book = get_object_or_404(Book, id=id)

    # Get the search term for notemarks from the query string
    search_term = request.GET.get('search', '')

    # Filter notemarks based on title or contents if a search term is provided
    if search_term:
        notemarks = Notemark.objects.filter(
            book=book
        ).filter(
            Q(title__icontains=search_term) | Q(contents__icontains=search_term)
        )
    else:
        # If no search term, fetch all notemarks for the book
        notemarks = Notemark.objects.filter(book=book)

    context = {
        'book': book,
        'notemarks': notemarks,  # Pass the filtered notemarks to the template
        'MEDIA_URL_BASE': settings.MEDIA_URL_BASE,  # Pass the MEDIA_URL from settings
    }

    # Pass the book and notemarks to the template
    return render(request, 'book.html', context)




def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('books')  # Replace 'home' with your desired redirect target
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})
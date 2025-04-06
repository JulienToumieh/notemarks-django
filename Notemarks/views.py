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
from .models import Category
from django.contrib import messages
from django.contrib.auth import logout

@login_required
def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_color = request.POST.get('category_color')

        # Create and save the new category
        category = Category.objects.create(name=category_name, color=category_color)

        # Success message
        messages.success(request, f'Category "{category.name}" created successfully!')

        return redirect('books')  # Adjust to redirect to the appropriate page (e.g., books list)

    return redirect('books')  # Handle case for non-POST requests

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

        # Get the selected categories from the POST data (assuming you have checkboxes for categories)
        category_ids = request.POST.getlist('categories')  # Get a list of selected category IDs
        categories = Category.objects.filter(id__in=category_ids)  # Get the Category objects

        # Debugging: Print the values being used to create the book
        print(f"Title: {title}, Authors: {authors}, Description: {description}, Cover Image: {cover_image_path}")
        print(f"Selected Categories: {categories}")

        try:
            # Create the book entry with the saved image path and user
            book = Book.objects.create(
                title=title,
                authors=authors,
                description=description,
                cover_image=cover_image_path,  # Store only the relative path
                user=request.user  # Associate the book with the logged-in user
            )

            # Associate the selected categories with the book (ManyToManyField)
            book.categories.set(categories)  # Use set to properly associate categories

            print(f"Book Created: {book.title} by {book.authors}")  # Debugging message

            # Success message
            messages.success(request, f'Book "{book.title}" has been added successfully!')

            return redirect('books')  # Adjust to your desired redirect
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debugging message

    # Render the form, passing categories to the template for selection
    categories = Category.objects.all()
    return render(request, 'books.html', {'categories': categories})

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


@login_required
def books(request):
    categories = Category.objects.all()  # Get all categories
    search_term = request.GET.get('search', '')  # Get the search term from the query string
    sort_direction = request.GET.get('sort', 'asc')  # Default sort is ascending

    if search_term:
        # Filter books by title or authors containing the search term
        books = Book.objects.filter(
            Q(title__icontains=search_term) | Q(authors__icontains=search_term)
        )
    else:
        # If no search term, return all books
        books = Book.objects.all()

    # Sort the books based on the sort direction
    if sort_direction == 'desc':
        books = books.order_by('-title')  # Adjust this field to whatever you want to sort by
    else:
        books = books.order_by('title')  # Adjust this field to whatever you want to sort by

    context = {
        'books': books,
        'categories': categories,
        'MEDIA_URL_BASE': settings.MEDIA_URL_BASE,  # Pass the MEDIA_URL from settings
        'sort_direction': sort_direction,  # Pass sort direction to template if needed
    }
    
    return render(request, 'books.html', context)


@login_required
def book(request, id):
    # Get the book object by its ID or return a 404 if not found
    book = get_object_or_404(Book, id=id)
    tags = Tag.objects.all()

    # Get the search term for notemarks from the query string
    search_term = request.GET.get('search', '')

    # Get the sort direction for notemarks from the query string, default is 'asc'
    notemarks_sort_direction = request.GET.get('notemarks_sort', 'asc')

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

    # Sort the notemarks based on the sort direction
    if notemarks_sort_direction == 'desc':
        notemarks = notemarks.order_by('-title')  # Change this field as needed
    else:
        notemarks = notemarks.order_by('title')  # Change this field as needed

    context = {
        'book': book,
        'notemarks': notemarks,  # Pass the sorted notemarks to the template
        'MEDIA_URL_BASE': settings.MEDIA_URL_BASE,  # Pass the MEDIA_URL from settings
        'tags': tags,
        'notemarks_sort_direction': notemarks_sort_direction  # Pass sort direction to the template
    }

    # Pass the book and notemarks to the template
    return render(request, 'book.html', context)


@login_required
def notemarks(request):
    tags = Tag.objects.all()

    search_term = request.GET.get('search', '')  # Get the search term from the query string

    # Get the sort direction for notemarks from the query string, default is 'asc'
    notemarks_sort_direction = request.GET.get('notemarks_sort', 'asc')

    if search_term:
        # Filter notemarks based on the search term (title or contents)
        notemarks = Notemark.objects.filter(
            Q(title__icontains=search_term) | Q(contents__icontains=search_term)
        )
    else:
        # If no search term, return all notemarks
        notemarks = Notemark.objects.all()

    # Sort the notemarks based on the sort direction
    if notemarks_sort_direction == 'desc':
        notemarks = notemarks.order_by('-title')  # Change this field if you want to sort by a different field
    else:
        notemarks = notemarks.order_by('title')  # Change this field if you want to sort by a different field

    return render(request, 'notemarks.html', {
        'notemarks': notemarks, 
        'tags': tags,
        'notemarks_sort_direction': notemarks_sort_direction  # Pass the sort direction to the template if needed
    })


@login_required
def add_tag(request):
    if request.method == 'POST':
        tag_name = request.POST.get('tag_name')
        tag_color = request.POST.get('tag_color')

        # Create and save the new category
        tag = Tag.objects.create(name=tag_name, color=tag_color)

        # Success message
        messages.success(request, f'Tag "{tag.name}" created successfully!')

        return redirect('notemarks')  # Adjust to redirect to the appropriate page (e.g., books list)

    return redirect('notemarks')  # Handle case for non-POST requests


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


@login_required
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})


def custom_logout(request):
    logout(request)
    return redirect('login')  # Redirect to homepage after logout

@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        description = request.POST.get('description')
        cover_image = request.FILES.get('cover_image')  # Handle file upload

        # Update the book instance
        book.title = title
        book.authors = authors
        book.description = description
        
        if cover_image:
            fs = FileSystemStorage()
            cover_image_path = fs.save(f'cover_images/{cover_image.name}', cover_image)
            book.cover_image = cover_image_path
        
        book.save()
        
        messages.success(request, 'Book details updated successfully!')
        return redirect('book', id=book_id)

    return render(request, 'edit_book.html', {'book': book})
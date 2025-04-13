from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import BookForm, RegisterForm
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

        category = Category.objects.create(name=category_name, color=category_color)

        messages.success(request, f'Category "{category.name}" created successfully!')

        return redirect('books') 

    return redirect('books') 

@login_required 
def add_notemark(request):
    if request.method == 'POST':
        print(request.POST)  
        form = NotemarkForm(request.POST)

        if form.is_valid():
            book_id = request.POST.get('book_id')
            try:
                book = Book.objects.get(id=book_id)
            except Book.DoesNotExist:
                print(f"Book with ID {book_id} does not exist.")  
                return render(request, 'book.html', {'form': form, 'tags': Tag.objects.all(), 'error': f"Book with ID {book_id} not found"})

            notemark = form.save(commit=False)
            notemark.book = book 
            notemark.save()

            tags = request.POST.getlist('tags')
            notemark.tags.set(tags) 

            print("Notemark successfully created!") 

            return redirect('book', id=book.id)
        else:
            print("Form is not valid:", form.errors) 

    else:
        form = NotemarkForm()

    return render(request, 'book.html', {'form': form, 'tags': Tag.objects.all()})

@login_required
def delete_notemark(request, notemark_id):
    notemark = get_object_or_404(Notemark, id=notemark_id)
    
    if notemark.book.user != request.user:
        messages.error(request, "You don't have permission to delete this notemark.")
        return redirect('book', id=notemark.book.id)

    notemark.delete()

    messages.success(request, "Notemark deleted successfully!")
    return redirect('book', id=notemark.book.id)


@login_required 
def add_book(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        author_email = request.POST.get('author_email') 
        description = request.POST.get('description')
        
        cover_image = request.FILES.get('cover_image') 
        cover_image_path = None
        book_pdf = request.FILES.get('book_pdf')  
        book_pdf_path = None
        

        if cover_image:
            fs = FileSystemStorage()
            cover_image_path = fs.save(f'cover_images/{cover_image.name}', cover_image)
        
        if book_pdf:
            fs = FileSystemStorage()
            book_pdf_path = fs.save(f'books_pdfs/{book_pdf.name}', book_pdf)

   
        category_ids = request.POST.getlist('categories')  
        categories = Category.objects.filter(id__in=category_ids) 

        print(f"Title: {title}, Authors: {authors}, Email: {author_email}, Description: {description}, Cover Image: {cover_image_path}, PDF: {book_pdf_path}")
        print(f"Selected Categories: {categories}")

        try:
            book = Book.objects.create(
                title=title,
                authors=authors,
                description=description,
                cover_image=cover_image_path, 
                book_pdf=book_pdf_path, 
                user=request.user,  
                author_email=author_email 
            )

           
            book.categories.set(categories)  

            print(f"Book Created: {book.title} by {book.authors}") 

            messages.success(request, f'Book "{book.title}" has been added successfully!')

            return redirect('books')  
        except Exception as e:
            print(f"Error occurred: {str(e)}")  

    categories = Category.objects.all()
    return render(request, 'books.html', {'categories': categories})


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if book.user != request.user:
        messages.error(request, "You don't have permission to delete this book.")
        return redirect('books')

    book.delete()

    messages.success(request, "Book deleted successfully!")
    return redirect('books')

def home(request):
    return render(request, 'home.html')


@login_required
def books(request):
    categories = Category.objects.all() 
    search_term = request.GET.get('search', '')  
    sort_direction = request.GET.get('sort', 'asc')
    category_filter = request.GET.get('category', None) 

    try:
        category_filter = int(category_filter) if category_filter else None
    except ValueError:
        category_filter = None 

    books = Book.objects.filter(user=request.user)  

    if search_term:
        books = books.filter(
            Q(title__icontains=search_term) | Q(authors__icontains=search_term)
        )

    if category_filter:
        books = books.filter(categories__id=category_filter)

    if sort_direction == 'desc':
        books = books.order_by('-title')  
    else:
        books = books.order_by('title')  

    context = {
        'books': books,
        'categories': categories,
        'MEDIA_URL_BASE': settings.MEDIA_URL_BASE,
        'sort_direction': sort_direction, 
        'category_filter': category_filter,
    }

    return render(request, 'books.html', context)



@login_required
def book(request, id):
    book = get_object_or_404(Book, id=id)
    tags = Tag.objects.all()
    search_term = request.GET.get('search', '')

    notemarks_sort_direction = request.GET.get('notemarks_sort', 'asc')

    if search_term:
        notemarks = Notemark.objects.filter(
            book=book
        ).filter(
            Q(title__icontains=search_term) | Q(contents__icontains=search_term)
        )
    else:
        notemarks = Notemark.objects.filter(book=book)

    if notemarks_sort_direction == 'desc':
        notemarks = notemarks.order_by('-title')  
    else:
        notemarks = notemarks.order_by('title') 

    context = {
        'book': book,
        'notemarks': notemarks, 
        'MEDIA_URL_BASE': settings.MEDIA_URL_BASE,
        'tags': tags,
        'notemarks_sort_direction': notemarks_sort_direction  
    }

    return render(request, 'book.html', context)


@login_required
def notemarks(request):
    tags = Tag.objects.all()

    search_term = request.GET.get('search', '') 
    tag_filter = request.GET.get('tag', None)  

    try:
        tag_filter = int(tag_filter) if tag_filter else None
    except ValueError:
        tag_filter = None  

    notemarks = Notemark.objects.all()

    if search_term:
        notemarks = notemarks.filter(
            Q(title__icontains=search_term) | Q(contents__icontains=search_term)
        )

    if tag_filter:
        notemarks = notemarks.filter(tags__id=tag_filter)

    notemarks_sort_direction = request.GET.get('notemarks_sort', 'asc')

    if notemarks_sort_direction == 'desc':
        notemarks = notemarks.order_by('-title')  
    else:
        notemarks = notemarks.order_by('title') 

    return render(request, 'notemarks.html', {
        'notemarks': notemarks, 
        'tags': tags,
        'notemarks_sort_direction': notemarks_sort_direction, 
        'tag_filter': tag_filter,  
    })


@login_required
def add_tag(request):
    if request.method == 'POST':
        tag_name = request.POST.get('tag_name')
        tag_color = request.POST.get('tag_color')

        tag = Tag.objects.create(name=tag_name, color=tag_color)

        messages.success(request, f'Tag "{tag.name}" created successfully!')

        return redirect('notemarks')  

    return redirect('notemarks') 


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('books') 
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login') 
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})


def custom_logout(request):
    logout(request)
    return redirect('login') 


@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        description = request.POST.get('description')
        cover_image = request.FILES.get('cover_image')  

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
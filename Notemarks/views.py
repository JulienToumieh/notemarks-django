from django.conf import settings
from django.http import JsonResponse
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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User  
import jwt
from datetime import datetime, timedelta 


def authenticateUser(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        user_id = payload.get('user_id')
        
        user = User.objects.get(id=user_id)

        print(token)
        print(user)
        
        return user.id  
    
    except jwt.ExpiredSignatureError:
        return JsonResponse({'error': 'Token has expired'}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({'error': 'Invalid token'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)


@csrf_exempt
def apiProfile(request):
    token = request.POST.get('token') 
    
    userId = authenticateUser(token)

    try:
        user = User.objects.get(id=userId) 
    except User.DoesNotExist:
        return JsonResponse({
            'error': 'Invalid user token'}, status=400)


    return JsonResponse({'message': 'User fetched', 
                         'username': user.username,
                         'email': user.email,
                         'date_joined': user.date_joined
                         }, status=200)



@csrf_exempt
def apiEditBook(request):
    book_id = request.POST.get('book_id')
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        authors = request.POST.get('authors')
        description = request.POST.get('description')

        book.title = title
        book.authors = authors
        book.description = description
        
        book.save()
        
        messages.success(request, 'Book details updated successfully!')
        return JsonResponse({'message': 'Book edited successfully!'}, status=200)

    return JsonResponse({'message': 'Book edited successfully!'}, status=200)


@csrf_exempt
def apiDeleteBook(request):

    book_id = request.POST.get('book_id')

    book = get_object_or_404(Book, id=book_id)

    book.delete()

    messages.success(request, "Book deleted successfully!")
    return JsonResponse({'message': 'Book deleted successfully!'}, status=200)


@csrf_exempt
def apiDeleteNotemark(request):

    notemark_id = request.POST.get('notemark_id')

    notemark = get_object_or_404(Notemark, id=notemark_id)
    
    notemark.delete()

    messages.success(request, "Notemark deleted successfully!")
    return JsonResponse({'message': 'Notemark deleted successfully!'}, status=200)


@csrf_exempt
def apiCreateNotemark(request):
    if request.method == 'POST':

        token = request.POST.get('token')
        book_id = request.POST.get('book_id')
        form_chapter = request.POST.get('chapter', '')
        form_color = request.POST.get('color', '')
        form_contents = request.POST.get('contents', '')
        form_favourite = request.POST.get('favourite', 'false') 
        form_page = request.POST.get('page', '')
        form_title = request.POST.get('title', '')

        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            print(f"Book with ID {book_id} does not exist.")
            return JsonResponse({'error': 'Book does not exist'}, status=500)


        notemark = Notemark.objects.create(
            title=form_title,
            chapter=form_chapter,
            color=form_color,
            contents=form_contents,
            favourite=(form_favourite == 'true'), 
            page=form_page,
            book=book
        )

        tags = request.POST.getlist('tags')
        print(f"Tags received: {tags}")
    
        if tags:
            tag_ids = [int(tag_id) for tag_id in tags[0].split(',')]

            print(f"Converted tag IDs: {tag_ids}")

            notemark.tags.set(tag_ids)

        notemark.save()


        print(f"Notemark successfully created: {notemark}")

        return JsonResponse({'message': 'Notemark created successfully!'}, status=200)
    else:
        return JsonResponse({'error': 'Something went wrong, please try again!'}, status=500)




@csrf_exempt
def apiCreateBook(request):
    if request.method == 'POST':

        token = request.POST.get('token') 

        userId = authenticateUser(token)
        
        try:
            user = User.objects.get(id=userId)  
        except User.DoesNotExist:
            return JsonResponse({'error': 'Invalid user token'}, status=400)

        title = request.POST.get('title')
        authors = request.POST.get('authors')
        author_email = request.POST.get('author_email')
        description = request.POST.get('description')
        
        cover_image = request.FILES.get('cover_image')
        book_pdf = request.FILES.get('book_pdf')

        cover_image_path = None
        book_pdf_path = None

        if cover_image:
            fs = FileSystemStorage()
            cover_image_path = fs.save(f'cover_images/{cover_image.name}', cover_image)
        
        if book_pdf:
            fs = FileSystemStorage()
            book_pdf_path = fs.save(f'books_pdfs/{book_pdf.name}', book_pdf)

        category_ids = request.POST.getlist('categories')
        categories = Category.objects.filter(id__in=category_ids)

        try:
            book = Book.objects.create(
                title=title,
                authors=authors,
                description=description,
                cover_image=cover_image_path, 
                book_pdf=book_pdf_path, 
                user=user, 
                author_email=author_email
            )

            book.categories.set(categories)
        
            messages.success(request, f'Book "{book.title}" has been added successfully!')
            return JsonResponse({'message': 'Book created successfully!'}, status=200)

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return JsonResponse({'error': 'Something went wrong, please try again!'}, status=500)


@csrf_exempt
def apiCreateTag(request):
    tag_name = request.POST.get('tag_name', None)
    tag_color = request.POST.get('tag_color', None)

    try:
        tag = Tag.objects.create(name=tag_name, color=tag_color)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Tag "{tag.name}" created successfully!',
            'tag_id': tag.id
        }, status=201)

    except Exception as e:
        return JsonResponse({
            'status': 'failure',
            'message': f'An error occurred: {str(e)}'
        }, status=500)  

@csrf_exempt
def apiCreateCategory(request):
    category_name = request.POST.get('category_name', None)
    category_color = request.POST.get('category_color', None)

    try:
        category = Category.objects.create(name=category_name, color=category_color)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Category "{category.name}" created successfully!',
            'category_id': category.id
        }, status=201) 

    except Exception as e:
        return JsonResponse({
            'status': 'failure',
            'message': f'An error occurred: {str(e)}'
        }, status=500) 



@csrf_exempt
def apibook(request):

    bookid = request.POST.get('bookid', None)  

    book = get_object_or_404(Book, id=bookid)
    tags = Tag.objects.all()
    search_term = request.POST.get('search', '')

    notemarks_sort_direction = request.POST.get('sort', 'asc')

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

    notemarks_data = [{
        'id': notemark.id,
        'title': notemark.title,
        'chapter': notemark.chapter,
        'page': notemark.page,
        'contents': notemark.contents,
        'color': notemark.color,
        'tags': [tag.name for tag in notemark.tags.all()],
    } for notemark in notemarks]

    tags_data = [{
        'id': tag.id,
        'name': tag.name,
        'color': tag.color
    } for tag in tags]

    book_data = {
        'id': book.id,
        'title': book.title,
        'authors': book.authors,
        'description': book.description,
        'cover_image': book.cover_image if book.cover_image else None,
        'book_pdf': book.book_pdf if book.book_pdf else None,
        'categories': [category.name for category in book.categories.all()],
    }

    return JsonResponse({
        'book': book_data,
        'notemarks': notemarks_data, 
        'tags': tags_data,
        'notemarks_sort_direction': notemarks_sort_direction 
    })


@csrf_exempt
def apinotemarks(request):
    token = request.POST.get('token')
    userId = authenticateUser(token)

    tags = Tag.objects.all()
    notemarks_sort_direction = request.POST.get('notemarks_sort', 'asc')
    search_term = request.POST.get('search', '') 
    tag_filter = request.POST.get('tag', None)  


    try:
        tag_filter = int(tag_filter) if tag_filter else None
    except ValueError:
        tag_filter = None  

    books = Book.objects.filter(user=userId) 

    notemarks = Notemark.objects.filter(book__in=books)

    if search_term:
        notemarks = notemarks.filter(
            Q(title__icontains=search_term) | Q(contents__icontains=search_term)
        )

    if tag_filter:
        notemarks = notemarks.filter(tags__id=tag_filter)


    if notemarks_sort_direction == 'desc':
        notemarks = notemarks.order_by('-title')  
    else:
        notemarks = notemarks.order_by('title') 


    notemarks_data = [{
        'id': notemark.id,
        'title': notemark.title,
        'chapter': notemark.chapter,
        'page': notemark.page,
        'contents': notemark.contents,
        'color': notemark.color,
        'tags': [tag.name for tag in notemark.tags.all()],
    } for notemark in notemarks]

    tags_data = [{
        'id': tag.id,
        'name': tag.name,
        'color': tag.color
    } for tag in tags]


    return JsonResponse({
        'notemarks': notemarks_data, 
        'tags': tags_data,
        'sort_direction': notemarks_sort_direction, 
        'category_filter': tag_filter,
    })


@csrf_exempt
def apilogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)


        if user is not None:
            login(request, user) 

            request.session['user_id'] = user.id 

            payload = {
                'user_id': user.id, 
                'username': user.username,
                'exp': datetime.utcnow() + timedelta(days=1), 
                'iat': datetime.utcnow()  
            }

            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            return JsonResponse({'message': 'Login successful', 'token': token}, status=200)
        
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def apibooks(request):

    token = request.POST.get('token')

    userId = authenticateUser(token)


    categories = Category.objects.all() 
    search_term = request.POST.get('search', '')  
    sort_direction = request.POST.get('sort', 'asc')
    category_filter = request.POST.get('category', None) 

    try:
        category_filter = int(category_filter) if category_filter else None
    except ValueError:
        category_filter = None 

    books = Book.objects.filter(user=userId)  

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

    books_data = [{
        'id': book.id,
        'title': book.title,
        'authors': book.authors,
        'description': book.description,
        'cover_image': book.cover_image if book.cover_image else None,
        'book_pdf': book.book_pdf if book.book_pdf else None,
        'categories': [category.name for category in book.categories.all()],
    } for book in books]

    categories_data = [{
        'id': category.id,
        'name': category.name,
        'color': category.color
    } for category in categories]


    return JsonResponse({
        'books': books_data,
        'categories': categories_data,
        'sort_direction': sort_direction, 
        'category_filter': category_filter,
    })









################################### DJANGO VERSION ########################################









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

    books = Book.objects.filter(user=request.user) 

    notemarks = Notemark.objects.filter(book__in=books)


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
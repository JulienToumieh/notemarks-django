"""
URL configuration for Notemarks project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Notemarks import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.books, name='books'),
    path('books/', views.books, name='books'),
    path('notemarks/', views.notemarks, name='notemarks'),
    path('book/<int:id>/', views.book, name='book'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('add_book/', views.add_book, name='add_book'),
    path('add_notemark/', views.add_notemark, name='add_notemark'),
    path('delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('delete_notemark/<int:notemark_id>/', views.delete_notemark, name='delete_notemark'),
    path('add_category/', views.add_category, name='add_category'),
    path('add_tag/', views.add_tag, name='add_tag'),
    path('book/<int:book_id>/edit/', views.edit_book, name='edit_book'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
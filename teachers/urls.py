"""Directory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from teachers import views

app_name = "teachers"

urlpatterns = [

    path('', views.base, name='base'),
    path('search/', views.SearchView.as_view(), name='search_teacher'),
    path('FileUploadView/', views.FileUploadView.as_view(), name='fileupload'),
    path('viewall/', views.ViewAll.as_view(), name='viewall'),
    path('getprofile/<int:pk>/', views.GetProfile.as_view(), name='getprofile'),
    path('addprofileview/', views.CreateProfile.as_view(), name='addprofileview'),
    path('login/', LoginView.as_view(redirect_authenticated_user=True, template_name='login.html'),name='loginview'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

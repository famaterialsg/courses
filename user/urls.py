from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 

app_name = 'user'

urlpatterns = [
    path('users/', views.user_list, name='user_list'),

    # Login URL
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    
    # Logout URL with redirection to login
    path('logout/', auth_views.LogoutView.as_view(next_page='user:login'), name='logout'),
    
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('add/', views.user_add, name='user_add'),
    path('edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('detail/<int:pk>/', views.user_detail, name='user_detail'),
    path('import/', views.import_users, name='import_users'),
    path('export/', views.export_users, name='export_users'),
    
]

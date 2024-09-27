from django.urls import path
from . import views
from django.contrib.auth import views as auth_views 
app_name = 'user'

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/create/', views.user_add, name='user_add'),
    path('users/edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('import/', views.import_users, name='import_users'),
    path('export/', views.export_users, name='export_users'),
    path('user/<int:user_id>/assign-programs/', views.assign_training_programs, name='assign_training_programs'),
]

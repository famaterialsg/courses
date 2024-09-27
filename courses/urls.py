from django.urls import path
from . import views
app_name = 'courses'
urlpatterns = [
    path('', views.course_list, name='list_courses'),
    path('new-home/', views.new_home, name='new_home'),
]

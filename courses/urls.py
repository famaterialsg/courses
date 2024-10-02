from django.urls import path
from . import views
app_name = 'courses'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('coursedb/', views.courses_list_database, name='courses_list_database'),
    
    path('import/', views.import_courses, name='import_courses'),
    path('delete-courses/', views.delete_courses, name='delete_courses'),
    path('get_sub_module_data/<str:sub_module_name>/', views.get_sub_module_data, name='get_sub_module_data'),
    
    path('admin', views.course_admin, name='course_admin'),
    path('detail/<str:course_name>/', views.course_detail, name='course_detail'),
    # path('admin/import/', views.import_courses, name='import_courses'),
    # path('admin/delete-courses/', views.delete_courses, name='delete_courses'),
    # path('admin/get_sub_module_data/<str:sub_module_name>/', views.get_sub_module_data, name='get_sub_module_data'),

    path('import-course/<str:course_name>/', views.import_courses, name='import_courses'),
    path('delete-course/<str:course_name>/', views.delete_courses, name='delete_course'),

    
   
]


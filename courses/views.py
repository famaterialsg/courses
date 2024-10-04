import os
import re
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from .models import Course
from django.contrib import messages
from django.http import JsonResponse
from user.models import Profile  # Adjust import based on your structure
from django.contrib.auth.models import User 
from .forms import ExcelImportCourseForm,CourseForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')  # Redirect to login page if not logged in
def home(request):
    # Check if the user is authenticated
    is_student = False
    if request.user.is_authenticated:
        # Get the user's profile and check the role
        profile = Profile.objects.filter(user=request.user).first()
        is_student = profile.role.role_name == 'Student' if profile and profile.role else False

    return render(request, 'home.html', {'is_student': is_student})


# For admin
def clean_content(content):
    if isinstance(content, str):
        return re.sub(r'[^\x00-\x7F]+', '', content)  # Loại bỏ ký tự không phải ASCII
    return content

def course_admin(request):
    courses = Course.objects.all().order_by('course', 'sub_course', 'module', 'sub_module')
    if not courses:
        message = "No course available."  # Set message if no course is found
        return render(request, 'course_admin.html', {'message': message})
    return render(request, 'course_admin.html', {'courses': courses})


def course_list_admin(request):
    form = ExcelImportCourseForm()
    
    # Lấy tất cả các sub_courses từ database
    sub_courses = Course.objects.values('sub_course', 'module', 'sub_module', 'content', 'img_list', 'video_url')
    
    # Tổ chức dữ liệu theo sub_course và module
    sub_courses_data = {}
    for row in sub_courses:
        sub_course = row['sub_course']
        module = row['module']
        sub_module_data = {
            'sub_module': row['sub_module'],
            'content': row['content'],  # Updated field
            'img_list': row['img_list'],
            'video_url': row['video_url']
        }
    
        if sub_course not in sub_courses_data:
            sub_courses_data[sub_course] = {}
        
        if module not in sub_courses_data[sub_course]:
            sub_courses_data[sub_course][module] = []
        
        sub_courses_data[sub_course][module].append(sub_module_data)

    context = {
        'sub_courses': [{'sub_course': sub_course, 'modules': modules} for sub_course, modules in sub_courses_data.items()],
        'form': form
    }

    return render(request, 'course_list.html', context)


def course_detail(request, course_name):
    # Replace - with / to get the original course name
    course_name_decoded = course_name.replace('-', '/')
    course = Course.objects.filter(course=course_name_decoded).first()  # Get the specific course

    if not course:
        return render(request, '404.html', {'message': 'No course available.'})  # Show a message if no course is found

    sub_modules = Course.objects.filter(course=course_name_decoded).distinct('sub_module')  # Fetch unique sub-modules

    return render(request, 'course_detail.html', {
        'course': course,
        'sub_modules': sub_modules,
    })



def get_sub_module_data(request, sub_module_name):
    course = Course.objects.filter(sub_module=sub_module_name).first()

    if not course:
        return JsonResponse({"error": "Sub-module not found"}, status=404)

    return JsonResponse({
        "content": course.content,
        "img_list": course.img_list,
        "video_url": course.video_url,
    })



def import_courses(request):
    if request.method == 'POST':
        form = ExcelImportCourseForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['csv_file']
            try:
                df = pd.read_csv(uploaded_file)  
                print(df)
                print(df.columns) 

                courses_imported = 0 

                df['content_html_list'] = df['content_html_list'].apply(clean_content)

                for index, row in df.iterrows():
                    if row.isnull().all():
                        continue 
                    course_name = row.get("course")
                    sub_course_name = row.get("sub_course")
                    module_name = row.get("module")
                    sub_module_name = row.get("sub_module")
                    content_html_list = row.get("content_html_list")  # No error expected here
                    img_list = row.get("img_list")
                    video_url = row.get("video_url")

                    print(f"Importing row: {row}")  # Log the row being processed

                    try:
                        Course.objects.create(
                            course=course_name,
                            sub_course=sub_course_name,
                            module=module_name,
                            sub_module=sub_module_name,
                            content=content_html_list,  # Update this to match your model
                            img_list=img_list,
                            video_url=video_url
                        )
                        courses_imported += 1
                        print(f"Imported row {index} successfully.")  # Log successful import
                    except Exception as e:
                        print(f"Error importing row {index}: {e}")  # Log import errors

                messages.success(request, f"{courses_imported} courses imported successfully!")
                # Query all users to display after import
                users = User.objects.all()  # Fetch all users from the database
            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")

            return redirect('courses:course_admin')  # Redirect to your course list page
    else:
        form = ExcelImportCourseForm()

    return render(request, 'course_list.html', {'form': form})


def delete_courses(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        
        if course_name:
            deleted_count, _ = Course.objects.filter(course=course_name).delete()
            if deleted_count > 0:
                messages.success(request, f"{deleted_count} course(s) deleted successfully!")
            else:
                messages.warning(request, "No courses found with that name.")
        else:
            messages.error(request, "Please provide a course name.")
        
    return redirect('courses:course_admin')  # Replace with your course list view


# @login_required(login_url='/login/')
def course_list(request):
    # Directory containing all CSV files
    csv_dir = os.path.join(settings.BASE_DIR, 'media/data_csv')
    
    # List all .csv files in the directory
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
    # Debugging: print the found files in the console
    print("CSV Files in Directory:", csv_files)

    # If a file is selected, load its content
    selected_file = request.GET.get('selected_file')
    sub_courses_data = {}
    course_name = None
    split_sub_courses = []
    error = None

    if selected_file:
        # Full file path
        file_path = os.path.join(csv_dir, selected_file)
        
        # Load the selected CSV file into a pandas DataFrame
        try:
            data = pd.read_csv(file_path)  # Updated to read CSV files
            print("Data Loaded Successfully:", data.head())  # Debugging
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            error = 'Failed to load CSV file.'

        if error is None:
            # Ensure the required columns are present
            if 'course' not in data.columns or 'sub_course' not in data.columns:
                error = 'Required columns are missing in the CSV.'
            else:
                # Get the course name from the first row
                course_name = data['course'].iloc[0]

                # Get unique sub_courses, dropping NaN values
                sub_course_list = data['sub_course'].dropna().unique()

                # Check if the sub_course_list is empty
                if len(sub_course_list) == 0:
                    print(f"No sub_courses found for course: {course_name}")
                    sub_course_list = ["No Sub Courses Available"]
                else:
                    print(f"Sub courses found for {course_name}: {sub_course_list}")

                # Process the CSV content
                for index, row in data.iterrows():
                    sub_course = row['sub_course'] if pd.notna(row['sub_course']) and row['sub_course'].strip() else course_name  # Use course name if sub_course is empty
                    module_name = row['module']
                    sub_module_name = row['sub_module']

                    # Skip rows with missing essential data
                    if pd.isna(module_name) or pd.isna(sub_module_name):
                        print(f"Skipping row {index} due to missing module or sub_module.")
                        continue

                    if sub_course not in sub_courses_data:
                        sub_courses_data[sub_course] = {}

                    if module_name not in sub_courses_data[sub_course]:
                        sub_courses_data[sub_course][module_name] = []

                    # Extract additional fields, defaulting to empty if NaN
                    content_html_list = row['content_html_list'] if pd.notna(row['content_html_list']) else ''
                    img_list = row['img_list'] if pd.notna(row['img_list']) else ''
                    video_url = row['video_url'] if pd.notna(row['video_url']) else ''

                    # Clean content_html_list
                    content_html_list = content_html_list.replace('\\n', '<br>').replace("\\'", "'")

                    sub_courses_data[sub_course][module_name].append({
                        'sub_module': sub_module_name,
                        'content_html_list': content_html_list,
                        'img_list': img_list,
                        'video_url': video_url
                    })

                # Prepare structured output for the template
                for sub_course in sub_course_list:
                    if ':' in sub_course:
                        title, description = sub_course.split(':', 1)
                        split_sub_courses.append({
                            'title': title.strip(),
                            'description': description.strip(),
                            'modules': sub_courses_data.get(sub_course, {})
                        })
                    else:
                        # Handle cases where there is no description
                        split_sub_courses.append({
                            'title': sub_course.strip(),
                            'description': '',  # No description provided
                            'modules': sub_courses_data.get(sub_course, {})
                        })


    context = {
        'csv_files': csv_files,  # Ensure this key matches in your template
        'selected_file': selected_file,
        'course_name': course_name,
        'split_sub_courses': split_sub_courses,
        'error': error,  # Pass the error message if any
    }

    return render(request, 'courses.html', context)



# GET DATA FROM DATABASE (TEST)

def get_courses(request):
    # Get all unique course names
    courses = Course.objects.values_list('course_name', flat=True).distinct()
    return render(request, 'courses_list_database.html', {'courses': courses})


def courses_list_database(request):
    # Get all unique courses from the 'course' field
    courses = Course.objects.values_list('course', flat=True).distinct()

    # Default to None if no course is selected
    selected_course = None
    sub_courses_data = {}

    # Check if the form is submitted
    if request.method == 'POST':
        selected_course = request.POST.get('selected_course')

        # Filter sub_courses by the selected course and sort by sub_course and module
        sub_courses = Course.objects.filter(course=selected_course).order_by('sub_course', 'module').values(
            'sub_course', 'module', 'sub_module', 'content', 'img_list', 'video_url'
        )

        # Organize data by sub_course and module
        for row in sub_courses:
            sub_course = row['sub_course']
            module = row['module']
            sub_module_data = {
                'sub_module': row['sub_module'],
                'content': row['content'],
                'img_list': row['img_list'],
                'video_url': row['video_url']
            }

            if sub_course not in sub_courses_data:
                sub_courses_data[sub_course] = {}

            if module not in sub_courses_data[sub_course]:
                sub_courses_data[sub_course][module] = []

            sub_courses_data[sub_course][module].append(sub_module_data)

    context = {
        'courses': courses,
        'selected_course': selected_course,  # Pass the selected course to the template
        'sub_courses': [{'sub_course': sub_course, 'modules': modules} for sub_course, modules in sub_courses_data.items()]
    }

    return render(request, 'courses_list_database.html', context)



def edit_course(request, course_name):
    # Get all courses that match the given course_name
    courses = Course.objects.filter(course=course_name)

    # Create a context dictionary to pass to the template
    context = {
        'course_name': course_name,
        'courses': courses,
    }

    # Render the 'edit_course.html' template with the context data
    return render(request, 'edit_course.html', context)


def edit_module(request, sub_module_name):
    # Get the course object that matches the given sub_module_name, or return a 404 if not found
    course = get_object_or_404(Course, sub_module=sub_module_name)

    if request.method == 'POST':
        # If the request is a POST, create a form instance with the submitted data and the current course instance
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            # If the form is valid, save the updated course information
            form.save()

            # Get the previous URL from the request's headers, or default to '/' (home page) if not found
            previous_url = request.META.get('HTTP_REFERER', '/')
            # Redirect the user to the previous page
            return HttpResponseRedirect(previous_url)
    else:
        # If the request is not a POST, create a form instance pre-filled with the current course data
        form = CourseForm(instance=course)

    # Render the 'edit_module.html' template, passing the form and course name
    return render(request, 'edit_module.html', {'form': form, 'course_name': course.course})




    

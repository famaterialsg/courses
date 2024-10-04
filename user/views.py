from django.shortcuts import render, get_object_or_404, redirect
from role.models import Role
from user.models import Profile
from django.contrib.auth.models import User
import pandas as pd
from django.http import HttpResponse
from django.contrib import messages
from user.forms import UserForm, RoleForm, ExcelImportForm
import openpyxl

from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required

@login_required(login_url='login')  # Redirect to login page if not logged in



# List all users
def user_list(request):
    users = User.objects.all()
    form = ExcelImportForm()

    return render(request, 'user_list.html', {'users': users, 'form': form})


# View user detail
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'user_detail.html', {'user': user})


def user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user:user_list')
        else:
            print('Invalid form')
            print(form.errors)  # Print the errors to the console
    else:
        form = UserForm()
    return render(request, 'user_form.html', {'form': form})


# Edit user details
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user:user_list')
        else:
            print('Form is invalid:', form.errors)  # Optional: For debugging purposes
    else:
        form = UserForm(instance=user)

    return render(request, 'user_form.html', {'form': form})



# Export users to Excel
def export_users(request):

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=users.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Users'
    
    columns = ['username', 'password', 'email', 'first_name', 'last_name', 'role']
    worksheet.append(columns)
    
    for user in User.objects.all():
        profile = Profile.objects.filter(user=user).first()  # Get the profile for the user
        role_name = profile.role.name if profile and profile.role else ''
        worksheet.append([user.username, '', user.email, user.first_name, user.last_name, role_name])
    
    workbook.save(response)
    return response



from django.contrib.auth.models import User

def import_users(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                # Load the Excel file into a DataFrame
                df = pd.read_excel(excel_file)

                # Iterate through the rows of the DataFrame
                for index, row in df.iterrows():
                    username = row['username']
                    password = row['password']
                    email = row['email']
                    first_name = row['first_name']
                    last_name = row['last_name']
                    role_name = row['role']

                    # Check if the role exists, if not, create it
                    role, created = Role.objects.get_or_create(role_name=role_name)

                    # Check if the user exists
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                        }
                    )

                    # Update the user's details if they exist or set the password for new users
                    if not created:
                        user.email = email
                        user.first_name = first_name
                        user.last_name = last_name
                    user.set_password(password)  # Set password
                    user.save()

                    # Assign role to user
                    user.profile.role = role  # Assuming you have a profile with a role field
                    user.profile.save()

                messages.success(request, "Users imported successfully!")
                
                # Query all users and their profiles/roles to display after import
                users = User.objects.select_related('profile__role')  # Fetch users and their roles

            except Exception as e:
                messages.error(request, f"Error occurred: {str(e)}")
                users = User.objects.none()  # Return empty queryset if error

            return render(request, 'user_list.html', {'form': form, 'users': users})

    else:
        form = ExcelImportForm()
        users = User.objects.select_related('profile__role')  # Show users when loading the form
    return render(request, 'user_list.html', {'form': form, 'users': users})









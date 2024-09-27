from django.shortcuts import render, get_object_or_404, redirect
from .models import User, Role
import pandas as pd
import bcrypt
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserForm, RoleForm, ExcelImportForm
import openpyxl
# from module_group.models import ModuleGroup
from .forms import AssignTrainingProgramForm

def assign_training_programs(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = AssignTrainingProgramForm(request.POST, instance=user)
        if form.is_valid():
            form.save()  # This will save the M2M relationship
            messages.success(request, f"Training programs have been successfully assigned to {user.username}.")
            return redirect('user:user_list')  # Redirect to your desired page after success
    else:
        form = AssignTrainingProgramForm(instance=user, initial={'training_programs': user.training_programs.all()})

    return render(request, 'assign_training_programs.html', {'user': user, 'form': form})


def user_list(request):
    users = User.objects.all()
    
    form = ExcelImportForm()

    return render(request, 'user_list.html', {'users': users,  'form': form})


def get_role_quick_and_dirty_way(role_id):
    roles = {
        1: "student",
        2: "teacher",
        3: "admin",
        4: "super admin"
    }
    return roles.get(role_id, "Unknown role")

def insert_user(username, hashed_password, email, full_name, role_id):
    try:
        User.objects.create(
            username=username,
            password=hashed_password.decode('utf-8'),
            email=email,
            full_name=full_name,
            role_id=role_id
        )
        return True, None
    except Exception as e:
        return False, str(e)


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
        form = UserForm()
    return render(request, 'user_form.html', {'form': form,})

def user_edit(request, pk):
    
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user:user_list')
    else:
        form = UserForm(instance=user)
    return render(request, 'user_form.html', {'form': form})

# Export Users to Excel
def export_users(request):
    # Create a workbook and add a worksheet
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lms_users.xlsx'
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Users'
    
    # Define the columns
    columns = ['username', 'password', 'email', 'full_name', 'role_id', 'role_name']
    worksheet.append(columns)
    
    # Fetch all users and write to the Excel file
    for user in User.objects.all():
        worksheet.append([user.username, '******', user.email, user.full_name, user.role.id, str(user.role)])
    
    workbook.save(response)
    return response

def import_users(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['excel_file']
            try:
                # Read the Excel file
                df = pd.read_excel(uploaded_file)
                users_imported = 0  # Counter for users successfully imported

                # Loop over the rows in the DataFrame
                for index, row in df.iterrows():
                    username = row.get("username")
                    password = str(row.get("password"))
                    email = row.get("email")
                    full_name = row.get("full_name")
                    role_id = row.get("role_id")

                    print(f"Processing row: {username}, {email}, {role_id}")  # Debugging

                    # Handling the role lookup
                    role = Role.objects.filter(id=role_id).first()
                    if not role:
                        messages.error(request, f"Invalid role ID '{role_id}' for user '{username}'. Skipping.")
                        print(f"Invalid role ID for {username}")  # Debugging
                        continue

                    # Hash the password
                    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()

                    # Check if the user already exists
                    if not User.objects.filter(username=username).exists():
                        # Create and save the new user
                        User.objects.create(
                            username=username,
                            password=hashed_password,
                            email=email,
                            full_name=full_name,
                            role=role
                        )
                        users_imported += 1
                        print(f"User {username} created")  # Debugging
                    else:
                        messages.warning(request, f"User '{username}' already exists. Skipping.")
                        print(f"User {username} already exists")  # Debugging

                # Feedback message
                if users_imported > 0:
                    messages.success(request, f"{users_imported} users imported successfully!")
                else:
                    messages.warning(request, "No users were imported.")

            except Exception as e:
                messages.error(request, f"An error occurred during import: {e}")
                print(f"Error during import: {e}")  # Debugging

            return redirect('user:user_list')
    else:
        form = ExcelImportForm()

    return render(request, 'user_list.html', {'form': form})






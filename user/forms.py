from django import forms
from role.models import Role
from user.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        # Save the user first before adding the role
        if commit:
            user.save()
            # Assign the role to the user via Profile
            role = self.cleaned_data['role']
            Profile.objects.create(user=user, role=role)
        return user



class ExcelImportForm(forms.Form):
    excel_file = forms.FileField()


# Form for creating and editing roles
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role_name']
        



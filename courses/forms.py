from django import forms
from .models import Course
import csv
import os
from ckeditor.widgets import CKEditorWidget


class ExcelImportCourseForm(forms.Form):
    csv_file = forms.FileField()

class CourseFileSelectForm(forms.Form):
    csv_files_directory = 'media/data_csv/'
    csv_file_choices = [(f, f) for f in os.listdir(csv_files_directory) if f.endswith('.csv')]
    csv_file = forms.ChoiceField(choices=csv_file_choices, label="Select a CSV File")

class CourseForm(forms.ModelForm):

    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Course
        fields = ['course', 'sub_course', 'module', 'sub_module', 'content', 'img_list', 'video_url']
        widgets = {
            'course': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course name'}),
            'sub_course': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sub-course name'}),
            'module': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Module name'}),
            'sub_module': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sub-module name'}),
            'content': CKEditorWidget(attrs={'class': 'form-control'}),
            'img_list': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Image URLs (one per line)'}),
            'video_url': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Video URL'}),
        }

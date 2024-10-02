from django import forms
from .models import Course
import csv
import os

class ExcelImportCourseForm(forms.Form):
    csv_file = forms.FileField()

class CourseFileSelectForm(forms.Form):
    csv_files_directory = 'media/data_csv/'
    csv_file_choices = [(f, f) for f in os.listdir(csv_files_directory) if f.endswith('.csv')]
    csv_file = forms.ChoiceField(choices=csv_file_choices, label="Select a CSV File")


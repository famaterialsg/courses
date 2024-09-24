import os
import pandas as pd
from django.shortcuts import render
from django.conf import settings

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

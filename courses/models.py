# Create your models here.
from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models


# Create your models here.

class Course(models.Model):
    course = models.CharField(max_length=255)  # Thay TextField bằng CharField để giới hạn độ dài
    sub_course = models.CharField(max_length=200)
    module = models.CharField(max_length=200)
    sub_module = models.CharField(max_length=200)
    content = RichTextUploadingField(config_name="default", null=True)
    img_list = models.TextField(null=True)
    video_url = models.TextField(null=True)

    def __str__(self):
        return self.course

    class Meta:
        db_table = "course"


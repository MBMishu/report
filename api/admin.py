from django.contrib import admin

# Register your models here.
from .models import  *



admin.site.register(Video)
admin.site.register(DetectedFrame)
admin.site.register(DetectedObjectPDF)
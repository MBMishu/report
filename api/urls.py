from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
  
path('video/', views.videoUpload, name="videoUpload"),
path('', views.home, name="home"),
path('all_detected_object_pdfs/', views.all_detected_object_pdfs, name="all_detected_object_pdfs"),
path('all_detected_object_pdfs/<int:id>/', views.detected_object_pdf_by_id, name="detected_object_pdf_by_id"),
path('detected_frame_by_id/<int:id>/', views.detected_frame_by_id, name="detected_frame_by_id"),
path('all_video/', views.all_video, name="all_video"),
path('all_video/<int:id>/', views.video_by_id, name="video_by_id"),
]

from rest_framework import serializers
from .models import *

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'

class DetectedFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectedFrame
        fields = '__all__'
        
        
class DetectedObjectPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectedObjectPDF
        fields = '__all__'
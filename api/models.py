from django.db import models
from django.utils import timezone
import imageio
import os
from django.conf import settings

import cv2



# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='video/')
    file_gif = models.FileField(upload_to='video_gifs/',blank=True, null=True)
    detected_gif = models.FileField(upload_to='detected_gifs/',blank=True, null=True)
    enhanced_gif = models.FileField(upload_to='enhanced_gif/',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    
    def create_gif(self, frames, output_path):
        # Create a GIF from a list of frames using imageio
        imageio.mimsave(output_path, frames, format='GIF', duration=1000.0)
        
    def create_gif_from_video(self, video_path, output_path):
        
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames = []
        
        for frame_index in range(frame_count):
            success, image = cap.read()
            if not success:
                break
            
            if frame_index % 100 == 0:
                # capture frame from video
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                frames.append(rgb_image)
        
        cap.release()
        imageio.mimsave(output_path, frames, format='GIF', duration=1000.0)
        
    
    
    def create_detected_gif(self):
        # Get all DetectedFrame instances for this video
        detected_frames = DetectedFrame.objects.filter(video=self)

        # Create a list to store image paths
        image_paths = []

        # Iterate over each DetectedFrame and append the image path to the list
        for detected_frame in detected_frames:
            image_paths.append(detected_frame.file.path)

        # Specify the output path for the detected_gif
        detected_gif_path = os.path.join(settings.MEDIA_ROOT, 'detected_gifs', f'{self.id}_detected.gif')

        # Before calling mimsave, ensure images are read correctly
        frames = [imageio.imread(image_path) for image_path in image_paths]

        # Create the GIF using the create_gif method
        self.create_gif(frames, detected_gif_path)

        # Save the detected_gif path to the detected_gif field of the Video model
        self.detected_gif = f'detected_gifs/{self.id}_detected.gif'
        self.save()
        
        return detected_gif_path
    
    def create_enhanced_gif(self):
        # Get all DetectedFrame instances for this video
        detected_frames = DetectedFrame.objects.filter(video=self)

        # Create a list to store image paths
        image_paths = []

        # Iterate over each DetectedFrame and append the image path to the list
        for detected_frame in detected_frames:
            image_paths.append(detected_frame.file.path)

        # Specify the output path for the detected_gif
        detected_gif_path = os.path.join(settings.MEDIA_ROOT, 'enhanced_gif', f'{self.id}enhanced_gif.gif')

        # Before calling mimsave, ensure images are read correctly
        frames = [imageio.imread(image_path) for image_path in image_paths]

        # Create the GIF using the create_gif method
        self.create_gif(frames, detected_gif_path)

        # Save the detected_gif path to the detected_gif field of the Video model
        self.enhanced_gif = f'enhanced_gif/{self.id}enhanced_gif.gif'
        self.save()
        
        return detected_gif_path

    def save_video_as_gif(self):
        # Specify the path for the input video
        video_path = self.file.path

        # Specify the output path for the gif
        gif_output_path = os.path.join(settings.MEDIA_ROOT, 'video_gifs', f'{self.id}_video.gif')

        # Create the GIF using the create_gif method
        self.create_gif_from_video(video_path, gif_output_path)

        # Save the gif path to the file_gif field of the Video model
        self.file_gif = f'video_gifs/{self.id}_video.gif'
        self.save()

        return gif_output_path
    
    def __str__(self):
        return str(self.id)
    
class DetectedFrame(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    frame_number = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='detected_frames/')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    @property
    def PicURL(self):
        try:
            url = self.file.url
        except:
            url = ''

        return url
    def __str__(self):
        return str(self.id)
    
    

class DetectedObjectPDF(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, blank=True, null=True)
    pdf_file = models.FileField(upload_to='pdf/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    def __str__(self):
        return str(self.id)
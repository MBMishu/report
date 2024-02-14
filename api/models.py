from django.db import models
from django.utils import timezone
import imageio
import os
from django.conf import settings

import cv2
import numpy as np


from django.core.files import File
from moviepy.editor import VideoFileClip

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    file = models.FileField(upload_to='video/')
    enhanced_file = models.FileField(upload_to='enhanced_file/',blank=True,null=True)
    file_gif = models.FileField(upload_to='video_gifs/',blank=True, null=True)
    detected_gif = models.FileField(upload_to='detected_gifs/',blank=True, null=True)
    enhanced_gif = models.FileField(upload_to='enhanced_gif/',blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    
    def create_gif(self, frames, output_path):
        # Create a GIF from a list of frames using imageio
        imageio.mimsave(output_path, frames, format='GIF', duration=100,loop=True)
        
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
        imageio.mimsave(output_path, frames, format='GIF', duration=100,loop=True)
        
    def create_enhanced_gif_from_video(self, video_path, output_path):
        
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames = []
        
        for frame_index in range(frame_count):
            success, image = cap.read()
            if not success:
                break
            
            if frame_index % 100 == 0:
              
                # Increase blue channel to reduce green color cast
                image[:,:,0] = cv2.addWeighted(image[:,:,0], 1.2, np.zeros_like(image[:,:,0]), 0, 0)
                # Reduce green channel to compensate for the increased blue
                image[:,:,1] = cv2.addWeighted(image[:,:,1], 0.8, np.zeros_like(image[:,:,1]), 0, 0)
                
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                frames.append(rgb_image)
        
        cap.release()
        imageio.mimsave(output_path, frames, format='GIF', duration=100,loop=True)
        
    def enhance_video(self, input_path, output_path):
        
        cap = cv2.VideoCapture(input_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        fourcc = cv2.VideoWriter_fourcc(*'H264')
        out = cv2.VideoWriter(output_path, fourcc, fps, size)
        frames = []
        
        for frame_index in range(frame_count):
            success, image = cap.read()
            if not success:
                break
            
            if frame_index % 10 == 0:
              
                # Increase blue channel to reduce green color cast
                image[:,:,0] = cv2.addWeighted(image[:,:,0], 1.2, np.zeros_like(image[:,:,0]), 0, 0)
                # Reduce green channel to compensate for the increased blue
                image[:,:,1] = cv2.addWeighted(image[:,:,1], 0.8, np.zeros_like(image[:,:,1]), 0, 0)
                
                # rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                frame_enhanced = image

                out.write(frame_enhanced)
        
        cap.release()
        out.release()
        
    
    
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
        video_path = self.file.path

        # Specify the output path for the enhanced video
        enhanced_video_path = os.path.join(settings.MEDIA_ROOT, 'enhanced_file', f'{self.id}_enhanced.mp4')

        # Enhance the video and save it
        self.enhance_video(video_path, enhanced_video_path)

        # Specify the output path for the enhanced_gif
        enhanced_gif_path = os.path.join(settings.MEDIA_ROOT, 'enhanced_gif', f'{self.id}_enhanced_gif.gif')

        # Create the GIF using the create_gif method
        self.create_enhanced_gif_from_video(video_path, enhanced_gif_path)

        # Save the enhanced_gif path and enhanced_file path to the respective fields of the Video model
        self.enhanced_file = f'enhanced_file/{self.id}_enhanced.mp4'
        self.enhanced_gif = f'enhanced_gif/{self.id}_enhanced_gif.gif'
        self.save()
        
        return enhanced_gif_path

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
    
    
    def save_(self, *args, **kwargs):
        print("save e sukse")
        # Check if the file field is not empty and the file size is greater than 25 MB
        if self.file and self.file.size > 25 * 1024 * 1024:
            print("sukse")
            # Open the video file using moviepy
            video_clip = VideoFileClip(self.file.path)

            # Resize the video while maintaining the aspect ratio
            resized_clip = video_clip.resize(width=640)  # Adjust the width as needed

            # Compress the video to meet the desired file size
            compressed_clip = resized_clip.write_videofile(self.file.path, codec="libx264", bitrate="800k")

            # Close the video clips
            video_clip.close()
            resized_clip.close()

        super().save(*args, **kwargs)
    
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
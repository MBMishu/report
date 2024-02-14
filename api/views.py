from django.core import paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from rest_framework import status, viewsets, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


from .models import *
from .serializers import *

from ultralytics import YOLO
import cv2
from PIL import Image
import os
import uuid
from django.conf import settings
import numpy as np
import shutil

# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas



from django.template.loader import get_template
from xhtml2pdf import pisa


from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage

import datetime
from django.shortcuts import get_object_or_404

@api_view(['GET'])
def all_detected_object_pdfs(request):
    detected_object_pdfs = DetectedObjectPDF.objects.all().order_by('-created_at')
    serializer = DetectedObjectPDFSerializer(detected_object_pdfs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def detected_object_pdf_by_id(request, id):
    detected_object_pdf = get_object_or_404(DetectedObjectPDF, video=id)
    serializer = DetectedObjectPDFSerializer(detected_object_pdf)
    return Response(serializer.data)

@api_view(['GET'])
def detected_frame_by_id(request, id):
    detected_frame = DetectedFrame.objects.filter(video=id).order_by('-created_at')
    serializer = DetectedFrameSerializer(detected_frame,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def video_by_id(request, id):
    video = get_object_or_404(Video, id=id)
    serializer = VideoSerializer(video)
    return Response(serializer.data)

@api_view(['GET'])
def all_video(request):
    recoded_video = Video.objects.all().order_by('-id')
    serializer = VideoSerializer(recoded_video, many=True)
    return Response(serializer.data)



@api_view(['POST'])
def videoUpload(request):
    video_serializer = VideoSerializer(data=request.data)

    if video_serializer.is_valid():
        video = video_serializer.save()
        video.save_()
        print(video.file.path)
        
        model = YOLO(os.path.join(settings.BASE_DIR, "static","models","best.pt"))

        video_path = video.file.path
        
        output_folder = os.path.join(settings.MEDIA_ROOT, 'frames')
        output_detected_frames = os.path.join(settings.MEDIA_ROOT, 'detected_frames')
        
        cap = cv2.VideoCapture(video_path)
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if not os.path.exists(output_folder):
            os.makedirs (output_folder)
            
        if not os.path.exists(output_detected_frames):
            os.makedirs (output_detected_frames)
        
        count = 0
        save_gif = False
        
        for frame_index in range(frame_count):
        
            if frame_index % 10 == 0:
                
                success, image = cap.read()
                if not success:
                    break
                
                # capture frame from video
                frame_filename = f"{video.id}_frame_{count}.jpg"
                frame_path = os.path.join(output_folder, frame_filename)
                cv2.imwrite(frame_path, image)
                
                # predict
                pil_image = Image.open(frame_path)
                results_list = model.predict(source=[pil_image], save=True)
                
                detect_hyse = False
                if results_list:
                    # Assuming results_list contains a single element
                    detection_boxes = results_list[0].boxes
                    
                    if detection_boxes.shape[0] > 0:
                        detect_hyse = True
                        save_gif = True
                    else:
                        detect_hyse = False

                if detect_hyse:
                    #  get recentpredict folder                
                    folder_path = "runs/detect"
                    recent_subfolder = get_recent_subfolder(folder_path)
                    img_path = f"{recent_subfolder}/image0.jpg"
                    
                    # copy to media 
                    unique_id = str(uuid.uuid4())
                    output_img_path = os.path.join(output_detected_frames, f"frame_{unique_id}_{video.id}.jpg")
                    shutil.copy(img_path, output_img_path)
                    
                            # Read the content of the image file
                    with open(output_img_path, 'rb') as image_file:
                        image_content = image_file.read()

                    
                    # Save the content to DetectedFrame model
                    detected_frame = DetectedFrame(video=video, frame_number=unique_id)
                    detected_frame.file.save(f"frame_{unique_id}_{video.id}.jpg", ContentFile(image_content))
                    detected_frame.save()
                   
                
                count += 1
                
        
        cap.release()
      
        
        video.save_video_as_gif()
        video.create_enhanced_gif()
       

        if save_gif:
            print("generate report")
            video.create_detected_gif()
            generate_pdf_for_video(video.id)
            return Response({"message": "Video uploaded and objects detected successfully","id":video.id}, status=status.HTTP_201_CREATED)
        
        else:
            return Response({"message": "Video uploaded successfully but no object detected","id":video.id}, status=status.HTTP_201_CREATED)
    
    else:
        return Response("Data did not added")



def get_recent_subfolder(folder_path):
    # Get a list of all files and directories in the specified folder
    entries = os.listdir(folder_path)

    # Filter out subdirectories
    subdirectories = [entry for entry in entries if os.path.isdir(os.path.join(folder_path, entry))]

    # Get the full path for each subdirectory
    subdirectory_paths = [os.path.join(folder_path, subdirectory) for subdirectory in subdirectories]

    # Sort subdirectories by modification time (most recent first)
    sorted_subdirectories = sorted(subdirectory_paths, key=lambda x: os.path.getmtime(x), reverse=True)

    # Return the most recently modified subdirectory
    if sorted_subdirectories:
        return sorted_subdirectories[0]
    else:
        return None



def render_to_pdf(template_path, context_dict):
    template = get_template(template_path)
    html = template.render(context_dict)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="output.pdf"'

    # Create a PDF object and write the HTML content to it
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF')

    return response



def generate_pdf_for_video(video_id):
    
    detected_frames = DetectedFrame.objects.filter(video_id=video_id)[:6]
    
    map_ = os.path.join(settings.MEDIA_ROOT, 'map.png')
    

    img1 = os.path.join(settings.BASE_DIR,detected_frames[0].file.path)
    img2 = os.path.join(settings.BASE_DIR,detected_frames[1].file.path)
    img3 = os.path.join(settings.BASE_DIR,detected_frames[2].file.path)
    img4 = os.path.join(settings.BASE_DIR,detected_frames[3].file.path)
    img5 = os.path.join(settings.BASE_DIR,detected_frames[4].file.path)
    img6 = os.path.join(settings.BASE_DIR,detected_frames[5].file.path)

    
    current_datetime = datetime.datetime.now()
    
    current_datetime_ = current_datetime.strftime("%Y-%m-%d")
    
    current_datetime_string = current_datetime.strftime("%H:%M:%S")
    
    generate_datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    duration_minutes = 5
    
    depth = -5


    end_time = current_datetime + datetime.timedelta(minutes=duration_minutes)
    end_datetime_string = end_time.strftime("%H:%M:%S")

  
    
    context = {'detected_frames': detected_frames,
            'map': map_,
            'img1': img1,
            'img2': img2,
            'img3': img3,
            'img4': img4,
            'img5': img5,
            'img6': img6,
         
            'current_datetime_string':current_datetime_,
            'start_datetime_string':current_datetime_string,
            'end_datetime_string':end_datetime_string,
            'generate_datetime_string':generate_datetime_string,
            'duration_minutes':duration_minutes,
            'depth':depth,
            }
    
    output_pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdf', f'{video_id}_temp.pdf')
    with open(output_pdf_path, 'wb') as pdf_file:
        pdf_file.write(render_to_pdf('pdf.html', context).content)
        
    with open(output_pdf_path, 'rb') as pdf_file:
        pdf_content = pdf_file.read()
    
    detected_object_pdf = DetectedObjectPDF(video_id=video_id)
    detected_object_pdf.pdf_file.save(f'{video_id}_detected_frames.pdf', ContentFile(pdf_content))
    detected_object_pdf.save()

    return detected_object_pdf

def home(request):
    detected_frames = DetectedFrame.objects.filter(video_id=151)[:7]
    
    map_ = os.path.join(settings.MEDIA_ROOT, 'map.png')
    
    img1 = os.path.join(settings.BASE_DIR,detected_frames[0].file.path)
    img2 = os.path.join(settings.BASE_DIR,detected_frames[1].file.path)
    img3 = os.path.join(settings.BASE_DIR,detected_frames[2].file.path)
    img4 = os.path.join(settings.BASE_DIR,detected_frames[3].file.path)
    img5 = os.path.join(settings.BASE_DIR,detected_frames[4].file.path)
    img6 = os.path.join(settings.BASE_DIR,detected_frames[5].file.path)
    img7 = os.path.join(settings.BASE_DIR,detected_frames[6].file.path)
    
    
    context = {'detected_frames': detected_frames,
            'map': map_,
            'img1': img1,
            'img2': img2,
            'img3': img3,
            'img4': img4,
            'img5': img5,
            'img7': img7,
            'img6': img6,'current_date': datetime.datetime.now().strftime("%Y-%m-%d"),}
    return render(request, 'pdf.html',context)


from django.shortcuts import render,get_object_or_404
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import viewsets
from .models import mainUserCentral
from .serializers import MainUserCentralSerializer
from .utils import create_supabase_folder,upload_video_to_bucket,list_user_videos_bucket,get_video_url_from_supabase,list_user_documents_bucket,get_document_url_from_supabase,upload_document_to_bucket
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

#The api for creation of the user with the trigger to create and initialize Supabase folders in bucket.
@api_view(['GET', 'POST'])
def data_list(request):
    if request.method=='GET':
        data=mainUserCentral.objects.all()
        serializer = MainUserCentralSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method =='POST':
        serializer=MainUserCentralSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            if not instance.UniqueID:
                instance.UniqueID = f'SIH1016FS{instance.id:03}'
                instance.bucket_url=f'https://zwxpudmuwltonzohjbse.supabase.co/storage/v1/object/public/sihbucketbackend/{instance.UniqueID}/'
                instance.save() 
            create_supabase_folder(instance.UniqueID)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#The api for single user request. Valid for get request only.
@api_view(['GET'])
def fetch_single_data(request, UniqueID, password):
    #obj=mainUserCentral.objects.filter(name=name,  email=email)
    obj = get_object_or_404(mainUserCentral, UniqueID=UniqueID, password=password)
    serializer=MainUserCentralSerializer(obj)
    return Response(serializer.data, status=status.HTTP_200_OK)

#The api for managing video uploads
@api_view(['POST','GET'])
def videoMan(request, UniqueID):
    if request.method=='POST':
        try:
            video_file = request.FILES.get('video_file', None)
            if video_file:
                if isinstance(video_file, InMemoryUploadedFile):
                    video_data = video_file.read()
                    destination = f'{UniqueID}/Videos/{video_file.name}'
                    resp = upload_video_to_bucket(destination, video_data)
                    print(resp)
                    if resp.status_code == 200:
                        return Response({'message': 'Video uploaded successfully'}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message': 'Failed to upload video to Supabase'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({'message': 'Invalid file format'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if request.method=='GET':
        try:
            data = list_user_videos_bucket(UniqueID)
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#The api for getting the public url for a video file
@api_view(['GET'])
def get_video_url(request, UniqueID, file_name):
    try:
        data = get_video_url_from_supabase(UniqueID, file_name)
    except:
        return Response({"data":"error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"url" : data}, status=status.HTTP_200_OK)

#The API for document manager
@api_view(['POST','GET'])
def docMan(request, UniqueID):
    if request.method=='POST':
        try:
            document_file = request.FILES.get('document_file', None)
            if document_file:
                if isinstance(document_file, InMemoryUploadedFile):
                    document_data = document_file.read()
                    destination = f'{UniqueID}/Documents/{document_file.name}'
                    resp = upload_document_to_bucket(destination, document_data)
                    print(resp)
                    if resp.status_code == 200:
                        return Response({'message': 'Document uploaded successfully'}, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'message': 'Failed to upload Document to Supabase'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    return Response({'message': 'Invalid file format'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if request.method=='GET':
        try:
            data = list_user_documents_bucket(UniqueID)
            return Response(data, status=status.HTTP_200_OK)
        except:
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#The api for getting the public url for a document file
@api_view(['GET'])
def get_document_url(request, UniqueID, file_name):
    try:
        data = get_document_url_from_supabase(UniqueID, file_name)
    except:
        return Response({"data":"error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({"url" : data}, status=status.HTTP_200_OK)
    



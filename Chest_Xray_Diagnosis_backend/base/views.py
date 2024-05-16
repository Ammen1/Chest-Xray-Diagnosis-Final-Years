from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Image, Prediction, Disease
from .serializers import ( 
    DiseaseSerializer,
    EmailValidationOnForgotPasswordSerializer,
    PatientSerializer,
    UserSerializer,
    PredictionSerializer,
    DoctorProfileSerializer,
    ImageSerializer
)
from tensorflow.keras.models import load_model
import tensorflow as tf
import cv2 as cv
import numpy as np
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User 
from .models import DoctorProfile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer
import cv2 as cv
import numpy as np
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Prediction 
from tensorflow.keras.models import load_model
from rest_framework_simplejwt.tokens import OutstandingToken, TokenError
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import DoctorProfile
from .serializers import DoctorProfileSerializer
from django.contrib.auth import logout
from django.http import JsonResponse


DISEASE_NAMES = ['Cardiomegaly', 'Emphysema', 'Effusion', 'Hernia', 'Nodule', 'Pneumothorax', 'Atelectasis',
                 'Pleural_Thickening', 'Mass', 'Edema', 'Consolidation', 'Infiltration', 'Fibrosis', 'Pneumonia']

from .models import Prediction, Patient
from keras.preprocessing import image
class Image_views(generics.CreateAPIView):
    
    serializer_class = PredictionSerializer

    def post(self, request, *args, **kwargs):
        image_data = request.FILES.get('image')
        patient_id = request.data.get('patient')  
        if not image_data:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not image_data.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return Response({'error': 'Invalid image format. Supported formats: PNG, JPEG'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(pk=patient_id)
            print(patient)
            
            img = cv.imdecode(np.fromstring(image_data.read(), np.uint8), cv.IMREAD_COLOR)
            # img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Convert image to grayscale
            # img_resized = cv.resize(img, (1, 224, 224, 1))
            # img_array = img_resized / 255.0
            # img_array = np.expand_dims(img_array, axis=(0, 1))  # Add channel dimension
            img = cv.resize(img, (224,224))
            x = image.img_to_array(img)
            x = x.reshape((1,) + x.shape)  
            x = x / 255.0  
            x = (x - x.mean()) / x.std()  
            # Load the Keras model
            keras_model_path = "model/densenet_with_out_sequential.h5"
            keras_model = load_model(keras_model_path)
            
            # Make prediction using the loaded model
            prediction = keras_model.predict(x)
            print(prediction)
            diseases = DISEASE_NAMES[np.argmax(prediction)]
            
            # Save prediction result to the database with patient data
            new_prediction = Prediction(image=image_data, diseases=diseases, patient=patient)
            new_prediction.save()
            
            return Response({'prediction': diseases})
            
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UploadImage(generics.CreateAPIView):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()

class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                print(f"Error saving user: {e}")
                return Response({"detail": "An error occurred while creating the user."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            token = OutstandingToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)



def logout_view(request):
    permission_classes = [IsAuthenticated]
    logout(request)
    return JsonResponse({'message': 'Logged out successfully'}, status=200)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):   
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['user_role'] = user.get_user_role  

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data['username'] = self.user.username
        data['email'] = self.user.email
        data['user_role'] = self.user.get_user_role
        print(data)
        return data
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response_data = {
            'access_token': str(serializer.validated_data['access']),
            'refresh_token': str(serializer.validated_data['refresh']),
            'user_role': str(serializer.validated_data['user_role']),
            'email': str(serializer.validated_data['email']),
            'username': str(serializer.validated_data['username']),
       
        }
        print(response_data)
        return Response(response_data)



class DoctorList(generics.ListAPIView):
    serializer_class = DoctorProfileSerializer
    queryset = DoctorProfile.objects.all()

class VerifyDoctorView(APIView):
    def post(self, request, doctor_id):
        try:
            doctor_profile = DoctorProfile.objects.get(pk=doctor_id)

            doctor_profile.verify_doctor()

            return Response({"detail": "Doctor verified successfully."}, status=status.HTTP_200_OK)

        except DoctorProfile.DoesNotExist:
            return Response({"detail": "Doctor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error verifying doctor: {e}")
            return Response({"detail": "An error occurred while verifying the doctor."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserListView(APIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()        
        total_users = User.get_total_users()
        total_doctors = User.get_total_doctors()       
        serializer = UserSerializer(users, many=True)       
        data = {
            'total_users': total_users,
            'total_doctors': total_doctors,
            'users': serializer.data
        }
        
        return Response(data, status=status.HTTP_200_OK)
    

class PredictionListView(generics.ListAPIView):
    serializer_class = PredictionSerializer
    queryset = Prediction.objects.all()
    

class DockorAddView(generics.CreateAPIView):
    serializer_class = DoctorProfileSerializer

class PateintAddView(generics.CreateAPIView):
    serializer_class = PatientSerializer

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "User and Student created successfully."}, status=status.HTTP_201_CREATED)

class AllPatient(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()



class DoctorProfileCreateAPIView(APIView):
    def post(self, request, format=None):
        serializer = DoctorProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    
class EmailValidationOnForgotPasswordView(generics.CreateAPIView):
    serializer_class = EmailValidationOnForgotPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            validated_email = serializer.validated_data['email']
            user = User.objects.get(email__iexact=validated_email)
        except User.DoesNotExist:
            raise serializers.ValidationError("There is no user registered with the specified E-mail address.")
        except User.MultipleObjectsReturned:
            raise serializers.ValidationError("Multiple users found with the specified E-mail address. Contact support.")

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        user.password_reset_token = token
        user.save()

        frontend_url = "http://127.0.0.1:8000/api/account"  
        reset_link = f"{frontend_url}/reset-password/{uid}/{token}/"

        send_mail(
            "Password Reset",
            f"Click the following link to reset your password: {reset_link}",
            settings.EMAIL_FROM_ADDRESS,
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "Reset link sent to the provided email address."}, status=status.HTTP_200_OK)




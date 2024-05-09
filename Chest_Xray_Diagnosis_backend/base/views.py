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
    PredictionSerializer, 
    DiseaseSerializer,
    EmailValidationOnForgotPasswordSerializer,
    ProfileUpdateSerializer,
    DoctorAddSerializer,
    PatientSerializer,
    Imageser,
    UserSerializer,
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
from .models import User, Doctor


import cv2 as cv
import numpy as np
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Prediction  # Import the Prediction model from your Django application
from tensorflow.keras.models import load_model

# Define disease names
DISEASE_NAMES = ['Cardiomegaly', 'Emphysema', 'Effusion', 'Hernia', 'Nodule', 'Pneumothorax', 'Atelectasis',
                 'Pleural_Thickening', 'Mass', 'Edema', 'Consolidation', 'Infiltration', 'Fibrosis', 'Pneumonia']

class Image_views(generics.CreateAPIView):
    
    serializer_class = Imageser

    def post(self, request, *args, **kwargs):
        image_data = request.FILES.get('image')
        if not image_data:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not image_data.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            return Response({'error': 'Invalid image format. Supported formats: PNG, JPEG'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            img = cv.imdecode(np.fromstring(image_data.read(), np.uint8), cv.IMREAD_COLOR)
            img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # Convert image to grayscale
            img_resized = cv.resize(img_gray, (128, 128))
            img_array = img_resized / 255.0
            img_array = np.expand_dims(img_array, axis=(0, -1))  # Add channel dimension
            
            # Load the Keras model
            keras_model_path = "model/le_tame_model_yehew_esti_eneyew_2.h5"
            keras_model = load_model(keras_model_path)
            
            # Make prediction using the loaded model
            prediction = keras_model.predict(img_array)
            print(prediction)
            predicted_label = DISEASE_NAMES[np.argmax(prediction)]
            print(predicted_label)
            
            # Save prediction result to the database
            new_prediction = Prediction(image=image_data, predicted_label=predicted_label)
            new_prediction.save()
            
            return Response({'prediction': predicted_label})
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_205_RESET_CONTENT)

class SignUpView(APIView):
    def post(self, request):
        request.data['is_doctor'] = True  # Fix typo
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileUpdateSerializer
    queryset = User.objects.all()


class UserListView(APIView):
    def get(self, request, *args, **kwargs):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AllDataView(APIView):
    def get(self, request, format=None):
        predictions = Prediction.objects.all()
        serializer = PredictionSerializer(predictions, many=True)
        return Response(serializer.data)

class PredictionView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, format=None):
        data = request.data
        request_image = data.get("image")
        if not request_image:
            return Response("No image provided", status=status.HTTP_400_BAD_REQUEST)
        
        # Process the image
        try:
            image = cv.imdecode(np.fromstring(request_image.read(), np.uint8), cv.IMREAD_COLOR)
            image_size = image.shape[:2]
            image_name = data.get("imageName")
            scanned = data.get("scanned", "").lower() == "true"
            
            verification_image = cv.resize(image, (128, 128))
            verification_image = np.reshape(verification_image, (1, 224, 224, 3))
            input_data = np.array(verification_image, dtype=np.float32)
            interpreter.set_tensor(input_details[0]["index"], input_data)
            interpreter.invoke()
            output_data = interpreter.get_tensor(output_details[0]["index"])[0][0]
            if output_data > 0.2:
                return Response("Invalid image", status=status.HTTP_400_BAD_REQUEST)

            # Rotate image if needed
            rotated = False
            if image.shape[0] > image.shape[1]:
                image = cv.rotate(image, cv.ROTATE_90_COUNTERCLOCKWISE)
                rotated = True

            # Resize and process the image
            image = cv.resize(image, (512, 512))
            image_name = 'xRay'
            predicted_image, predicted_diseases, severity = self.segment_image(image=image)

            # Save prediction
            prediction = Prediction(
                imageName=image_name,
                scanned=scanned,
                image=request_image,
                severity=severity,
            )
            prediction.save()

            # Rotate image back if rotated
            if rotated:
                predicted_image = cv.rotate(predicted_image, cv.ROTATE_90_CLOCKWISE)

            # Resize and save the predicted image
            predicted_image = cv.resize(predicted_image, image_size[::-1])
            _, buf = cv.imencode(".jpg", predicted_image)
            content = ContentFile(buf.tobytes())
            prediction.predictedImage.save(image_name, content)

            # Create or get disease objects
            disease_objects = [Disease.objects.get_or_create(name=name)[0] for name in predicted_diseases]

            # Add diseases to the prediction
            prediction.diseases.add(*disease_objects)

            serializer = PredictionSerializer(prediction)
            return Response(serializer.data)

        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def segment_image(self, image):
        # Image segmentation and disease prediction logic
        return predicted_image, predicted_diseases, severity

class DockorAddView(generics.CreateAPIView):
    serializer_class = DoctorAddSerializer

class PateintAddView(generics.CreateAPIView):
    serializer_class = PatientSerializer

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "User and Student created successfully."}, status=status.HTTP_201_CREATED)
class ProfileUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileUpdateSerializer
    queryset = User.objects.all()

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



from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, DoctorSerializer  # Import the DoctorSerializer
from .models import Doctor  # Import the Doctor model

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UsersSerializer
from .models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, DoctorAddSerializer
from .models import User, Doctor

class DashboardAPI(APIView):
    def get(self, request, *args, **kwargs):
        all_users = User.objects.all()
        doctors = Doctor.objects.all()  # Get queryset of doctors
        doctor_count = doctors.count()
        admin_count = User.objects.filter(is_superuser=True).count()
        current_month_users = User.objects.filter(date_joined__month=timezone.now().month).count()
        last_month_users = User.objects.filter(date_joined__month=timezone.now().month - 1).count()
        recent_users = User.objects.order_by('-date_joined')[:5]

        user_serializer = UserSerializer(all_users, many=True)
        doctor_serializer = DoctorAddSerializer(doctors, many=True)  # Pass queryset to serializer

        data = {
            'all_users': user_serializer.data,
            'doctor_count': doctor_count,
            'admin_count': admin_count,
            'current_month_users': current_month_users,
            'last_month_users': last_month_users,
            'recent_users': recent_users,
            'doctors': doctor_serializer.data,  # Include serialized doctors data in response
        }
        return Response(data, status=status.HTTP_200_OK)









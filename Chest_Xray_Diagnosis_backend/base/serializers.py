from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Doctor, Patient, Disease,Prediction,  GENDERS, Image
from datetime import datetime
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.mail import send_mail
from .models import User



User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    doctor_count = serializers.SerializerMethodField()
    superuser_count = serializers.SerializerMethodField()
    # totalusers_count = serializers.SerializerMethodField()
    

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'doctor_count', 'gender', 'phone',  'superuser_count')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_role'] = instance.get_user_role
        return representation

    def get_total_users(self, instance):
        return instance.get_total_users()

    def get_doctor_count(self, instance):
        return instance.get_doctor_count()

    def get_superuser_count(self, instance):
        return instance.get_superuser_count()


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class DoctorAddSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    phone = serializers.CharField(max_length=30)
    email = serializers.CharField(max_length=30)
    age = serializers.CharField(max_length=30)

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create(
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                phone=validated_data['phone'],
                email=validated_data['email'],
                age=validated_data['age'],
                is_doctor=True
            )

            registration_date = datetime.now().strftime("%Y")
            total_doctor_count = User.objects.filter(is_doctor=True).count()
            generated_username = (
                f"{settings.DOCTOR_ID_PREFIX}-{registration_date}-{total_doctor_count}"
            )
            generated_password = User.objects.make_random_password()

            user.username = generated_username
            user.set_password(generated_password)
            user.save()

            send_mail(
                "Your account credentials from Chest_Xray_Diagnosis",
                f"Your username: {generated_username}\nYour password: {generated_password}\n You Are Our Doctor",
                "teachingandlearningsupport@gooderash.com",
                [user.email],
                fail_silently=False,
            )

            return user


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    gender = serializers.ChoiceField(choices=GENDERS)
    email = serializers.EmailField()
    phone = serializers.CharField()
    address = serializers.CharField()

    def update(self, instance, validated_data):
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']
        instance.gender = validated_data['gender']
        instance.email = validated_data['email']
        instance.phone = validated_data['phone']
        instance.address = validated_data['address']
        instance.save()
        return instance


class EmailValidationOnForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value, is_active=True).exists():
            raise serializers.ValidationError("There is no active user registered with the specified E-mail address.")
        return value

    def create(self, validated_data):
        validated_email = validated_data['email']
        user = User.objects.get(email__iexact=validated_email)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        user.password_reset_token = token
        user.save()

        frontend_url = "http://localhost:5173/dashboard?tab=addstudents/"  

        reset_link = f"{frontend_url}{uid}/{token}/"
        send_mail(
            "Password Reset",
            f"Click the following link to reset your password: {reset_link}",
            settings.EMAIL_FROM_ADDRESS,
            [user.email],
            fail_silently=False,
        )

        return {"message": "Reset link sent to the provided email address."}


class PredictionSerializer(serializers.ModelSerializer):
    diseases_summary = serializers.SerializerMethodField()

    class Meta:
        model = Prediction
        fields = '__all__'

    def get_diseases_summary(self, obj):
        return obj.get_diseases_summary()



class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = '__all__'
        
class Imageser(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'       
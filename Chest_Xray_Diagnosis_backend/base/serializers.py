from rest_framework import serializers
from .models import User, DoctorProfile, Patient, Disease, Prediction, Image 

class UserSerializer(serializers.ModelSerializer):
    doctor_profile = serializers.PrimaryKeyRelatedField(queryset=DoctorProfile.objects.all(), allow_null=True, required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = '__all__'
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_role'] = instance.get_user_role
        return representation

    def get_superuser_count(self, instance):
        return instance.get_superuser_count()
    
    
class DoctorProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) 

    class Meta:
        model = DoctorProfile
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name', 'patient_id']

class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = ['id', 'name']

class PredictionSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Prediction
        fields = ['id', 'patient', 'image', 'diseases', 'date']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']

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
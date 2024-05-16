from django.urls import path
from .views import *
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('classify/', Image_views.as_view(), name='classify_image'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('logout/', logout_view, name='logout'),
    # path('logout/', logout_view.as_view(), name='logout'),
    path('dockor/add/', DockorAddView.as_view(), name='doctor-add'),
    path('pateint/add/', PateintAddView.as_view(), name='pateint-add'),
    path('pateint/list/', AllPatient.as_view(), name='pateint-list'),
    path('doctor/list/', DoctorList.as_view(), name='pateint-list'),
    path('verify-doctor/<int:doctor_id>/', VerifyDoctorView.as_view(), name='verify-doctor'),
    path('forgot-password/', EmailValidationOnForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('getusers/', UserListView.as_view(), name='getusers'),
    path('predictions/', PredictionListView.as_view(), name='prediction-list'),
    path('doctor/create/', DoctorProfileCreateAPIView.as_view(), name='doctor-create'),
    path('upload/image/', UploadImage.as_view(), name='upload-image'),
]

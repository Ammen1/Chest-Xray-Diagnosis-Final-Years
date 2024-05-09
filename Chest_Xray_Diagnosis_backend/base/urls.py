from django.urls import path
from .views import *
# from .views import UserLoginView, MyTokenObtainPairView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth import views as auth_views
# from .views import logout_view

urlpatterns = [
    path('classify/', Image_views.as_view(), name='classify_image'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('dockor/add/', DockorAddView.as_view(), name='doctor-add'),
    path('pateint/add/', PateintAddView.as_view(), name='pateint-add'),
    path('dashboard/', DashboardAPI.as_view(), name='dashboard'),
    path('profile/update/<int:pk>/', ProfileUpdateView.as_view(), name='profile-update'),
    path('forgot-password/', EmailValidationOnForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('getusers/', UserListView.as_view(), name='getusers'),
]

from django.contrib.auth.models import AbstractUser, UserManager, Group, Permission
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .validators import ASCIIUsernameValidator
from PIL import Image
from django.contrib.auth.models import UserManager


# Gender choices
GENDERS = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

from django.contrib.auth.models import UserManager

class CustomUserManager(UserManager):
    pass

class User(AbstractUser):
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=100, blank=True, verbose_name=_("Last Name"))
    age = models.PositiveIntegerField(blank=True, null=True, verbose_name=_("Age"))
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, verbose_name=_("Gender"))
    phone = models.CharField(max_length=60, blank=True, verbose_name=_("Phone"))
    is_doctor = models.BooleanField(default=False, verbose_name=_("Is Doctor"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    doctor_profile = models.OneToOneField('DoctorProfile', related_name='doctor_profile', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Doctor Profile"))

    username_validator = ASCIIUsernameValidator()
    objects = UserManager()

    class Meta:
        ordering = ("username",)
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def get_full_name(self):
        """Get the user's full name."""
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})"
    
    @property
    def get_user_role(self):
        if self.is_superuser:
            role = "Admin"
        elif self.is_doctor:
            role = "Doctor"
        else:
            role = "user"  

        return role

    @classmethod
    def get_total_users(cls):
        """Return the total number of users."""
        return cls.objects.filter(is_active=True).count()

    @classmethod
    def get_total_doctors(cls):
        """Return the total number of doctors."""
        return cls.objects.filter(is_doctor=True).count()


class Patient(models.Model):
    name = models.CharField(max_length=100, blank=True, verbose_name=_("Name"))
    patient_id = models.PositiveIntegerField(unique=True, verbose_name=_("Patient ID"))

    class Meta:
        ordering = ("patient_id",)
        verbose_name = _("Patient")
        verbose_name_plural = _("Patients")

    def __str__(self):
        return self.name


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='related_doctor_profile',
        verbose_name=_("User")
    )
    specialty = models.CharField(max_length=100, blank=True, verbose_name=_("Specialty"))
    medical_license_number = models.CharField(max_length=100, blank=True, verbose_name=_("Medical License Number"))
    patients = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='doctors', blank=True, null=True, verbose_name=_("Patients"))
    cv = models.FileField(upload_to='cvs/', blank=True, null=True, verbose_name=_("CV"))
    verified = models.BooleanField(default=False, verbose_name=_("Verified"))

    class Meta:
        verbose_name = _("Doctor Profile")
        verbose_name_plural = _("Doctor Profiles")

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialty}"

    def verify_doctor(self):
        """Method for superuser to verify the doctor's profile."""
        self.verified = True
        self.save()


class Disease(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Name"))

    def __str__(self):
        return self.name

class Prediction(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='predictions', blank=True, null=True, verbose_name=_("Patient"))
    image = models.ImageField(upload_to='original/', default='image.jpg', verbose_name=_("Image"))
    diseases = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Diseases"))
    date = models.DateTimeField(auto_now_add=True, verbose_name=_("Date"))

    class Meta:
        ordering = ('date',)
        verbose_name = _("Prediction")
        verbose_name_plural = _("Predictions")

    def __str__(self):
        return f"Prediction for {self.patient} on {self.date}"

class Image(models.Model):
    image = models.ImageField(upload_to='images/', default='image.jpg', verbose_name=_("Image"))
    category = models.CharField(max_length=200, blank=True, null=True, verbose_name=_("Diseases"))

    def __str__(self):
        return str(self.image)



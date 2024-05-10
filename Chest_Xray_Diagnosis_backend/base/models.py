from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import os
from .validators import ASCIIUsernameValidator
from PIL import Image


def upload_to(instance, filename):
    return f'profile_pics/{filename}'


class CustomUserManager(UserManager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = (
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )
            queryset = queryset.filter(
                or_lookup
            ).distinct() 
        return queryset


GENDERS = (("M", "Male"), ("F", "Female"))


class User(AbstractUser):
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, null=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    is_doctor = models.BooleanField(default=False)
    picture = models.ImageField(
        upload_to="profile_pictures/%Y/%m/%d/", default="default.png", null=True
    )
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    username_validator = ASCIIUsernameValidator()

    objects = CustomUserManager() 

    class Meta:
        ordering = ("username",)

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    
    @classmethod
    def get_total_users(cls):
        return cls.objects.filter(is_active=True).count()

    @classmethod
    def get_doctor_count(cls):
        return cls.objects.filter(is_doctor=True).count()
    
    @classmethod
    def get_superuser_count(cls):
        return cls.objects.filter(is_superuser=True).count()

    def __str__(self):
        return "{} ({})".format(self.username, self.get_full_name)

    @property
    def get_user_role(self):
        if self.is_superuser:
            role = "Admin"
        elif self.is_doctor:
            role = "Doctor"
        else:
            role = "Unknown Role"  

        return role

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + "default.png"
            return no_picture


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.picture.path)
        except:
            pass

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + "default.png":
            self.picture.delete()
        super().delete(*args, **kwargs)


class Patient(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    patient_id = models.PositiveIntegerField(unique=True)

    class Meta:
        ordering = ("patient_id",)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.delete()
        super().delete(*args, **kwargs)

class Doctor(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    patients = models.ForeignKey(Patient,on_delete=models.CASCADE, related_name='doctors', blank=True)

    def __str__(self):
        return self.doctor.get_full_name




class FeedBack(models.Model):
    pass
    
    
class Disease(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Prediction(models.Model):
    patient = models.ForeignKey(Patient , on_delete=models.CASCADE, related_name='patient', default="", blank=True, null=True)
    image = models.ImageField(upload_to='original/', default='image.jpg')
    diseases = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ('date',)



class Image(models.Model):
    image = models.ImageField(upload_to='images/', default='image.jpg')




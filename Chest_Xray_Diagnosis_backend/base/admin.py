from django.contrib import admin
from .models import User, Patient, DoctorProfile, Disease, Prediction, Image

admin.site.register(User)
admin.site.register(Patient)
admin.site.register(DoctorProfile)
admin.site.register(Disease)
admin.site.register(Prediction)
admin.site.register(Image)

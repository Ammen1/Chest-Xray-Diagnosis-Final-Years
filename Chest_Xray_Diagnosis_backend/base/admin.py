from django.contrib import admin
from .models import User, Patient, Doctor, FeedBack, Disease, Prediction, Image

admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(FeedBack)
admin.site.register(Disease)
admin.site.register(Prediction)
admin.site.register(Image)

from django.test import TestCase
from base.models import User, Patient, DoctorProfile, Prediction
from django.contrib.auth import get_user_model

class UserModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser', password='testpassword', first_name='John', last_name='Doe', age=30, gender='M', phone='1234567890', email='test@example.com', is_doctor=False)

    def test_get_full_name(self):
        user = User.objects.get(username='testuser')
        self.assertEqual(user.get_full_name(), 'John Doe')

    def test_get_user_role(self):
        user = User.objects.get(username='testuser')
        self.assertEqual(user.get_user_role, 'user')

    def test_get_total_users(self):
        total_users = User.get_total_users()
        self.assertEqual(total_users, 1)

    def test_get_total_doctors(self):
        total_doctors = User.get_total_doctors()
        self.assertEqual(total_doctors, 0)

    def test_user_str_representation(self):
        user = User.objects.get(username='testuser')
        self.assertEqual(str(user), 'testuser (John Doe)')






class DoctorProfileModelTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password'
        )
        self.patient = Patient.objects.create(name='Test Patient', patient_id=1)
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.user,
            specialty='Cardiology',
            medical_license_number='12345',
            patients=self.patient,
            cv=None,
            verified=False
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.doctor_profile),
            f"{self.user.get_full_name()} - Cardiology"
        )

    def test_verify_doctor(self):
        self.assertFalse(self.doctor_profile.verified)
        self.doctor_profile.verify_doctor()
        self.assertTrue(self.doctor_profile.verified)




from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.response import Response
from .views import Image_views
from .models import Patient, Prediction
from unittest.mock import MagicMock, patch
import cv2 as cv
import numpy as np
from tensorflow.keras.models import load_model

class TestImageViews(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.view = Image_views.as_view()

    @patch('cv2.imdecode')
    @patch('numpy.fromstring')
    @patch('cv2.resize')
    @patch('tensorflow.keras.models.load_model')
    @patch.object(Patient.objects, 'get')
    def test_post_request(self, mock_patient_get, mock_load_model, mock_resize, mock_fromstring, mock_imdecode):
        mock_patient = MagicMock(spec=Patient)
        mock_patient.pk = 1
        mock_patient_get.return_value = mock_patient
        mock_load_model.return_value = MagicMock(spec=load_model)
        mock_resize.return_value = MagicMock()
        mock_fromstring.return_value = MagicMock()
        mock_imdecode.return_value = MagicMock()
        
        image_file = MagicMock(name='image_file')
        image_file.name = 'test_image.jpg'
        image_file.read.return_value = b'fake_image_data'

        request = self.factory.post('/api/images/', {'image': image_file, 'patient': 1})

        response = self.view(request)
        self.assertTrue(Prediction.objects.exists())

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Add more test cases for different scenarios as needed



from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

class ImageViewTest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
    
    def tearDown(self):
        self.browser.quit()
    
    def test_image_upload(self):
        self.browser.get(self.live_server_url)
        image_input = self.browser.find_element_by_id('id_image')  
        image_path = 'media/cvs/00000003_001_lf6CdUC.png' 
        image_input.send_keys(image_path)
        
        patient_input = self.browser.find_element_by_id('id_patient') 
        patient_input.send_keys('1') 
        
        submit_button = self.browser.find_element_by_id('submit_button_id')  
        submit_button.click()
        success_message = self.browser.find_element_by_id('success_message_id').text
        self.assertIn('Image uploaded successfully', success_message)

import React, { useState, useEffect } from 'react';
import { Alert, Button, FileInput, Select, TextInput } from 'flowbite-react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import {
  getDownloadURL,
  getStorage,
  ref,
  uploadBytesResumable,
} from 'firebase/storage';
import { app } from '../firebase';
import { CircularProgressbar } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import { useNavigate } from 'react-router-dom';

export default function CreatePost() {
  const [file, setFile] = useState(null);
  const [imageUploadProgress, setImageUploadProgress] = useState(null);
  const [imageUploadError, setImageUploadError] = useState(null);
  const [formData, setFormData] = useState({});
  const [publishError, setPublishError] = useState(null);
  const [patients, setPatients] = useState([]);
  const [result, setResult] = useState('');
  const navigate = useNavigate();

  const handleUploadImage = async () => {
    try {
      // Validate file
      if (!file) {
        setImageUploadError('Please select an image');
        return;
      }

      setImageUploadError(null);

      // Initialize Firebase storage
      const storage = getStorage(app);
      const fileName = new Date().getTime() + '-' + file.name;
      const storageRef = ref(storage, fileName);
      const formDataWithImage = new FormData();
      formDataWithImage.append('image', file);

      // Upload image
      const uploadTask = uploadBytesResumable(storageRef, file);
      uploadTask.on(
        'state_changed',
        (snapshot) => {
          // Track upload progress
          const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
          setImageUploadProgress(progress.toFixed(0));
        },
        (error) => {
          // Handle upload error
          setImageUploadError('Image upload failed');
          setImageUploadProgress(null);
        },
        () => {
          // Get download URL after successful upload
          getDownloadURL(uploadTask.snapshot.ref)
            .then((downloadURL) => {
              setImageUploadProgress(null);
              setFormData({ ...formData, image: downloadURL });
            })
            .catch((error) => {
              setImageUploadError('Failed to get image URL');
              setImageUploadProgress(null);
            });
        }
      );
    } catch (error) {
      setImageUploadError('Image upload failed');
      setImageUploadProgress(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const formDataWithImage = new FormData();
      formDataWithImage.append('image', file);

      for (const key in formData) {
        formDataWithImage.append(key, formData[key]);
      }

      const res = await fetch('http://127.0.0.1:8000/api/classify/', {
        method: 'POST',
        body: formDataWithImage,
      });
      const data = await res.json();
      if (!res.ok) {
        setPublishError(data.error);
        return;
      }

      setResult(data.prediction);
    } catch (error) {
      setPublishError('Something went wrong');
    }
  };
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/pateint/list/')
      .then((response) => response.json())
      .then((data) => setPatients(data))
      .catch((error) => console.error('Error fetching patients:', error));
  }, []);
  return (
    <div className='p-3 max-w-3xl mx-auto min-h-screen'>
      <h1 className='text-center text-3xl my-7 font-semibold'>Create a post</h1>
      <form className='flex flex-col gap-4' onSubmit={handleSubmit}>
        <div className='flex flex-col gap-4 sm:flex-row justify-between'>
        <TextInput
            type='text'
            placeholder='Title'
            required
            id='patient'
            className='flex-1'
            onChange={(e) => setFormData({ ...formData, patient: e.target.value })}
            disabled={patients.length > 0}
          />
       
            <Select
              onChange={(e) => setFormData({ ...formData, patient: e.target.value })}
            >
              <option value=''>Select a patient</option>
              {patients.map((patient) => (
                <option key={patient.id} value={patient.id}>
                  {patient.name}
                  
                </option>
              ))}
            </Select>
          
        </div>
        <div className='flex gap-4 items-center justify-between border-4 border-teal-500 border-dotted p-3'>
          <FileInput
            type='file'
            id='image'
            accept='image/*'
            onChange={(e) => setFile(e.target.files[0])}
          />
          <Button
            type='button'
            id='image'
            gradientDuoTone='purpleToBlue'
            size='sm'
            outline
            onClick={handleUploadImage}
            disabled={imageUploadProgress}
          >
            {imageUploadProgress ? (
              <div className='w-16 h-16'>
                <CircularProgressbar
                  value={imageUploadProgress}
                  text={`${imageUploadProgress || 0}%`}
                />
              </div>
            ) : (
              'Upload Image'
            )}
          </Button>
        </div>
        {imageUploadError && <Alert color='failure'>{imageUploadError}</Alert>}
        {formData.image && (
          <img
            src={formData.image}
            alt='upload'
            className='w-full h-72 object-cover'
          />
        )}
        <ReactQuill
        theme='snow'
        placeholder='Write something...'
        className='h-72 mb-12'
        required
        value={result} 
        onChange={(value) => {
          value.diseases
          value.image    
        }}
        />
          
        
        <Button type='submit' gradientDuoTone='purpleToPink'>
          Publish
        </Button>
        {publishError && (
          <Alert className='mt-5' color='failure'>
            {publishError}
          </Alert>
        )}
      </form>
    </div>
  );
}

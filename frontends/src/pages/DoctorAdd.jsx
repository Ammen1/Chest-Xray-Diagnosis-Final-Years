import React, { useState } from 'react';
import axios from 'axios';
import { Alert, Button, Label, Spinner, Select, TextInput } from "flowbite-react"; // Import Select component
import { GENDERS } from '../constants/constants';

const DoctorAdd = () => {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    age: '',
    gender: '',
    phone: '',
    email: '',
  });
  const [errors, setErrors] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); // Set loading state to true when form is submitted
    try {
      const response = await axios.post('http://127.0.0.1:8000/api/dockor/add/', formData);
      console.log(response.data); 
      alert('Doctor member added successfully!');
      setFormData({
        first_name: '',
        last_name: '',
        age: '',
        gender: '',
        phone: '',
        email: '',
      });
    } catch (error) {
      console.error('Error adding staff member:', error);
      alert('An error occurred. Please try again later.');
    } finally {
      setLoading(false); // Set loading state back to false after form submission is completed
    }
  };

  return (
    <div className="max-w-md mx-auto w-full h-full p-3 bg-gradient-to-br from-slate-50 to-white via-slate-100 mt-7 shadow-md rounded-md ">
      <h2 className="text-2xl font-semibold mb-6 text-center text-slate-900">Add Doctor </h2>
      <form onSubmit={handleSubmit} className='w-full'>
        <Label for="first_name">First Name</Label>
        <div className="mb-4 ">
          <TextInput
            type="text"
            name="first_name"
            value={formData.first_name}
            onChange={handleChange}
            placeholder="First Name"
            className=" w-full"
            required
          />
          {errors.first_name && <p className="text-red-500">{errors.first_name}</p>}
        </div>
        <Label for="last_name">Last Name</Label>
        <div className="mb-4">
          <TextInput
            type="text"
            name="last_name"
            value={formData.last_name}
            onChange={handleChange}
            placeholder="Last Name"
            className="input"
            required
          />
          {errors.last_name && <p className="text-red-500">{errors.last_name}</p>}
        </div>
        <Label for="age">Age</Label>
        <div className="mb-4">
          <TextInput
            type="text"
            name="age"
            value={formData.age}
            onChange={handleChange}
            placeholder="Age"
            className="input"
            pattern="\d*"
            title="Please enter a valid age"
          />
          {errors.age && <p className="text-red-500">{errors.age}</p>}
        </div>
        <Label for="gender">Gender</Label>
        <div className="mb-4 text-white">
          <Select
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            placeholder="Gender"
            className="input"
            required
          >
            <option value="">Select Gender</option>
            {GENDERS.map(gender => (
              <option key={gender[0]} value={gender[0]}>{gender[1]}</option>
            ))}
          </Select>
          {errors.gender && <p className="text-red-500">{errors.gender}</p>}
        </div>
        <Label for="phone">Phone</Label>
        <div className="mb-4">
          <TextInput
            type="tel"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="Phone"
            className="input"
            pattern="[0-9]*"
            title="Please enter a valid phone number"
          />
          {errors.phone && <p className="text-red-500">{errors.phone}</p>}
        </div>
        <Label for="email">Email</Label>
        <div className="mb-4">
          <TextInput
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Email"
            className="input"
            required
          />
          {errors.email && <p className="text-red-500">{errors.email}</p>}
        </div>
  
        <Button
        className=' ml-36 bg-gradient-to-l from-green-800 to-teal-800 via-cyan-600'
          // gradientDuoTone="purpleToPink"
          type="submit"
          disabled={loading}
        >
          {loading ? (
            <>
              <Spinner size="sm" />
              <span className="pl-3">Loading...</span>
            </>
          ) : (
            "Add Doctor"
          )}
        </Button>

      </form>
    </div>
  );
};

export default DoctorAdd;

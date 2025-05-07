const mongoose = require('mongoose');

const patientProfileSchema = new mongoose.Schema({
  firstName: {
    type: String,
    required: true
  },
  lastName: {
    type: String,
    required: true
  },
  dateOfBirth: {
    type: Date,
    required: true
  },
  phoneNumber: {
    type: String,
    required: true
  },
  emergencyContact: {
    type: String,
    required: true
  },
  medicalHistory: [{
    condition: String,
    diagnosedDate: Date,
    notes: String
  }],
  surgeries: [{
    type: { type: String }, // Changed from 'type' to 'type: { type: String }' to avoid naming conflict
    date: Date,
    surgeon: String,
    notes: String
  }],
  medications: [{
    name: String,
    dosage: String,
    frequency: String,
    startDate: Date,
    endDate: Date
  }],
  recoveryProgress: [{
    date: Date,
    notes: String,
    painLevel: Number,
    symptoms: [String]
  }]
});

const PatientProfile = mongoose.model('patient', patientProfileSchema);
module.exports = PatientProfile;
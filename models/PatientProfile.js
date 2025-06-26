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
  registeredBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Doctor', // Reference to the doctor who registered this patient
    required: true
  },
  userType: {
    type: String,
    default: 'patient'
  },
  role: {
    type: String,
    default: 'patient'
  },
  medicalHistory: [{
    condition: String,
    diagnosedDate: Date,
    notes: String
  }],
  surgeries: [{
    type: { type: String },
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
}, {
  timestamps: true
});

const PatientProfile = mongoose.model('patient', patientProfileSchema);
module.exports = PatientProfile;
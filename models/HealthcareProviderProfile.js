const mongoose = require('mongoose');

const healthcareProviderProfileSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true
  },
  specialization: {
    type: String,
    required: true
  },
  licenseNumber: {
    type: String,
    required: true,
    unique: true
  },
  yearsOfExperience: {
    type: Number,
    required: true
  },
  patients: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }],
  appointments: [{
    patient: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'User'
    },
    date: Date,
    notes: String,
    status: {
      type: String,
      enum: ['scheduled', 'completed', 'cancelled']
    }
  }],
  availability: [{
    day: String,
    startTime: String,
    endTime: String
  }]
});

const HealthcareProviderProfile = mongoose.model('healthcare-provider', healthcareProviderProfileSchema);
module.exports = HealthcareProviderProfile;
const mongoose = require('mongoose');

const hospitalProfileSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  name: { type: String, required: true },
  address: { type: String, required: true },
  contactNumber: { type: String, required: true },
  // Add other hospital-specific fields
}, { timestamps: true });

module.exports = mongoose.model('HospitalProfile', hospitalProfileSchema); 
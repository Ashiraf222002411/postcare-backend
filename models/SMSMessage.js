const mongoose = require('mongoose');

const smsMessageSchema = new mongoose.Schema({
  patientId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'patient',
    required: true
  },
  patientName: {
    type: String,
    required: true
  },
  phoneNumber: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  direction: {
    type: String,
    enum: ['inbound', 'outbound'],
    required: true,
    default: 'inbound'
  },
  status: {
    type: String,
    enum: ['unread', 'read', 'urgent', 'archived'],
    default: 'unread'
  },
  type: {
    type: String,
    enum: ['symptom', 'medication', 'general', 'emergency', 'checkup', 'response'],
    default: 'general'
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  processed: {
    type: Boolean,
    default: false
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {}
  }
}, {
  timestamps: true
});

// Index for efficient queries
smsMessageSchema.index({ patientId: 1, timestamp: -1 });
smsMessageSchema.index({ status: 1, timestamp: -1 });
smsMessageSchema.index({ type: 1, timestamp: -1 });

const SMSMessage = mongoose.model('SMSMessage', smsMessageSchema);
module.exports = SMSMessage;



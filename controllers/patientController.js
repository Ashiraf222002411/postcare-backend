// controllers/patientController.js (your existing file)
const Patient = require('../models/PatientProfile');
const SMSController = require('./smsController'); // NEW

const smsController = new SMSController(); // NEW

// Enhance your existing registerPatient function
const registerPatient = async (req, res) => {
    try {
        // Your existing patient creation code
        const patient = new Patient(req.body);
        const savedPatient = await patient.save();

        // NEW: Send welcome SMS via Python service
        if (savedPatient.phone) {
            const smsResult = await smsController.sendWelcomeSMS(savedPatient);
            console.log('Welcome SMS result:', smsResult);
        }

        res.status(201).json({
            success: true,
            patient: savedPatient
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
};

// NEW: Add follow-up function
const sendFollowUp = async (req, res) => {
    try {
        const patient = await Patient.findById(req.params.patientId);
        const { day } = req.body;

        const result = await smsController.sendFollowUp(
            req.params.patientId, 
            patient, 
            day
        );

        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
};

module.exports = {
    registerPatient,
    sendFollowUp, // NEW
    // ... your other existing functions
};
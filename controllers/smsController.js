// controllers/smsController.js
const axios = require('axios');

class SMSController {
    constructor() {
        this.pythonServiceUrl = process.env.PYTHON_AI_URL || 'http://localhost:5001';
    }

    async sendWelcomeSMS(patientData) {
        try {
            const response = await axios.post(`${this.pythonServiceUrl}/send_welcome`, {
                name: patientData.name,
                phone: patientData.phone,
                surgery_type: patientData.surgeryType
            });
            
            return response.data;
        } catch (error) {
            console.error('Welcome SMS failed:', error.message);
            return { success: false, error: error.message };
        }
    }

    async sendFollowUp(patientId, patientData, day) {
        try {
            const response = await axios.post(`${this.pythonServiceUrl}/send_followup`, {
                name: patientData.name,
                phone: patientData.phone,
                day: day
            });
            
            return response.data;
        } catch (error) {
            console.error('Follow-up SMS failed:', error.message);
            return { success: false, error: error.message };
        }
    }
}

module.exports = SMSController;
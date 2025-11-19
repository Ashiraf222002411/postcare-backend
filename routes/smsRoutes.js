const express = require('express');
const router = express.Router();
const smsController = require('../controllers/smsController');
const { protect: auth } = require('../middleware/auth');

// Get all messages with filtering
router.get('/messages', auth, smsController.getMessages);

// Get message statistics
router.get('/statistics', auth, smsController.getStatistics);

// Get messages for a specific patient
router.get('/messages/patient/:patientId', auth, smsController.getPatientMessages);

// Mark message as read
router.patch('/messages/:messageId/read', auth, smsController.markAsRead);

// Mark multiple messages as read
router.patch('/messages/read', auth, smsController.markMultipleAsRead);

// Send SMS message
router.post('/messages/send', auth, smsController.sendMessage);

// Store incoming message (webhook from Python service)
router.post('/messages/incoming', smsController.storeIncomingMessage);

// Legacy route
router.post('/trigger-checkup', auth, async (req, res) => {
    try {
        const axios = require('axios');
        const response = await axios.post(
            `${process.env.SMS_SERVICE_URL}/trigger-checkup`,
            req.body
        );
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;

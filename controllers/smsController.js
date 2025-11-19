// controllers/smsController.js
const axios = require('axios');
const SMSMessage = require('../models/SMSMessage');
const PatientProfile = require('../models/PatientProfile');

class SMSController {
    constructor() {
        this.pythonServiceUrl = process.env.PYTHON_AI_URL || 'http://localhost:5001';
        this.smsServiceUrl = process.env.SMS_SERVICE_URL || 'http://localhost:5000';
    }

    // Get all messages with filtering and pagination
    async getMessages(req, res) {
        try {
            const { 
                status, 
                type, 
                patientId, 
                search,
                page = 1, 
                limit = 50,
                sortBy = 'timestamp',
                sortOrder = 'desc'
            } = req.query;

            // Build query
            const query = {};
            
            if (status && status !== 'all') {
                query.status = status;
            }
            
            if (type && type !== 'all') {
                query.type = type;
            }
            
            if (patientId) {
                query.patientId = patientId;
            }
            
            if (search) {
                query.$or = [
                    { message: { $regex: search, $options: 'i' } },
                    { patientName: { $regex: search, $options: 'i' } }
                ];
            }

            // Calculate pagination
            const skip = (parseInt(page) - 1) * parseInt(limit);
            const sort = { [sortBy]: sortOrder === 'desc' ? -1 : 1 };

            // Get messages
            const messages = await SMSMessage.find(query)
                .sort(sort)
                .skip(skip)
                .limit(parseInt(limit))
                .populate('patientId', 'firstName lastName phoneNumber')
                .lean();

            // Get total count for pagination
            const total = await SMSMessage.countDocuments(query);

            // Format messages for frontend
            const formattedMessages = messages.map(msg => ({
                id: msg._id.toString(),
                patientId: msg.patientId?._id?.toString() || msg.patientId?.toString() || 'unknown',
                patientName: msg.patientName || 
                    (msg.patientId?.firstName && msg.patientId?.lastName 
                        ? `${msg.patientId.firstName} ${msg.patientId.lastName}`
                        : 'Unknown Patient'),
                message: msg.message,
                timestamp: this.formatTimestamp(msg.timestamp),
                status: msg.status,
                type: msg.type,
                direction: msg.direction,
                phoneNumber: msg.phoneNumber || msg.patientId?.phoneNumber
            }));

            res.json({
                success: true,
                messages: formattedMessages,
                pagination: {
                    page: parseInt(page),
                    limit: parseInt(limit),
                    total,
                    pages: Math.ceil(total / parseInt(limit))
                }
            });
        } catch (error) {
            console.error('Error fetching messages:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Get message statistics
    async getStatistics(req, res) {
        try {
            const [
                totalMessages,
                unreadCount,
                urgentCount,
                todayCount,
                recentMessages
            ] = await Promise.all([
                SMSMessage.countDocuments(),
                SMSMessage.countDocuments({ status: 'unread' }),
                SMSMessage.countDocuments({ status: 'urgent' }),
                SMSMessage.countDocuments({
                    timestamp: { $gte: new Date(new Date().setHours(0, 0, 0, 0)) }
                }),
                SMSMessage.find()
                    .sort({ timestamp: -1 })
                    .limit(5)
                    .populate('patientId', 'firstName lastName')
                    .lean()
            ]);

            // Count by type
            const typeCounts = await SMSMessage.aggregate([
                {
                    $group: {
                        _id: '$type',
                        count: { $sum: 1 }
                    }
                }
            ]);

            const typeStats = {};
            typeCounts.forEach(item => {
                typeStats[item._id] = item.count;
            });

            res.json({
                success: true,
                statistics: {
                    totalMessages,
                    unreadCount,
                    urgentCount,
                    todayCount,
                    typeStats,
                    recentMessages: recentMessages.map(msg => ({
                        id: msg._id.toString(),
                        patientName: msg.patientName || 
                            (msg.patientId?.firstName && msg.patientId?.lastName 
                                ? `${msg.patientId.firstName} ${msg.patientId.lastName}`
                                : 'Unknown'),
                        message: msg.message.substring(0, 100),
                        timestamp: this.formatTimestamp(msg.timestamp),
                        status: msg.status
                    }))
                }
            });
        } catch (error) {
            console.error('Error fetching statistics:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Mark message as read
    async markAsRead(req, res) {
        try {
            const { messageId } = req.params;
            const { status } = req.body;

            const message = await SMSMessage.findByIdAndUpdate(
                messageId,
                { 
                    status: status || 'read',
                    updatedAt: new Date()
                },
                { new: true }
            );

            if (!message) {
                return res.status(404).json({
                    success: false,
                    error: 'Message not found'
                });
            }

            res.json({
                success: true,
                message: 'Message updated successfully',
                data: message
            });
        } catch (error) {
            console.error('Error updating message:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Mark multiple messages as read
    async markMultipleAsRead(req, res) {
        try {
            const { messageIds, status } = req.body;

            if (!Array.isArray(messageIds) || messageIds.length === 0) {
                return res.status(400).json({
                    success: false,
                    error: 'messageIds must be a non-empty array'
                });
            }

            const result = await SMSMessage.updateMany(
                { _id: { $in: messageIds } },
                { 
                    status: status || 'read',
                    updatedAt: new Date()
                }
            );

            res.json({
                success: true,
                message: `${result.modifiedCount} messages updated successfully`,
                modifiedCount: result.modifiedCount
            });
        } catch (error) {
            console.error('Error updating messages:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Send SMS message
    async sendMessage(req, res) {
        try {
            const { patientId, phoneNumber, message, type = 'general' } = req.body;

            if (!phoneNumber || !message) {
                return res.status(400).json({
                    success: false,
                    error: 'phoneNumber and message are required'
                });
            }

            // Get patient info if patientId provided
            let patientName = 'Unknown Patient';
            if (patientId) {
                const patient = await PatientProfile.findById(patientId);
                if (patient) {
                    patientName = `${patient.firstName} ${patient.lastName}`;
                }
            }

            // Send SMS via Python service
            let sendResult = { success: false };
            try {
                const response = await axios.post(`${this.pythonServiceUrl}/send_sms`, {
                    phone: phoneNumber,
                    message: message
                });
                sendResult = response.data;
            } catch (error) {
                console.error('Error sending SMS via Python service:', error.message);
                // Continue to save message even if sending fails
            }

            // Save outbound message to database
            const smsMessage = new SMSMessage({
                patientId: patientId || null,
                patientName,
                phoneNumber,
                message,
                direction: 'outbound',
                status: 'read',
                type,
                processed: true
            });

            await smsMessage.save();

            res.json({
                success: true,
                message: 'SMS sent successfully',
                data: {
                    id: smsMessage._id.toString(),
                    patientId: smsMessage.patientId?.toString(),
                    patientName: smsMessage.patientName,
                    message: smsMessage.message,
                    timestamp: this.formatTimestamp(smsMessage.timestamp),
                    status: smsMessage.status,
                    type: smsMessage.type,
                    sendResult
                }
            });
        } catch (error) {
            console.error('Error sending message:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Store incoming message (called by Python service webhook)
    async storeIncomingMessage(req, res) {
        try {
            const { phoneNumber, message, patientId, patientName, type = 'general', metadata = {} } = req.body;

            if (!phoneNumber || !message) {
                return res.status(400).json({
                    success: false,
                    error: 'phoneNumber and message are required'
                });
            }

            // Try to find patient by phone number if patientId not provided
            let finalPatientId = patientId;
            let finalPatientName = patientName;

            if (!finalPatientId || !finalPatientName) {
                const patient = await PatientProfile.findOne({ phoneNumber });
                if (patient) {
                    finalPatientId = patient._id;
                    finalPatientName = `${patient.firstName} ${patient.lastName}`;
                }
            }

            // Determine status based on message content
            let status = 'unread';
            let messageType = type;
            
            // Check for urgent keywords
            const urgentKeywords = ['emergency', 'urgent', 'pain', 'help', 'severe', 'critical'];
            const lowerMessage = message.toLowerCase();
            if (urgentKeywords.some(keyword => lowerMessage.includes(keyword))) {
                status = 'urgent';
            }

            // Auto-detect message type
            if (lowerMessage.includes('medication') || lowerMessage.includes('med')) {
                messageType = 'medication';
            } else if (lowerMessage.includes('symptom') || lowerMessage.includes('pain') || lowerMessage.includes('fever')) {
                messageType = 'symptom';
            } else if (lowerMessage.includes('emergency') || lowerMessage.includes('help')) {
                messageType = 'emergency';
            }

            // Save incoming message
            const smsMessage = new SMSMessage({
                patientId: finalPatientId,
                patientName: finalPatientName || 'Unknown Patient',
                phoneNumber,
                message,
                direction: 'inbound',
                status,
                type: messageType,
                processed: false,
                metadata
            });

            await smsMessage.save();

            res.json({
                success: true,
                message: 'Incoming message stored successfully',
                data: {
                    id: smsMessage._id.toString(),
                    patientId: smsMessage.patientId?.toString(),
                    patientName: smsMessage.patientName,
                    message: smsMessage.message,
                    timestamp: this.formatTimestamp(smsMessage.timestamp),
                    status: smsMessage.status,
                    type: smsMessage.type
                }
            });
        } catch (error) {
            console.error('Error storing incoming message:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Get messages for a specific patient
    async getPatientMessages(req, res) {
        try {
            const { patientId } = req.params;
            const { limit = 50 } = req.query;

            const messages = await SMSMessage.find({ patientId })
                .sort({ timestamp: -1 })
                .limit(parseInt(limit))
                .populate('patientId', 'firstName lastName phoneNumber')
                .lean();

            const formattedMessages = messages.map(msg => ({
                id: msg._id.toString(),
                patientId: msg.patientId?._id?.toString() || msg.patientId?.toString(),
                patientName: msg.patientName || 
                    (msg.patientId?.firstName && msg.patientId?.lastName 
                        ? `${msg.patientId.firstName} ${msg.patientId.lastName}`
                        : 'Unknown'),
                message: msg.message,
                timestamp: this.formatTimestamp(msg.timestamp),
                status: msg.status,
                type: msg.type,
                direction: msg.direction
            }));

            res.json({
                success: true,
                messages: formattedMessages
            });
        } catch (error) {
            console.error('Error fetching patient messages:', error);
            res.status(500).json({
                success: false,
                error: error.message
            });
        }
    }

    // Helper method to format timestamp
    formatTimestamp(timestamp) {
        if (!timestamp) return 'Unknown';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} ${diffMins === 1 ? 'min' : 'mins'} ago`;
        if (diffHours < 24) return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
        if (diffDays < 7) return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
        
        return date.toLocaleDateString();
    }

    // Legacy methods
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

module.exports = new SMSController();
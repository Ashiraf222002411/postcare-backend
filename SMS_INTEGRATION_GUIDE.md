# SMS Monitoring Integration Guide

This document explains how the frontend SMS monitoring system integrates with the backend.

## Overview

The integration allows the frontend dashboard to:
- View all SMS messages from patients
- Filter messages by status (unread, urgent, read) and type (symptom, medication, general, emergency)
- Search messages
- Mark messages as read
- Send SMS messages to patients
- View statistics about messages

## Backend Components

### 1. SMS Message Model (`models/SMSMessage.js`)
MongoDB schema for storing SMS messages with the following fields:
- `patientId`: Reference to patient
- `patientName`: Patient's name
- `phoneNumber`: Phone number
- `message`: Message content
- `direction`: 'inbound' or 'outbound'
- `status`: 'unread', 'read', 'urgent', 'archived'
- `type`: 'symptom', 'medication', 'general', 'emergency', 'checkup', 'response'
- `timestamp`: When the message was sent/received

### 2. SMS Controller (`controllers/smsController.js`)
Provides the following endpoints:
- `getMessages()` - Get all messages with filtering and pagination
- `getStatistics()` - Get message statistics
- `markAsRead()` - Mark a single message as read
- `markMultipleAsRead()` - Mark multiple messages as read
- `sendMessage()` - Send an SMS to a patient
- `storeIncomingMessage()` - Store incoming messages (called by Python service)
- `getPatientMessages()` - Get messages for a specific patient

### 3. SMS Routes (`routes/smsRoutes.js`)
API endpoints:
- `GET /api/sms/messages` - Get messages (with query params: status, type, search, page, limit)
- `GET /api/sms/statistics` - Get statistics
- `GET /api/sms/messages/patient/:patientId` - Get patient messages
- `PATCH /api/sms/messages/:messageId/read` - Mark message as read
- `PATCH /api/sms/messages/read` - Mark multiple messages as read
- `POST /api/sms/messages/send` - Send SMS
- `POST /api/sms/messages/incoming` - Store incoming message (webhook)

### 4. Python SMS Service Integration
The Python SMS service (`sms-service/app/enhanced_sms_service.py`) has been updated to automatically store incoming messages in the Node.js backend database when messages are received via the webhook.

## Frontend Components

### API Service (`services/api.ts`)
The `smsAPI` object provides methods to interact with the backend:
- `getMessages(params)` - Fetch messages with filtering
- `getStatistics()` - Get statistics
- `markAsRead(messageId, status)` - Mark message as read
- `markMultipleAsRead(messageIds, status)` - Mark multiple as read
- `sendMessage(messageData)` - Send SMS
- `getPatientMessages(patientId, limit)` - Get patient messages

## Usage Example

### In Your Dashboard Component

```typescript
import { smsAPI } from '@/services/api';
import { useState, useEffect } from 'react';

export default function DoctorDashboard() {
  const [messages, setMessages] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  // Fetch messages
  useEffect(() => {
    const fetchMessages = async () => {
      setLoading(true);
      try {
        const params = {
          status: activeTab !== 'all' ? activeTab : undefined,
          search: searchQuery || undefined,
          page: 1,
          limit: 50
        };
        
        const response = await smsAPI.getMessages(params);
        setMessages(response.messages || []);
      } catch (error) {
        console.error('Error fetching messages:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMessages();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchMessages, 30000);
    return () => clearInterval(interval);
  }, [activeTab, searchQuery]);

  // Fetch statistics
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await smsAPI.getStatistics();
        setStatistics(response.statistics);
      } catch (error) {
        console.error('Error fetching statistics:', error);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  // Mark message as read
  const handleMarkAsRead = async (messageId) => {
    try {
      await smsAPI.markAsRead(messageId);
      // Refresh messages
      const response = await smsAPI.getMessages({ status: activeTab !== 'all' ? activeTab : undefined });
      setMessages(response.messages || []);
    } catch (error) {
      console.error('Error marking message as read:', error);
    }
  };

  // Send message
  const handleSendMessage = async (phoneNumber, message, patientId) => {
    try {
      await smsAPI.sendMessage({
        phoneNumber,
        message,
        patientId,
        type: 'general'
      });
      // Refresh messages
      const response = await smsAPI.getMessages();
      setMessages(response.messages || []);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  return (
    <div>
      {/* Your dashboard UI */}
      {loading && <div>Loading...</div>}
      {messages.map(msg => (
        <div key={msg.id}>
          <p>{msg.patientName}: {msg.message}</p>
          <span>{msg.timestamp}</span>
          {msg.status === 'unread' && (
            <button onClick={() => handleMarkAsRead(msg.id)}>
              Mark as Read
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
```

## Environment Variables

For the Python SMS service to store messages in the backend, set:
```bash
NODE_BACKEND_URL=http://localhost:3000/api
```

Or update `sms-service/config.py`:
```python
NODE_BACKEND_URL = os.getenv('NODE_BACKEND_URL', 'http://localhost:3000/api')
```

## Message Status Flow

1. **Incoming Message**: Patient sends SMS → Python service receives it → Automatically stored in MongoDB via `/api/sms/messages/incoming` endpoint
2. **Display**: Frontend fetches messages from `/api/sms/messages`
3. **Mark as Read**: Frontend calls `/api/sms/messages/:messageId/read` to mark message as read
4. **Send Message**: Frontend calls `/api/sms/messages/send` → Backend sends via Python service → Message stored in database

## Testing

1. Start the Node.js backend:
   ```bash
   npm start
   ```

2. Start the Python SMS service:
   ```bash
   cd sms-service/app
   python enhanced_sms_service.py
   ```

3. Test the endpoints:
   ```bash
   # Get messages
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:3000/api/sms/messages
   
   # Get statistics
   curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:3000/api/sms/statistics
   ```

## Notes

- All SMS endpoints require authentication (Bearer token)
- The `/api/sms/messages/incoming` endpoint does NOT require authentication (it's called by Python service)
- Messages are automatically categorized based on content (urgent keywords, medication mentions, etc.)
- Patient information is automatically linked when phone numbers match registered patients


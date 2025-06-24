require('dotenv').config();
const express = require('express');
const cors = require('cors');

// Import with error handling
let connectDB;
try {
  connectDB = require('./config/db');
} catch (error) {
  console.log('⚠️ Database config not found, skipping DB connection');
  connectDB = () => console.log('Database connection skipped');
}

let authRoutes;
try {
  authRoutes = require('./routes/authRoutes');
} catch (error) {
  console.log('⚠️ Auth routes not found, using placeholder');
  authRoutes = require('express').Router();
  authRoutes.get('/health', (req, res) => res.json({ message: 'Auth placeholder' }));
}

process.env.PYTHON_AI_URL = process.env.PYTHON_AI_URL || 'http://localhost:5001';

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Connect to MongoDB
connectDB();

// Routes
app.use('/api/auth', authRoutes);

app.use(cors({
  origin: [
    ' https://postcareplus-39391.web.app', 
    'https://postcareplus.com'     
  ],
  credentials: true
}));
// Basic route
app.get('/', (req, res) => {
  res.json({ 
    success: true,
    message: 'Welcome to PostCare API',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

app.get('/health', (req, res) => {
  res.json({
    success: true,
    status: 'healthy',
    services: {
      api: 'running',
      database: process.env.MONGODB_URI ? 'configured' : 'not configured',
      python_ai: process.env.PYTHON_AI_URL
    }
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({
    success: false,
    message: err.message,
    stack: process.env.NODE_ENV === 'development' ? err.stack : undefined
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: `Route ${req.originalUrl} not found`
  });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 PostCare Backend running on port ${PORT}`);
  console.log(`📍 Health check: http://localhost:${PORT}/health`);
});
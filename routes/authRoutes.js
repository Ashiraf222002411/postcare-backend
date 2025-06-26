const express = require('express');
const router = express.Router();
const { 
  register, 
  login, 
  getProfile, 
  updateProfile,
  registerPatient // Add this import
} = require('../controllers/authController');
const { validateRegistration, validatePatientRegistration, validateLogin, validate } = require('../middleware/validate');
const { protect, restrictTo } = require('../middleware/auth'); // Add restrictTo for role-based access

// Debug route
router.get('/test', (req, res) => {
  res.json({ message: 'Auth routes are working' });
});

// Debug route for testing authentication
router.get('/debug-auth', protect, (req, res) => {
  res.json({ 
    message: 'Authentication successful',
    user: {
      id: req.user._id,
      email: req.user.email,
      userType: req.user.userType,
      role: req.user.role
    }
  });
});

// Debug route to check server configuration (be careful with this in production)
router.get('/debug-config', (req, res) => {
  res.json({
    hasJwtSecret: !!process.env.JWT_SECRET,
    jwtSecretLength: process.env.JWT_SECRET ? process.env.JWT_SECRET.length : 0,
    nodeEnv: process.env.NODE_ENV,
    mongoConfigured: !!process.env.MONGODB_URI
  });
});

// Public routes
router.post('/register', validateRegistration, validate, register);
router.post('/login', validateLogin, validate, login);

// Protected routes
router.get('/profile', protect, getProfile);
router.put('/profile', protect, updateProfile);

// Doctor-only routes
router.post('/register-patient', protect, restrictTo('doctor'), validatePatientRegistration, validate, registerPatient);

module.exports = router;
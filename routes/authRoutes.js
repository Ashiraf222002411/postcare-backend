const express = require('express');
const router = express.Router();
const { 
  register, 
  login, 
  getProfile, 
  updateProfile,
  registerPatient // Add this import
} = require('../controllers/authController');
const { validateRegistration, validateLogin, validate } = require('../middleware/validate');
const { protect, restrictTo } = require('../middleware/auth'); // Add restrictTo for role-based access

// Debug route
router.get('/test', (req, res) => {
  res.json({ message: 'Auth routes are working' });
});

// Public routes
router.post('/register', validateRegistration, validate, register);
router.post('/login', validateLogin, validate, login);

// Protected routes
router.get('/profile', protect, getProfile);
router.put('/profile', protect, updateProfile);

// Doctor-only routes
router.post('/register-patient', protect, restrictTo('doctor'), validateRegistration, validate, registerPatient);

module.exports = router;
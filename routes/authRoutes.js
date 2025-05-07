const express = require('express');
const router = express.Router();
const { 
  register, 
  login, 
  getProfile, 
  updateProfile 
} = require('../controllers/authController');
const { validateRegistration, validateLogin, validate } = require('../middleware/validate');
const { protect } = require('../middleware/auth'); // Add this import

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

module.exports = router;
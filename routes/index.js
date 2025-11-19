const express = require('express');
const router = express.Router();
const authRoutes = require('./authRoutes');
const smsRoutes = require('./smsRoutes');

router.use('/auth', authRoutes);
router.use('/sms', smsRoutes);

module.exports = router;
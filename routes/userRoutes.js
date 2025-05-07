const express = require('express');
const router = express.Router();

// Test route
router.get('/test', (req, res) => {
    res.json({ message: 'User route is working' });
});

// Export the router
module.exports = router;
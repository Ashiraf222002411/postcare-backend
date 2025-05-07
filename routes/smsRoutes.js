const express = require('express');
const router = express.Router();
const axios = require('axios');

router.post('/trigger-checkup', async (req, res) => {
    try {
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

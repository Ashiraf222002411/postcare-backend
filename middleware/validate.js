const { validationResult, check } = require('express-validator');

const validateRegistration = [
  check('email')
    .normalizeEmail()
    .isEmail().withMessage('Please provide a valid email'),
  check('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long')
    .matches(/[A-Z]/).withMessage('Password must contain at least one uppercase letter')
    .matches(/[0-9]/).withMessage('Password must contain at least one number'),
  check('userType')
    .trim()
    .toLowerCase()
    .isIn(['patient', 'healthcare-provider', 'hospital'])
    .withMessage('Invalid user type'),
];

const validatePatientRegistration = [
  check('email')
    .normalizeEmail()
    .isEmail().withMessage('Please provide a valid email'),
  check('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long')
    .matches(/[A-Z]/).withMessage('Password must contain at least one uppercase letter')
    .matches(/[0-9]/).withMessage('Password must contain at least one number'),
  // Note: userType is not validated here as it's automatically set to 'patient' in the controller
];

const validateLogin = [
  check('email')
    .normalizeEmail()
    .isEmail().withMessage('Please provide a valid email'),
  check('password').exists().withMessage('Password is required'),
];

const validate = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ 
      success: false,
      message: 'Validation failed',
      errors: errors.array().map(err => err.msg)
    });
  }
  next();
};

module.exports = {
  validateRegistration,
  validatePatientRegistration,
  validateLogin,
  validate,
};
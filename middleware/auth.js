const jwt = require('jsonwebtoken');
const { User } = require('../models');

const protect = async (req, res, next) => {
  try {
    let token;

    console.log('Auth middleware - Authorization header:', req.headers.authorization);

    if (req.headers.authorization?.startsWith('Bearer')) {
      token = req.headers.authorization.split(' ')[1];
      console.log('Auth middleware - Token extracted:', token ? 'Token present' : 'No token');

      if (!process.env.JWT_SECRET) {
        console.error('JWT_SECRET environment variable is not set');
        return res.status(500).json({ message: 'Server configuration error' });
      }

      console.log('Auth middleware - JWT_SECRET available:', !!process.env.JWT_SECRET);
      
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      console.log('Auth middleware - Token decoded successfully:', decoded);
      
      const user = await User.findById(decoded.id).select('-password');
      console.log('Auth middleware - User found:', user ? 'Yes' : 'No');
      
      if (!user) {
        console.error('User not found for token:', decoded.id);
        return res.status(401).json({ message: 'Not authorized, user not found' });
      }

      req.user = user;
      console.log('Auth middleware - Success, user attached to request');
      next();
    } else {
      console.error('No authorization header or invalid format');
      res.status(401).json({ message: 'Not authorized, no token' });
    }
  } catch (error) {
    console.error('Auth middleware error:', error);
    
    if (error.name === 'JsonWebTokenError') {
      console.error('JWT Error - Invalid token format or signature');
      return res.status(401).json({ message: 'Not authorized, invalid token' });
    }
    if (error.name === 'TokenExpiredError') {
      console.error('JWT Error - Token has expired');
      return res.status(401).json({ message: 'Not authorized, token expired' });
    }
    
    res.status(401).json({ message: 'Not authorized, token failed' });
  }
};

const restrictTo = (...roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ 
        success: false,
        message: 'Not authenticated' 
      });
    }

    // Check if user's role or userType matches any of the allowed roles
    const userRole = req.user.role || req.user.userType;
    const allowedRoles = roles.includes('doctor') ? [...roles, 'healthcare-provider'] : roles;
    
    if (!allowedRoles.includes(userRole)) {
      return res.status(403).json({ 
        success: false,
        message: `Access denied. This endpoint requires one of the following roles: ${roles.join(', ')}. Your role: ${userRole}` 
      });
    }
    
    next();
  };
};

module.exports = { protect, restrictTo };
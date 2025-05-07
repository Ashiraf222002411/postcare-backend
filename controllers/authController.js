const jwt = require('jsonwebtoken');
const { User, PatientProfile, HealthcareProviderProfile, HospitalProfile } = require('../models');

// Helper function to generate JWT
const generateToken = (userId) => {
  return jwt.sign({ id: userId }, process.env.JWT_SECRET, {
    expiresIn: '30d',
  });
};
//  register controller
const register = async (req, res) => {
  console.log('Registration request received');
  console.log('Request body:', req.body);
  
  try {
    const { email, password, userType, ...profileData } = req.body;

    // Check if user already exists
    const userExists = await User.findOne({ email });
    if (userExists) {
      return res.status(400).json({ message: 'User already exists' });
    }

    // Create appropriate profile based on user type
    let profile;
    try {
      switch (userType) {
        case 'patient':
          profile = await PatientProfile.create(profileData);
          break;
        case 'healthcare-provider':
          profile = await HealthcareProviderProfile.create(profileData);
          break;
        case 'hospital':
          profile = await HospitalProfile.create(profileData);
          break;
        default:
          return res.status(400).json({ message: 'Invalid user type' });
      }
    } catch (profileError) {
      console.error('Profile creation error:', profileError);
      return res.status(400).json({
        message: 'Error creating profile',
        error: profileError.message,
        validationErrors: profileError.errors
      });
    }

    // Create user with reference to profile
    const userData = {
      email,
      password,
      userType,
      role: userType, // Explicitly set role to match userType
      profile: profile._id
    };

    const user = await User.create(userData);

    if (user) {
      res.status(201).json({
        success: true,
        data: {
          _id: user._id,
          email: user.email,
          userType: user.userType,
          profile: profile,
          token: generateToken(user._id)
        }
      });
    } else {
      // If user creation failed, delete the profile
      await profile.deleteOne();
      return res.status(400).json({ message: 'Invalid user data' });
    }

  } catch (error) {
    console.error('Registration error:', error);
    res.status(500).json({
      success: false,
      message: 'Error registering user',
      error: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
};
// Login controller
const login = async (req, res) => {
  try {
    const { email, password } = req.body;

    // Find user and populate profile
    const user = await User.findOne({ email }).populate('profile');
    
    if (user && (await user.matchPassword(password))) {
      res.json({
        _id: user._id,
        email: user.email,
        userType: user.userType,
        profile: user.profile,
        token: generateToken(user._id)
      });
    } else {
      res.status(401).json({ message: 'Invalid email or password' });
    }
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Error logging in', error: error.message });
  }
};

// Get user profile
const getProfile = async (req, res) => {
  try {
    // TODO: Implement get profile logic
    res.status(200).json({ message: 'Get profile endpoint' });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};

// Update profile
const updateProfile = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).populate('profile');
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Update profile based on user type
    const { ...profileData } = req.body;
    let updatedProfile;

    switch (user.userType) {
      case 'patient':
        updatedProfile = await PatientProfile.findByIdAndUpdate(
          user.profile._id,
          profileData,
          { new: true }
        );
        break;
      case 'healthcare-provider':
        updatedProfile = await HealthcareProviderProfile.findByIdAndUpdate(
          user.profile._id,
          profileData,
          { new: true }
        );
        break;
      case 'hospital':
        updatedProfile = await HospitalProfile.findByIdAndUpdate(
          user.profile._id,
          profileData,
          { new: true }
        );
        break;
    }

    res.json({
      _id: user._id,
      email: user.email,
      userType: user.userType,
      profile: updatedProfile
    });
  } catch (error) {
    console.error('Profile update error:', error);
    res.status(500).json({ message: 'Error updating profile', error: error.message });
  }
};

module.exports = {
  register,
  login,
  getProfile,
  updateProfile
};
from termux_gateway import TermuxSMSGateway
import numpy as np
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import joblib
import os
from datetime import datetime
import pickle
import requests
from config import Config
import logging

class IntelligentPostCareSystem:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        os.makedirs(model_dir, exist_ok=True)
        self.symptom_classifier = self._load_or_create_classifier()
        self.recovery_predictor = self._load_or_create_predictor()
        self.patient_data = self._load_patient_data()
        self.active_sessions = {}
        self.alert_thresholds = self._load_alert_thresholds()
        self.sms_gateway = TermuxSMSGateway(
            Config.TERMUX_GATEWAY_URL,
            Config.TERMUX_API_KEY
        )
        
        if self.sms_gateway.health_check():
            logging.info("✅ Termux gateway connected")
        else:
            logging.warning("⚠️ Termux gateway offline!")

    def _load_or_create_classifier(self):
        try:
            return joblib.load(os.path.join(self.model_dir, 'symptom_classifier.pkl'))
        except:
            classifier = RandomForestRegressor(n_estimators=100)
            initial_data = np.array([[1,1,1,1], [2,2,2,2], [3,3,3,3]])
            initial_labels = np.array([0, 1, 2])
            classifier.fit(initial_data, initial_labels)
            joblib.dump(classifier, os.path.join(self.model_dir, 'symptom_classifier.pkl'))
            return classifier

    def _load_or_create_predictor(self):
        try:
            return tf.keras.models.load_model(os.path.join(self.model_dir, 'recovery_predictor.h5'))
        except:
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(32, activation='relu', input_shape=(7,)),
                tf.keras.layers.Dense(16, activation='relu'),
                tf.keras.layers.Dense(8, activation='relu'),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
            model.save(os.path.join(self.model_dir, 'recovery_predictor.h5'))
            return model

    def analyze_patient_condition(self, patient_data):
        """Analyze patient condition using the ML models"""
        features = np.array([[
            patient_data['wound'],
            patient_data['pain'],
            patient_data['temperature'],
            patient_data['mobility']
        ]])
        
        severity = self.symptom_classifier.predict(features)[0]
        
        extended_features = np.array([[
            patient_data['wound'],
            patient_data['pain'],
            patient_data['temperature'],
            patient_data['mobility'],
            patient_data.get('appetite', 0),
            patient_data.get('sleep', 0),
            patient_data.get('medication_adherence', 0)
        ]])
        
        recovery_prediction = self.recovery_predictor.predict(extended_features)[0][0]
        
        return {
            'severity': float(severity),
            'recovery_prediction': float(recovery_prediction),
            'alerts': self._generate_alerts(patient_data, severity)
        }

    def _load_patient_data(self):
        try:
            with open(os.path.join(self.model_dir, 'patient_history.pkl'), 'rb') as f:
                return pickle.load(f)
        except:
            return {}

    def _load_alert_thresholds(self):
        return {
            'pain_threshold': self._calculate_dynamic_threshold('pain'),
            'fever_threshold': self._calculate_dynamic_threshold('temperature'),
            'wound_threshold': self._calculate_dynamic_threshold('wound')
        }

    def _calculate_dynamic_threshold(self, metric):
        if not self.patient_data:
            return 0.7
        values = [data[metric] for data in self.patient_data.values() if metric in data]
        return np.mean(values) + np.std(values) if values else 0.7

    def _generate_alerts(self, patient_data, severity):
        alerts = []
        if severity > self.alert_thresholds['pain_threshold']:
            alerts.append("HIGH_PAIN")
        if patient_data.get('temperature', 0) > self.alert_thresholds['fever_threshold']:
            alerts.append("FEVER")
        if patient_data.get('wound', 0) > self.alert_thresholds['wound_threshold']:
            alerts.append("WOUND_CONCERN")
        return alerts

     def send_sms(self, phone_number, message):
        """Send SMS using Termux gateway"""
        return self.sms_gateway.send_sms(phone_number, message)
   
   
    # ... [Rest of the IntelligentPostCareSystem class implementation]

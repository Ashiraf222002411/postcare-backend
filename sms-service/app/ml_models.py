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
        """Send SMS using SmsMobile API with improved error handling"""
        try:
            logging.info(f"Attempting to send SMS to {phone_number}")
            
            payload = {
                "recipient": phone_number,
                "sender_id": Config.SMS_SENDER_ID,
                "message": message,
                "api_key": Config.SMS_API_KEY
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            response = requests.post(
                Config.SMS_API_URL,
                json=payload,
                headers=headers,
                timeout=30  # Add timeout
            )

            logging.info(f"SMS API Response: {response.status_code} - {response.text}")

            if response.status_code == 200:
                logging.info(f"Successfully sent SMS to {phone_number}")
                return True
            else:
                logging.error(f"Failed to send SMS. Status: {response.status_code}, Response: {response.text}")
                return False

        except requests.Timeout:
            logging.error(f"Timeout while sending SMS to {phone_number}")
            return False
        except requests.ConnectionError:
            logging.error(f"Connection error while sending SMS to {phone_number}")
            return False
        except Exception as e:
            logging.error(f"Error sending SMS: {str(e)}")
            return False

    # ... [Rest of the IntelligentPostCareSystem class implementation]

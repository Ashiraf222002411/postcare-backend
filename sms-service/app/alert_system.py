# sms-service/app/alert_system.py
"""
Alert System for PostCare SMS Service
Manages alerts and notifications to Community Health Workers (CHW) and Doctors
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class AlertLevel(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

class AlertType(Enum):
    """Types of alerts"""
    ROUTINE_FOLLOWUP = "routine_followup"
    HEALTH_CONCERN = "health_concern"
    EMERGENCY = "emergency"
    MISSED_CHECKUP = "missed_checkup"
    MEDICATION_ISSUE = "medication_issue"

class AlertSystem:
    """Manages healthcare provider alerts and notifications"""
    
    def __init__(self, sms_service, ai_advisor, translations):
        self.sms_service = sms_service
        self.ai_advisor = ai_advisor
        self.translations = translations
        
        # Healthcare provider contacts
        self.healthcare_providers = {
            'primary_doctor': {
                'name': 'Dr. Muganga Mukuru',
                'phone': '+250785379885',  # Replace with actual number
                'specialties': ['surgery', 'general_medicine'],
                'emergency_contact': True
            },
            'emergency_doctor': {
                'name': 'Dr. Byihutirwa',
                'phone': '+250788123456',  # Replace with actual number
                'specialties': ['emergency'],
                'emergency_contact': True
            },
            'cwh_coordinator': {
                'name': 'CHW Mukuru',
                'phone': '+250787654321',  # Replace with actual number
                'role': 'community_health_worker',
                'region': 'main'
            }
        }
        
        # CHW network (Community Health Workers)
        self.chw_network = {
            'sector_1': {
                'name': 'Uwimana CHW',
                'phone': '+250783111111',
                'region': 'sector_1',
                'patients_assigned': []
            },
            'sector_2': {
                'name': 'Mukamana CHW', 
                'phone': '+250783222222',
                'region': 'sector_2',
                'patients_assigned': []
            },
            'sector_3': {
                'name': 'Nkurunziza CHW',
                'phone': '+250783333333',
                'region': 'sector_3', 
                'patients_assigned': []
            }
        }
        
        self.alert_history = []
        print("🚨 Alert System initialized")
    
    def process_patient_alert(self, patient_info: Dict, analysis: Dict, conversation_context: Dict = None) -> Dict:
        """Process patient condition and send appropriate alerts"""
        severity = analysis.get('severity', 0)
        alerts = analysis.get('alerts', [])
        recovery_score = analysis.get('recovery_prediction', 0.5)
        
        # Determine alert level
        alert_level = self._determine_alert_level(severity, alerts, recovery_score)
        
        # Determine alert type
        alert_type = self._determine_alert_type(analysis, conversation_context)
        
        # Send alerts based on severity
        results = {}
        
        if alert_level == AlertLevel.EMERGENCY:
            results.update(self._send_emergency_alerts(patient_info, analysis, conversation_context))
        
        elif alert_level == AlertLevel.HIGH:
            results.update(self._send_high_priority_alerts(patient_info, analysis))
        
        elif alert_level == AlertLevel.MEDIUM:
            results.update(self._send_medium_priority_alerts(patient_info, analysis))
        
        else:
            # Low priority - routine reporting to CHW only
            results.update(self._send_routine_report(patient_info, analysis))
        
        # Log alert
        self._log_alert(patient_info, alert_level, alert_type, results)
        
        return {
            'alert_level': alert_level.value,
            'alert_type': alert_type.value,
            'notifications_sent': results
        }
    
    def send_emergency_alert(self, patient_info: Dict, emergency_details: str, analysis: Dict = None) -> Dict:
        """Send immediate emergency alert"""
        print(f"🚨 EMERGENCY ALERT for {patient_info.get('name', 'Unknown patient')}")
        
        if not analysis:
            analysis = {
                'severity': 10,
                'alerts': ['EMERGENCY'],
                'recovery_prediction': 0.1
            }
        
        # Generate emergency messages
        doctor_message = self.ai_advisor.generate_doctor_alert(patient_info, analysis, emergency_details)
        cwh_message = self.ai_advisor.generate_cwh_report(patient_info, {'summary': f'EMERGENCY: {emergency_details}'}, analysis)
        
        results = {}
        
        # Alert emergency doctor immediately
        emergency_doctor = self.healthcare_providers['emergency_doctor']
        result = self.sms_service.send_sms(emergency_doctor['phone'], doctor_message)
        results['emergency_doctor'] = {
            'provider': emergency_doctor['name'],
            'phone': emergency_doctor['phone'],
            'sent': result.get('success', False),
            'priority': 'EMERGENCY'
        }
        
        # Alert primary doctor
        primary_doctor = self.healthcare_providers['primary_doctor']
        result = self.sms_service.send_sms(primary_doctor['phone'], doctor_message)
        results['primary_doctor'] = {
            'provider': primary_doctor['name'],
            'phone': primary_doctor['phone'],
            'sent': result.get('success', False),
            'priority': 'EMERGENCY'
        }
        
        # Alert CHW coordinator
        cwh_coordinator = self.healthcare_providers['cwh_coordinator']
        result = self.sms_service.send_sms(cwh_coordinator['phone'], cwh_message)
        results['cwh_coordinator'] = {
            'provider': cwh_coordinator['name'],
            'phone': cwh_coordinator['phone'],
            'sent': result.get('success', False),
            'priority': 'EMERGENCY'
        }
        
        return results
    
    def _send_emergency_alerts(self, patient_info: Dict, analysis: Dict, conversation_context: Dict) -> Dict:
        """Send emergency level alerts"""
        emergency_details = conversation_context.get('emergency_message', 'Severe symptoms detected')
        return self.send_emergency_alert(patient_info, emergency_details, analysis)
    
    def _send_high_priority_alerts(self, patient_info: Dict, analysis: Dict) -> Dict:
        """Send high priority alerts"""
        results = {}
        
        # Generate messages
        doctor_message = self.ai_advisor.generate_doctor_alert(patient_info, analysis)
        cwh_message = self.ai_advisor.generate_cwh_report(patient_info, {'summary': 'High priority health concern'}, analysis)
        
        # Alert primary doctor
        primary_doctor = self.healthcare_providers['primary_doctor']
        result = self.sms_service.send_sms(primary_doctor['phone'], doctor_message)
        results['primary_doctor'] = {
            'provider': primary_doctor['name'],
            'phone': primary_doctor['phone'],
            'sent': result.get('success', False),
            'priority': 'HIGH'
        }
        
        # Alert CHW coordinator
        cwh_coordinator = self.healthcare_providers['cwh_coordinator']
        result = self.sms_service.send_sms(cwh_coordinator['phone'], cwh_message)
        results['cwh_coordinator'] = {
            'provider': cwh_coordinator['name'],
            'phone': cwh_coordinator['phone'],
            'sent': result.get('success', False),
            'priority': 'HIGH'
        }
        
        # Alert regional CHW if assigned
        regional_chw = self._get_regional_chw(patient_info)
        if regional_chw:
            result = self.sms_service.send_sms(regional_chw['phone'], cwh_message)
            results['regional_chw'] = {
                'provider': regional_chw['name'],
                'phone': regional_chw['phone'],
                'sent': result.get('success', False),
                'priority': 'HIGH'
            }
        
        return results
    
    def _send_medium_priority_alerts(self, patient_info: Dict, analysis: Dict) -> Dict:
        """Send medium priority alerts"""
        results = {}
        
        # Generate CHW report
        cwh_message = self.ai_advisor.generate_cwh_report(patient_info, {'summary': 'Medium priority health update'}, analysis)
        
        # Alert CHW coordinator
        cwh_coordinator = self.healthcare_providers['cwh_coordinator']
        result = self.sms_service.send_sms(cwh_coordinator['phone'], cwh_message)
        results['cwh_coordinator'] = {
            'provider': cwh_coordinator['name'],
            'phone': cwh_coordinator['phone'],
            'sent': result.get('success', False),
            'priority': 'MEDIUM'
        }
        
        # Alert regional CHW
        regional_chw = self._get_regional_chw(patient_info)
        if regional_chw:
            result = self.sms_service.send_sms(regional_chw['phone'], cwh_message)
            results['regional_chw'] = {
                'provider': regional_chw['name'],
                'phone': regional_chw['phone'],
                'sent': result.get('success', False),
                'priority': 'MEDIUM'
            }
        
        return results
    
    def _send_routine_report(self, patient_info: Dict, analysis: Dict) -> Dict:
        """Send routine report to CHW"""
        results = {}
        
        # Generate routine CHW report
        cwh_message = self.ai_advisor.generate_cwh_report(patient_info, {'summary': 'Routine health check-in'}, analysis)
        
        # Send to regional CHW only
        regional_chw = self._get_regional_chw(patient_info)
        if regional_chw:
            result = self.sms_service.send_sms(regional_chw['phone'], cwh_message)
            results['regional_chw'] = {
                'provider': regional_chw['name'],
                'phone': regional_chw['phone'],
                'sent': result.get('success', False),
                'priority': 'LOW'
            }
        
        return results
    
    def _determine_alert_level(self, severity: float, alerts: List[str], recovery_score: float) -> AlertLevel:
        """Determine alert level based on analysis"""
        # Emergency conditions
        if (severity >= 9 or 
            ('HIGH_PAIN' in alerts and 'FEVER' in alerts) or
            ('POOR_WOUND_HEALING' in alerts and severity >= 7) or
            recovery_score < 0.2):
            return AlertLevel.EMERGENCY
        
        # High priority conditions
        elif (severity >= 7 or 
              len(alerts) >= 3 or
              'HIGH_PAIN' in alerts or
              recovery_score < 0.4):
            return AlertLevel.HIGH
        
        # Medium priority conditions
        elif (severity >= 4 or 
              len(alerts) >= 2 or
              recovery_score < 0.6):
            return AlertLevel.MEDIUM
        
        # Low priority - routine
        else:
            return AlertLevel.LOW
    
    def _determine_alert_type(self, analysis: Dict, conversation_context: Dict = None) -> AlertType:
        """Determine type of alert"""
        if conversation_context and conversation_context.get('emergency_message'):
            return AlertType.EMERGENCY
        
        severity = analysis.get('severity', 0)
        alerts = analysis.get('alerts', [])
        
        if severity >= 8:
            return AlertType.EMERGENCY
        elif severity >= 6 or len(alerts) >= 2:
            return AlertType.HEALTH_CONCERN
        else:
            return AlertType.ROUTINE_FOLLOWUP
    
    def _get_regional_chw(self, patient_info: Dict) -> Optional[Dict]:
        """Get regional CHW based on patient location/assignment"""
        # This would normally be based on patient's location or assignment
        # For now, use a simple round-robin or default assignment
        patient_region = patient_info.get('region', 'sector_1')
        
        if patient_region in self.chw_network:
            return self.chw_network[patient_region]
        else:
            # Default to first available CHW
            return list(self.chw_network.values())[0] if self.chw_network else None
    
    def _log_alert(self, patient_info: Dict, alert_level: AlertLevel, alert_type: AlertType, results: Dict):
        """Log alert for tracking"""
        alert_record = {
            'timestamp': datetime.now().isoformat(),
            'patient_id': patient_info.get('id'),
            'patient_name': patient_info.get('name'),
            'patient_phone': patient_info.get('phone'),
            'alert_level': alert_level.value,
            'alert_type': alert_type.value,
            'notifications_sent': results,
            'total_notifications': len(results)
        }
        
        self.alert_history.append(alert_record)
        
        # Keep only last 1000 alerts to prevent memory issues
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        print(f"📝 Alert logged: {alert_level.value} for {patient_info.get('name')} ({len(results)} notifications)")
    
    def send_daily_summary(self, target_provider: str = 'cwh_coordinator') -> Dict:
        """Send daily summary to healthcare providers"""
        today = datetime.now().date()
        
        # Get today's alerts
        today_alerts = [
            alert for alert in self.alert_history 
            if datetime.fromisoformat(alert['timestamp']).date() == today
        ]
        
        # Count by severity
        emergency_count = len([a for a in today_alerts if a['alert_level'] == 'emergency'])
        high_count = len([a for a in today_alerts if a['alert_level'] == 'high'])
        medium_count = len([a for a in today_alerts if a['alert_level'] == 'medium'])
        low_count = len([a for a in today_alerts if a['alert_level'] == 'low'])
        
        # Generate summary message
        summary_message = f"""📊 RAPORO Y'UMUNSI - PostCare+
📅 {today.strftime('%Y-%m-%d')}

📈 IBIMENYETSO BYA LEO:
🚨 Byihutirwa: {emergency_count}
⚠️ Bikomeye: {high_count}
📋 Bisanzwe: {medium_count}
✅ Byoroshye: {low_count}

📊 IGITERANYO: {len(today_alerts)} abakuraguzi

Murakoze gukora PostCare+!
---
Sisitemu ya PostCare SMS"""
        
        # Send to specified provider
        provider = self.healthcare_providers.get(target_provider)
        if provider:
            result = self.sms_service.send_sms(provider['phone'], summary_message)
            return {
                'summary_sent': result.get('success', False),
                'provider': provider['name'],
                'phone': provider['phone'],
                'alerts_count': len(today_alerts)
            }
        
        return {'error': 'Provider not found'}
    
    def add_healthcare_provider(self, provider_id: str, provider_info: Dict):
        """Add new healthcare provider"""
        self.healthcare_providers[provider_id] = provider_info
        print(f"➕ Added healthcare provider: {provider_info.get('name', provider_id)}")
    
    def add_chw(self, chw_id: str, chw_info: Dict):
        """Add new Community Health Worker"""
        self.chw_network[chw_id] = chw_info
        print(f"➕ Added CHW: {chw_info.get('name', chw_id)}")
    
    def get_alert_statistics(self) -> Dict:
        """Get alert system statistics"""
        total_alerts = len(self.alert_history)
        
        if total_alerts == 0:
            return {
                'total_alerts': 0,
                'alert_levels': {},
                'alert_types': {},
                'success_rate': 0
            }
        
        # Count by level
        level_counts = {}
        type_counts = {}
        successful_notifications = 0
        total_notifications = 0
        
        for alert in self.alert_history:
            level = alert['alert_level']
            alert_type = alert['alert_type']
            
            level_counts[level] = level_counts.get(level, 0) + 1
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
            
            # Count successful notifications
            notifications = alert.get('notifications_sent', {})
            for notification in notifications.values():
                total_notifications += 1
                if notification.get('sent', False):
                    successful_notifications += 1
        
        success_rate = (successful_notifications / total_notifications * 100) if total_notifications > 0 else 0
        
        return {
            'total_alerts': total_alerts,
            'alert_levels': level_counts,
            'alert_types': type_counts,
            'success_rate': round(success_rate, 2),
            'total_providers': len(self.healthcare_providers),
            'total_chws': len(self.chw_network)
        }


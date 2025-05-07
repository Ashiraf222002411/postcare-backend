from datetime import datetime, timedelta

def should_send_checkup(patient, current_time):
    """Determine if patient should receive checkup based on their condition"""
    last_checkup = datetime.fromisoformat(patient.get('last_checkup', '2000-01-01'))
    high_risk = patient.get('risk_level', 'LOW') == 'HIGH'
    
    if high_risk and (current_time - last_checkup) > timedelta(hours=12):
        return True
    elif (current_time - last_checkup) > timedelta(hours=24):
        return True
    return False

def generate_checkup_message(patient):
    """Generate personalized checkup message based on patient history"""
    # Add implementation
    pass

# PostCare Enhanced SMS Service - Kinyarwanda Support

## Overview

The PostCare Enhanced SMS Service now includes comprehensive Kinyarwanda language support with an intelligent conversation flow system. The system provides SMS-based healthcare monitoring with AI-powered advice and automated reporting to Community Health Workers (CHWs) and doctors.

## 🌟 New Features

### 1. Kinyarwanda Language Support
- **Full medical terminology translation** - Pain, wound healing, fever, mobility terms
- **Cultural adaptation** - Healthcare advice adapted for Rwandan context
- **Bilingual support** - Patients can use English or Kinyarwanda

### 2. SMS Menu System (USSD-like Flow)
- **Interactive menu navigation** via SMS
- **Step-by-step health data collection**
- **Free conversation mode** after structured data entry
- **Emergency detection and handling**

### 3. AI-Powered Medical Advisor
- **Contextual advice** in Kinyarwanda based on patient symptoms
- **Emergency detection** from patient messages
- **Recovery tracking** and progress monitoring
- **Personalized recommendations**

### 4. Automated Alert System
- **Community Health Worker notifications** for routine follow-ups
- **Doctor alerts** for concerning symptoms
- **Emergency alerts** for critical situations
- **Daily summary reports** for healthcare providers

## 🔄 Conversation Flow

### Initial Contact
1. **Welcome SMS** - Patient receives welcome message in Kinyarwanda
2. **Main Menu** - Patient gets interactive menu options:
   ```
   Muraho [Name]! Hitamo icyo ushaka:
   1. Gutanga amakuru y'ubuzima
   2. Kubaza ikibazo mu buzima  
   3. Gusaba ubufasha bw'ihutirwa
   4. Kureba uko mukira
   5. Kuvugana n'umuganga
   0. Kuva
   ```

### Health Data Collection (Option 1)
1. **Pain Level** (1-10) - "Ni gute ububabare bwawe ubu?"
2. **Wound Healing** (1-10) - "Ni gute ikibago cyawe gikira?"
3. **Temperature** (°C) - "Ni angahe umushyuha wawe?"
4. **Mobility** (1-10) - "Ni gute ubushobozi bwawe bwo kugenda?"

### Free Conversation Mode
After data collection, patients can:
- **Ask any health questions** in Kinyarwanda
- **Report concerns** in natural language
- **Receive AI-generated advice** tailored to their condition
- **Get emergency help** if keywords detected

### Emergency Handling
- **Automatic detection** of emergency keywords
- **Immediate response** with emergency instructions
- **Healthcare provider alerts** sent instantly
- **Escalation protocols** activated

## 🏥 Healthcare Provider Integration

### Community Health Workers (CHWs)
- **Routine reports** for patient follow-ups
- **Regional assignment** based on patient location
- **Progress summaries** in Kinyarwanda
- **Action recommendations** (visit patient, call doctor, etc.)

### Doctors
- **Urgent alerts** for concerning symptoms
- **Emergency notifications** for critical situations
- **Patient history** and conversation context
- **Clinical recommendations** based on AI analysis

## 📱 API Endpoints

### Patient Interaction
- `POST /send_welcome` - Send welcome SMS in Kinyarwanda
- `POST /start_conversation` - Start interactive conversation
- `POST /webhook/sms` - Handle incoming SMS with enhanced processing

### Conversation Management
- `GET /conversation_status/<phone>` - Check conversation state
- `POST /send_menu` - Send main menu to patient

### Healthcare Provider Tools
- `POST /emergency_alert` - Send emergency alerts
- `POST /send_daily_summary` - Send daily summary to providers
- `GET /alert_statistics` - Get alert system statistics

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Start the SMS service
python app/enhanced_sms_service.py

# In another terminal, run tests
python test_kinyarwanda_system.py
```

The test suite covers:
- System health checks
- Kinyarwanda SMS sending
- Conversation flow simulation
- Emergency alert testing
- Statistics and reporting

## 🌍 Sample Conversations

### Health Data Collection
**System:** Muraho Uwimana! Tuzagukusanya amakuru y'ubuzima bwawe. Ubanza, twubaze ku bubabare: Ni gute ububabare bwawe ubu? (1-10)

**Patient:** 6

**System:** Murakoze! Ububabare bwo hagati (6). Ubwo, gukira kw'ikibago cyawe: Ni gute ikibago cyawe gikira? (1-10)

**Patient:** 8

**System:** Ikiriho! Ikibago gikira neza (8/10). Ni angahe umushyuha wawe?

**Patient:** 37.2

**System:** Umushyuha usanzwe (37.2°C). Ni gute ubushobozi bwawe bwo kugenda? (1-10)

**Patient:** 7

### AI-Generated Advice
**System:** Murakoze cyane Uwimana! Ubwoba bwawe ni 78%. Ikiriho! Ukiri neza cyane! 🎉

Komeza gufata imiti yawe nk'uko byasabwe, rya ibiryo byiza, uruhuke bihagije. Komeza neza Uwimana! Tuzongera tugusuzuma.

Ubu ushobora kutwandikira ikibazo cyose cyangwa icyo ubabaje ku buzima bwawe.

### Emergency Detection
**Patient:** Mfite ububabare bukabije cyane, sinshobora kugenda!

**System:** 🚨 BYIHUTIRWA Uwimana! Twabonye ko muvuze ikibazo gikomeye. Kora iki VUBA:
1. 📞 Hamagara: 912 (Ihutirwa)
2. 🏥 Jya mu bitaro byihutirwa
3. 📱 Hamagara umuganga wawe

Tugiye kumenyesha umuganga wawe UBUNYANGAMUGAYO!

## 🔧 Configuration

### Healthcare Providers
Edit `app/alert_system.py` to configure your healthcare providers:

```python
self.healthcare_providers = {
    'primary_doctor': {
        'name': 'Dr. Your Doctor Name',
        'phone': '+250XXXXXXXXX',
        'specialties': ['surgery', 'general_medicine'],
        'emergency_contact': True
    },
    # ... other providers
}
```

### CHW Network
Configure Community Health Workers by region:

```python
self.chw_network = {
    'your_sector': {
        'name': 'CHW Name',
        'phone': '+250XXXXXXXXX',
        'region': 'your_sector',
        'patients_assigned': []
    }
}
```

### Language Settings
Patients can be configured for different languages:

```python
# In patient registration
patient_info = {
    'language': 'rw',  # 'rw' for Kinyarwanda, 'en' for English
    # ... other patient data
}
```

## 🚨 Emergency Keywords

The system automatically detects emergency situations from these Kinyarwanda keywords:

- `byihutirwa` (urgent)
- `kubabara cyane` (severe pain)
- `sinshobora` (cannot)
- `ndarwaye cyane` (very sick)
- `umuriro mukomeye` (high fever)
- `ntabwo nshobora kugenda` (cannot walk)
- `ikibazo gikomeye` (serious problem)
- `mfite ubwoba` (I'm scared)
- `nsaba ubufasha` (need help)

## 📊 Monitoring and Analytics

### Alert Statistics
- Track total alerts sent
- Monitor success rates
- Analyze alert levels (Emergency, High, Medium, Low)
- Provider response tracking

### Conversation Analytics
- Active conversation count
- State distribution
- Response times
- Patient engagement metrics

## 🔐 Security and Privacy

- **HIPAA-compliant** data handling
- **Encrypted** patient data storage
- **Secure** SMS transmission
- **Access controls** for healthcare providers
- **Audit logging** for all interactions

## 📝 Customization

### Adding New Medical Terms
Edit `app/kinyarwanda_translations.py` to add new medical terminology or advice templates.

### Custom Alert Logic
Modify `app/alert_system.py` to customize when and how alerts are sent.

### AI Advice Customization
Update `app/ai_advisor.py` to add new advice patterns or medical knowledge.

## 🆘 Support

For technical support or feature requests:
1. Check system logs in `postcare_sms.log`
2. Run health checks via `/health` endpoint
3. Use test suite to verify functionality
4. Contact system administrator

## 📋 Todo and Roadmap

- [ ] Voice message support in Kinyarwanda
- [ ] Integration with electronic health records
- [ ] Medication reminder system
- [ ] Family member notifications
- [ ] Multi-language voice synthesis
- [ ] Advanced analytics dashboard
- [ ] Telemedicine integration

---

**Note:** This system is designed to supplement, not replace, professional medical care. Patients should always consult healthcare providers for serious medical concerns.



# sms-service/app/ai_advisor.py
"""
AI Medical Advisor for PostCare SMS Service
Provides contextual medical advice in Kinyarwanda based on patient data and conversation
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

class KinyarwandaAIAdvisor:
    """AI advisor that provides medical advice in Kinyarwanda"""
    
    def __init__(self, translations, simple_analyzer=None):
        self.translations = translations
        self.simple_analyzer = simple_analyzer
        
        # Medical knowledge base in Kinyarwanda
        self.medical_knowledge = {
            'pain_management': {
                'mild': [
                    "Fata imiti yo kuraguza ububabare nk'uko muganga yagusabye.",
                    "Komeza uruhuke kandi udakore ibikorwa bikomeye.",
                    "Shyira ibintu bikonjesha ku karere k'ububabare iminota 15-20."
                ],
                'moderate': [
                    "Fata imiti yo kuraguza ububabare nk'uko byasabwe.",
                    "Niba ububabare bukomeje iminsi 2-3, hamagara muganga.",
                    "Ruhuka cyane kandi wirinde ibikorwa bikomeye."
                ],
                'severe': [
                    "HAMAGARA MUGANGA VUBA! Ububabare bukomeye bushobora kwerekanye ikibazo gikomeye.",
                    "Fata imiti yawe yo kuraguza ububabare.",
                    "Wirinde kurya ibintu bikarishye cyangwa umuti utemewe."
                ]
            },
            
            'wound_care': {
                'poor': [
                    "Ikibago cyawe gisaba uwitabire ukomeye.",
                    "Sukura ikibago n'amazi meza buhoro buhoro.",
                    "Koresha imiti ya antibiotike nk'uko byasabwe.",
                    "Niba ikibago gikira cyane cyangwa kirusha amaraso, hamagara muganga."
                ],
                'improving': [
                    "Ikibago cyawe gikira neza. Komeza ukwitwaririka.",
                    "Sukura ikibago buri munsi n'amazi meza.",
                    "Komeza gufata imiti ya antibiotike kugeza igihe cyose."
                ],
                'good': [
                    "Ikibago cyawe gikira neza cyane!",
                    "Komeza gukwitwaririka ikibago kandi usukure neza.",
                    "Wirinde gushira amazi make ku kibago."
                ]
            },
            
            'fever_management': {
                'mild_fever': [
                    "Nywa amazi menshi kugira ngo utazimiye.",
                    "Ruhuka kandi wisigasire mu mazu.",
                    "Fata imiti yo kugabanya umuriro nk'uko byasabwe."
                ],
                'high_fever': [
                    "Umuriro mukomeye usaba uwitabire bw'umuganga.",
                    "Nywa amazi menshi cyane kandi uruhuke.",
                    "Niba umuriro uri hejuru ya 38.5°C cyangwa ukomeje iminsi myinshi, hamagara muganga.",
                    "Koresha igikoma cyangwa amazi yo gukonjesha umubiri."
                ]
            },
            
            'mobility_advice': {
                'limited': [
                    "Tangira guhagaza umubiri buhoro buhoro.",
                    "Kora siporo idahari nk'urugero rwo kugenda gahoro.",
                    "Saba ubufasha mu kugenda niba bibaye ngombwa.",
                    "Wirinde gukora ibikorwa bikomeye cyane."
                ],
                'improving': [
                    "Komeza gukora siporo idahari buri munsi.",
                    "Ongera ubushobozi bwawe bwo kugenda buhoro buhoro.",
                    "Wirinde kuruhura umubiri cyane."
                ],
                'good': [
                    "Ikiriho! Ubushobozi bwawe bwo kugenda ni bwiza.",
                    "Komeza gukora siporo isanzwe kandi ongera ubusanzwe.",
                    "Wirinde ibikorwa bikomeye kugeza muganga akubwira."
                ]
            },
            
            'general_recovery': [
                "Rya ibiryo byiza birimo vitamini (inyama, ibinyobinya, imbuto).",
                "Nywa amazi menshi buri munsi (byibuze 8 ibikombe).",
                "Ruhuka bihagije (amasaha 7-8 mu ijoro).",
                "Fata imiti yawe nk'uko byasabwe ugasiga.",
                "Hoberana akarere k'ikibago gatukura buri munsi.",
                "Wirinde gunywa inzoga cyangwa gukoresha itabi.",
                "Jya gusuzuma umuganga nk'uko byagenwe."
            ],
            
            'emergency_indicators': [
                "ububabare bukabije budasubirwaho",
                "umuriro uri hejuru ya 39°C",
                "ikibago gisukuye cyane cyangwa gitukura",
                "ubushobozi buke bwo guhumeka",
                "ubushobozi buke bwo gukingura cyangwa gutujurwa",
                "amaraso menshi",
                "ubwoba bukomeye"
            ]
        }
        
        print("🤖 Kinyarwanda AI Advisor initialized")
    
    def generate_response(self, patient_message: str, conversation_context: Dict) -> str:
        """Generate contextual response to patient message"""
        patient_info = conversation_context.get('patient_info', {})
        patient_name = patient_info.get('name', 'Patient')
        
        # Check for emergency
        if self.translations.detect_emergency(patient_message):
            return self._generate_emergency_response(patient_message, patient_name)
        
        # Check if it's a question
        if self.translations.detect_question(patient_message):
            return self._generate_question_response(patient_message, patient_name, conversation_context)
        
        # General conversational response
        return self._generate_general_response(patient_message, patient_name, conversation_context)
    
    def generate_health_analysis_advice(self, patient_data: Dict, analysis: Dict, patient_name: str) -> str:
        """Generate advice based on health data analysis"""
        advice_parts = []
        
        # Add personalized greeting
        recovery_score = analysis.get('recovery_prediction', 0.5)
        greeting = f"Muraho {patient_name}! Tubonye amakuru yawe y'ubuzima."
        
        if recovery_score > 0.8:
            greeting += " Wowe! Ukiri neza cyane! 🎉"
        elif recovery_score > 0.6:
            greeting += " Ukiri neza! 👍"
        elif recovery_score > 0.4:
            greeting += " Uko mukira ni neza."
        else:
            greeting += " Dufite amakuru asaba uwitabire."
        
        advice_parts.append(greeting)
        
        # Analyze each component
        pain_level = patient_data.get('pain', 5)
        wound_level = patient_data.get('wound', 5)
        temperature = patient_data.get('temperature', 37.0)
        mobility = patient_data.get('mobility', 5)
        
        # Pain advice
        if pain_level >= 8:
            advice_parts.extend(self.medical_knowledge['pain_management']['severe'])
        elif pain_level >= 5:
            advice_parts.extend(self.medical_knowledge['pain_management']['moderate'])
        elif pain_level > 0:
            advice_parts.extend(self.medical_knowledge['pain_management']['mild'])
        
        # Wound advice
        if wound_level <= 3:
            advice_parts.extend(self.medical_knowledge['wound_care']['poor'])
        elif wound_level <= 6:
            advice_parts.extend(self.medical_knowledge['wound_care']['improving'])
        else:
            advice_parts.extend(self.medical_knowledge['wound_care']['good'])
        
        # Temperature advice
        if temperature >= 38.5:
            advice_parts.extend(self.medical_knowledge['fever_management']['high_fever'])
        elif temperature >= 37.5:
            advice_parts.extend(self.medical_knowledge['fever_management']['mild_fever'])
        
        # Mobility advice
        if mobility <= 3:
            advice_parts.extend(self.medical_knowledge['mobility_advice']['limited'])
        elif mobility <= 6:
            advice_parts.extend(self.medical_knowledge['mobility_advice']['improving'])
        else:
            advice_parts.extend(self.medical_knowledge['mobility_advice']['good'])
        
        # Add general recovery advice
        advice_parts.append("\n📋 Inama rusange z'ubuzima:")
        advice_parts.extend(self.medical_knowledge['general_recovery'][:3])  # Limit to 3 for SMS
        
        # Add follow-up
        if analysis.get('needs_attention', False):
            advice_parts.append(f"\n⚠️ {patient_name}, hamagara umuganga niba ibimenyetso bisibangana cyangwa bikomeje.")
        else:
            advice_parts.append(f"\n✅ Komeza neza {patient_name}! Tuzongera tugusuzuma.")
        
        return " ".join(advice_parts)
    
    def _generate_emergency_response(self, message: str, patient_name: str) -> str:
        """Generate emergency response"""
        return f"""🚨 BYIHUTIRWA {patient_name}!

Twabonye ko muvuze ikibazo gikomeye. Kora iki VUBA:

1. 📞 Hamagara: 912 (Ihutirwa)
2. 🏥 Jya mu bitaro byihutirwa
3. 📱 Hamagara umuganga wawe

Tugiye kumenyesha umuganga wawe UBUNYANGAMUGAYO!

Niba ukenera ubufasha bwandi, twandikire 'UBUFASHA'.

Turagushimira ko watubwiye vuba!"""
    
    def _generate_question_response(self, message: str, patient_name: str, context: Dict) -> str:
        """Generate response to patient questions"""
        message_lower = message.lower()
        
        # Common medical questions in Kinyarwanda
        if any(word in message_lower for word in ['ububabare', 'ndababara', 'bubabare']):
            return f"""Muraho {patient_name}! Ku bubabare:

🔸 Niba ububabare ni buke (1-4): Fata imiti yo kuraguza ububabare, ruhuka.
🔸 Niba ari bwo hagati (5-7): Fata imiti yawe, ruhuka cyane, hamagara muganga niba bukomeje.
🔸 Niba bukomeye (8-10): Hamagara muganga VUBA!

Komeza kutubwira uko mumereye. Hari ikindi ushaka kubaza?"""
        
        elif any(word in message_lower for word in ['ikibago', 'gukira', 'kibago']):
            return f"""Muraho {patient_name}! Ku kwitwaririka ikibago:

🔸 Sukura ikibago n'amazi meza buri munsi
🔸 Koresha imiti ya antibiotike nk'uko byasabwe
🔸 Hoberana akarere gatukura
🔸 Niba ikibago gikira cyane, gitukura, cyangwa girusha amaraso - hamagara muganga

Ikibago cyawe gikira gute ubu? Hari ikindi ubaza?"""
        
        elif any(word in message_lower for word in ['umuriro', 'umushyuha', 'gushyuha']):
            return f"""Muraho {patient_name}! Ku muriro:

🔸 Nywa amazi menshi
🔸 Ruhuka wisigasire
🔸 Fata imiti yo kugabanya umuriro
🔸 Niba umuriro uri hejuru ya 38.5°C cyangwa ukomeje - hamagara muganga

Umushyuha wawe ubu ni angahe? Turabaza ko duhura!"""
        
        elif any(word in message_lower for word in ['imiti', 'muti', 'kubana imiti']):
            return f"""Muraho {patient_name}! Ku miti:

🔸 Fata imiti yawe nk'uko muganga yagusabye GUSA
🔸 Ntugasige imiti hagati y'inzira
🔸 Niba wibagirwa, nyamira igihe gikurikira - ntugongere
🔸 Niba ufite ibibazo by'imiti, hamagara muganga

Waba ukeka ko imiti igufasha? Hari ikindi ubaza?"""
        
        else:
            # General response for other questions
            return f"""Muraho {patient_name}! Murakoze kubaza.

Ku bibazo bya rusange by'ubuzima nyuma y'ubuganga:
🔸 Rya ibiryo byiza (inyama, ibinyobinya, imbuto)
🔸 Nywa amazi menshi
🔸 Ruhuka bihagije
🔸 Kora siporo idahari
🔸 Jya gusuzuma muganga nk'uko byagenwe

Niba hari ikibazo runaka, tumbwire arambuye. Turafasha!"""
    
    def _generate_general_response(self, message: str, patient_name: str, context: Dict) -> str:
        """Generate general conversational response"""
        message_lower = message.lower()
        
        # Positive responses
        if any(word in message_lower for word in ['murakoze', 'ni byiza', 'nkiri neza', 'ndakira']):
            return f"""Ikiriho {patient_name}! Tunishimye cyane kubona ko mukira neza.

Komeza ukurikiza inama z'umuganga:
🔸 Fata imiti yawe nk'uko byasabwe
🔸 Ruhuka bihagije
🔸 Hoberana ikibago neza

Tuzongera tugusuzuma vuba. Niba hari ikindi, tubwire!"""
        
        # Negative/concerning responses
        elif any(word in message_lower for word in ['ndarwaye', 'ndasiba', 'mfite ibibazo', 'ntabwo nkira']):
            return f"""Tubabajije {patient_name}. Tubwire arambuye icyo kibabaje:

🔸 Ni ububabare bukomeye?
🔸 Ikibago gikira nabi?
🔸 Umuriro ukomeye?
🔸 Ikindi kintu?

Tuzagusubiza vuba kandi tugafasha. Niba ari byihutirwa, hamagara 912!"""
        
        # General supportive response
        else:
            return f"""Muraho {patient_name}! Twumvise ubutumwa bwawe.

📋 Wibutse kwisuzuma:
• Ububabare: Bukomeye/bwiza?
• Ikibago: Gikira neza/nabi?
• Umushyuha: Usanzwe/mukomeye?
• Kugenda: Bishoboka/bigoye?

Tubwire uko ubona kandi tuzagufasha. Turagufasha buri gihe!"""
    
    def generate_cwh_report(self, patient_info: Dict, conversation_summary: Dict, analysis: Dict) -> str:
        """Generate report for Community Health Worker in Kinyarwanda"""
        patient_name = patient_info.get('name', 'Unknown')
        surgery_type = patient_info.get('surgery_type', 'Unknown')
        phone = patient_info.get('phone', 'Unknown')
        
        severity = analysis.get('severity', 0)
        alerts = analysis.get('alerts', [])
        recovery_score = analysis.get('recovery_prediction', 0)
        
        # Translate alerts to Kinyarwanda
        alert_translations = {
            'HIGH_PAIN': 'Ububabare bukomeye',
            'POOR_WOUND_HEALING': 'Ikibago gikira nabi', 
            'FEVER': 'Umuriro',
            'LOW_MOBILITY': 'Ubushobozi buke bwo kugenda'
        }
        
        kinyarwanda_alerts = [alert_translations.get(alert, alert) for alert in alerts]
        
        report = f"""📋 RAPORO Y'UMURWAYI - PostCare+

👤 Umurwayi: {patient_name}
📱 Telefoni: {phone}
🏥 Ubuganga: {surgery_type}
📅 Igihe: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📊 UBUZIMA:
• Ukomeretse: {severity}/10
• Ubwoba bwo gukira: {recovery_score:.0%}
• Ibimenyetso: {', '.join(kinyarwanda_alerts) if kinyarwanda_alerts else 'Nta kimenyetso'}

⚠️ ICYIFUZO:
{self._get_cwh_recommendation(severity, alerts)}

📝 ICYO URUGERO RWAKOZWE:
{conversation_summary.get('summary', 'Ikiganiro cy\'ubuzima')}

---
PostCare+ SMS System"""
        
        return report
    
    def generate_doctor_alert(self, patient_info: Dict, analysis: Dict, emergency_details: str = None) -> str:
        """Generate urgent alert for doctor"""
        patient_name = patient_info.get('name', 'Unknown')
        surgery_type = patient_info.get('surgery_type', 'Unknown')
        phone = patient_info.get('phone', 'Unknown')
        
        severity = analysis.get('severity', 0)
        alerts = analysis.get('alerts', [])
        
        if emergency_details:
            alert_type = "🚨 BYIHUTIRWA - UMURWAYI"
        elif severity > 7:
            alert_type = "⚠️ UKOMERETSE BUKOMEYE"
        else:
            alert_type = "📋 RAPORO Y'UMURWAYI"
        
        report = f"""{alert_type}

👤 {patient_name}
📱 {phone}
🏥 {surgery_type}
📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}

🔴 UKOMERETSE: {severity}/10
🔴 IBIMENYETSO: {', '.join(alerts) if alerts else 'Nta kimenyetso'}

{f'💬 IKIBAZO: {emergency_details}' if emergency_details else ''}

ICYIFUZO: {self._get_doctor_recommendation(severity, alerts, bool(emergency_details))}

---
PostCare+ - Gukurikirana ubuzima"""
        
        return report
    
    def _get_cwh_recommendation(self, severity: float, alerts: List[str]) -> str:
        """Get recommendation for CHW"""
        if severity > 8 or 'HIGH_PAIN' in alerts:
            return "HAMAGARA UMUGANGA VUBA! Umurwayi asaba ubwoba bw'ubuganga bwihutirwa."
        elif severity > 5 or len(alerts) > 1:
            return "Sura umurwayi mu masaha 24 akurikira. Menya niba asaba kujya mu bitaro."
        else:
            return "Kurikirana gisanzwe. Sura umurwayi mu minsi 2-3."
    
    def _get_doctor_recommendation(self, severity: float, alerts: List[str], is_emergency: bool) -> str:
        """Get recommendation for doctor"""
        if is_emergency or severity > 8:
            return "HAMAGARA UMURWAYI VUBA cyangwa musabe kuja mu bitaro ihutirwa."
        elif severity > 6:
            return "Hamagara umurwayi muri uyu munsi cyangwa ejo."
        else:
            return "Kurikirana gisanzwe mu gice cy'icyumweru gikurikira."


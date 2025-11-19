# sms-service/app/kinyarwanda_translations.py
"""
Kinyarwanda translations for PostCare SMS Service
Provides medical terms and responses in Kinyarwanda language
"""

class KinyarwandaTranslations:
    """Kinyarwanda translations for medical and SMS responses"""
    
    def __init__(self):
        self.translations = {
            # Basic greetings and responses
            'hello': 'Muraho',
            'thank_you': 'Murakoze',
            'welcome': 'Murakaza neza',
            'good_morning': 'Muraho mu gitondo',
            'good_afternoon': 'Muraho mu nyama',
            'good_evening': 'Muraho mumugoroba',
            'goodbye': 'Murabeho',
            'yes': 'Yego',
            'no': 'Oya',
            'help': 'Ubufasha',
            
            # Medical terms
            'pain': 'ububabare',
            'wound': 'ikibago',
            'temperature': 'umushyuha',
            'fever': 'umuriro',
            'mobility': 'kugenda',
            'healing': 'gukira',
            'medicine': 'umuti',
            'doctor': 'muganga',
            'nurse': 'umuforomo',
            'hospital': 'ibitaro',
            'surgery': 'kubagwa',
            'recovery': 'gukira',
            'health': 'ubuzima',
            'sick': 'kurwara',
            'well': 'gukira',
            'better': 'gukira neza',
            'worse': 'gusiba',
            'emergency': 'ihutirwa',
            'urgent': 'byihutirwa',
            
            # Pain levels (1-10)
            'pain_levels': {
                1: 'nta bubabare (1)',
                2: 'ububabare buke (2)', 
                3: 'ububabare buke (3)',
                4: 'ububabare bwiza (4)',
                5: 'ububabare bwo hagati (5)',
                6: 'ububabare bukomeye (6)',
                7: 'ububabare bukomeye cyane (7)',
                8: 'ububabare bukabije (8)',
                9: 'ububabare bukabije cyane (9)',
                10: 'ububabare budasubirwaho (10)'
            },
            
            # Common messages
            'messages': {
                'welcome_new_patient': "Muraho {name}, murakaza neza kuri PostCare+! Tuzakurikirana uko mukira nyuma y'ubuganga bwa {surgery_type}. Tuzagira ubusanzwe tubabajije uko mukira kugira ngo twizere ko mukira neza.",
                
                'ussd_menu': """Muraho {name}! Hitamo icyo ushaka:
1. Gutanga amakuru y'ubuzima
2. Kubaza ikibazo mu buzima
3. Gusaba ubufasha bw'ihutirwa
4. Kureba uko mukira
5. Kuvugana n'umuganga
0. Kuva""",
                
                'followup_request': """Muraho {name}, Gusuzuma umunsi wa {day}:

Nyabuneka subiza maze utange ibi bikurikira:
1. Ububabare (1-10): ___
2. Gukira kw'ikibago (1-10): ___  
3. Umushyuha (°C): ___
4. Ubushobozi bwo kugenda (1-10): ___

Urugero:
5
7
37.0
8""",
                
                'thank_you_response': "Murakoze {name} kubw'amakuru. Ubwoba bwawe ni {recovery_score}%. {advice}",
                
                'urgent_alert': "🚨 BYIHUTIRWA {name}: Ibimenyetso byawe bisaba ubwoba bw'ubuganga bwihutirwa. Nyabuneka hamagara umuganga cyangwa ujye mu bitaro byihutirwa. Ibimenyetso: {alerts}",
                
                'needs_attention': "Muraho {name}, ibimenyetso byawe bisaba ubwitabire. Nyabuneka hamagara umuganga niba ibimenyetso bikomeje cyangwa bisibangana. Fata imiti yawe kandi uruhuke. Ibimenyetso: {alerts}",
                
                'good_progress': "Ikinamico {name}! Uko mukira ni neza cyane (Ubwoba: {recovery_score}%). Komeza ukurikiza gahunda yawe yo kwita ku buzima no gufata imiti nk'uko byasabwe.",
                
                'normal_progress': "Murakoze kubw'amakuru, {name}. Uko mukira ni neza (Ubwoba: {recovery_score}%). Komeza ukurikiza gahunda yawe yo kwita ku buzima. Tuzongera tugusuzuma.",
                
                'clarification_needed': "Muraho {name}, nyabuneka subiza gusa n'imibare, kimwe ku murongo:\n1. Ububabare (1-10)\n2. Ikibago (1-10)\n3. Umushyuha\n4. Kugenda (1-10)",
                
                'unknown_patient': "Muraho! Ntibaguzi muri sisitemu ya PostCare. Nyabuneka hamagara umuganga wawe kugira ngo abafashe.",
                
                'provider_alert': """🚨 UMURWAYI ASABA UBWITABIRE: {patient_name} ({phone})
Ubuganga: {surgery_type}
Ibimenyetso: {alerts}
Ukomeretse: {severity}/10
Igihe: {timestamp}

Nyabuneka mukurikire uyu murwayi.""",
                
                'free_conversation_prompt': "Ubu ushobora kutwandikira ikibazo cyose cyangwa icyo ubabaje ku buzima bwawe. Tuzagusubiza ubunahi tunagufasha:",
                
                'ai_advice_intro': "Ubu ni inama y'ubuganga ukurikije ibimenyetso byawe:",
                
                'end_conversation': "Murakoze gukoresha PostCare+. Niba mufite andi makuru, mutwandikire. Mwizere neza!"
            },
            
            # Medical advice templates
            'advice_templates': {
                'high_pain': "Ububabare bukomeye: Fata imiti yo kuraguza ububabare nk'uko muganga yagusabye. Niba bukomeje, hamagara muganga.",
                'poor_wound': "Ikibago gikira nabi: Kora ku karere gutukura, komeza gufata imiti ya antibiotike, hamagara muganga niba kikomeje gusiba.",
                'fever': "Umuriro: Nywa amazi menshi, ruhuka, fata imiti yo kugabanya umuriro. Niba uri hejuru ya 38.5°C cg ukomeje iminsi myinshi, hamagara muganga.",
                'low_mobility': "Ubushobozi buke bwo kugenda: Baza bigenda buhoro, kora siporo idahari, saba ubufasha mu kugenda niba bibaye ngombwa.",
                'good_recovery': "Ukiri neza! Komeza gufata imiti yawe, rya ibiryo byiza, uruhuke bihagije, kandi ujye gusuzuma umuganga nk'uko byagenwe.",
                'general_care': "Komeza gufata imiti yawe nk'uko byasabwe, rya ibiryo byiza, uruhuke bihagije, kandi uhoberana akarere k'ikibago gatukura."
            },
            
            # Emergency keywords that patients might use
            'emergency_keywords': [
                'byihutirwa', 'kubabara cyane', 'sinshobora', 'ndarwaye cyane', 
                'umuriro mukomeye', 'ntabwo nshobora kugenda', 'ikibazo gikomeye',
                'mfite ubwoba', 'nsaba ubufasha', 'ibimenyetso bibi'
            ],
            
            # Question keywords to identify when patients are asking questions
            'question_keywords': [
                'niki', 'nigute', 'ryari', 'hehe', 'kubera iki', 'ese',
                'mbwira', 'nsabe', 'mfasha', 'ikibazo', 'mba'
            ]
        }
    
    def get_translation(self, key, **kwargs):
        """Get translation for a key with optional formatting"""
        if '.' in key:
            # Handle nested keys like 'messages.welcome_new_patient'
            keys = key.split('.')
            value = self.translations
            for k in keys:
                value = value.get(k, key)
                if isinstance(value, str):
                    break
        else:
            value = self.translations.get(key, key)
        
        if isinstance(value, str) and kwargs:
            try:
                return value.format(**kwargs)
            except KeyError:
                return value
        return value
    
    def detect_emergency(self, message):
        """Detect if message contains emergency keywords"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.translations['emergency_keywords'])
    
    def detect_question(self, message):
        """Detect if message contains question keywords"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.translations['question_keywords'])
    
    def get_pain_level_description(self, level):
        """Get Kinyarwanda description for pain level"""
        return self.translations['pain_levels'].get(int(level), f'ububabare {level}')
    
    def generate_medical_advice(self, analysis, patient_data):
        """Generate medical advice in Kinyarwanda based on analysis"""
        advice_parts = []
        alerts = analysis.get('alerts', [])
        
        if 'HIGH_PAIN' in alerts:
            advice_parts.append(self.translations['advice_templates']['high_pain'])
        
        if 'POOR_WOUND_HEALING' in alerts:
            advice_parts.append(self.translations['advice_templates']['poor_wound'])
        
        if 'FEVER' in alerts:
            advice_parts.append(self.translations['advice_templates']['fever'])
        
        if 'LOW_MOBILITY' in alerts:
            advice_parts.append(self.translations['advice_templates']['low_mobility'])
        
        if not advice_parts:
            if analysis.get('recovery_prediction', 0) > 0.7:
                advice_parts.append(self.translations['advice_templates']['good_recovery'])
            else:
                advice_parts.append(self.translations['advice_templates']['general_care'])
        
        return ' '.join(advice_parts)

# Global instance
kinyarwanda = KinyarwandaTranslations()

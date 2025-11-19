# sms-service/app/sms_menu_handler.py
"""
SMS Menu Handler for PostCare SMS Service
Implements USSD-like menu flow through SMS for patient interaction
"""

from enum import Enum
from typing import Dict, Optional, List, Tuple
from datetime import datetime
import re

class MenuState(Enum):
    """SMS Menu states"""
    MAIN_MENU = "main_menu"
    HEALTH_DATA_MENU = "health_data_menu"
    COLLECTING_PAIN = "collecting_pain"
    COLLECTING_WOUND = "collecting_wound" 
    COLLECTING_TEMPERATURE = "collecting_temperature"
    COLLECTING_MOBILITY = "collecting_mobility"
    QUESTION_MODE = "question_mode"
    FREE_CONVERSATION = "free_conversation"
    EMERGENCY_MODE = "emergency_mode"
    COMPLETED = "completed"

class SMSMenuHandler:
    """Handles SMS menu-based interactions (USSD-like flow)"""
    
    def __init__(self, translations, conversation_manager):
        self.translations = translations
        self.conversation_manager = conversation_manager
        self.health_data_fields = ['pain', 'wound', 'temperature', 'mobility']
        print("📱 SMS Menu Handler initialized")
    
    def generate_main_menu(self, patient_name: str) -> str:
        """Generate main menu SMS"""
        menu_text = self.translations.get_translation('messages.ussd_menu', name=patient_name)
        return menu_text
    
    def process_menu_response(self, phone: str, message: str) -> Dict:
        """Process patient response to menu"""
        conversation = self.conversation_manager.get_conversation(phone)
        if not conversation:
            return {'error': 'No active conversation'}
        
        current_state = conversation.get('state', 'initial')
        patient_name = conversation.get('patient_info', {}).get('name', 'Patient')
        
        # Add message to history
        self.conversation_manager.add_message_to_history(phone, message, 'patient')
        
        # Process based on current state
        if current_state == 'initial' or current_state == 'main_menu':
            return self._process_main_menu_selection(phone, message, patient_name)
        
        elif current_state == 'health_data_menu':
            return self._start_health_data_collection(phone, patient_name)
        
        elif current_state in ['collecting_pain', 'collecting_wound', 'collecting_temperature', 'collecting_mobility']:
            return self._process_health_data_input(phone, message, current_state)
        
        elif current_state == 'question_mode':
            return self._start_free_conversation(phone, patient_name)
        
        elif current_state == 'free_conversation':
            return self._process_free_conversation(phone, message, patient_name)
        
        elif current_state == 'emergency_mode':
            return self._process_emergency_mode(phone, message, patient_name)
        
        else:
            return self._send_main_menu(phone, patient_name)
    
    def _process_main_menu_selection(self, phone: str, selection: str, patient_name: str) -> Dict:
        """Process main menu selection"""
        selection = selection.strip()
        
        if selection == '1':
            # Health data collection
            self.conversation_manager.update_conversation_state(phone, MenuState.HEALTH_DATA_MENU)
            return self._start_health_data_collection(phone, patient_name)
        
        elif selection == '2':
            # Ask question mode
            self.conversation_manager.update_conversation_state(phone, MenuState.QUESTION_MODE)
            return self._start_question_mode(phone, patient_name)
        
        elif selection == '3':
            # Emergency help
            self.conversation_manager.update_conversation_state(phone, MenuState.EMERGENCY_MODE)
            return self._start_emergency_mode(phone, patient_name)
        
        elif selection == '4':
            # Recovery status
            return self._show_recovery_status(phone, patient_name)
        
        elif selection == '5':
            # Speak to doctor
            return self._connect_to_doctor(phone, patient_name)
        
        elif selection == '0':
            # Exit
            return self._end_conversation(phone, patient_name)
        
        else:
            # Invalid selection
            return self._send_main_menu_with_error(phone, patient_name)
    
    def _start_health_data_collection(self, phone: str, patient_name: str) -> Dict:
        """Start health data collection process"""
        self.conversation_manager.update_conversation_state(phone, MenuState.COLLECTING_PAIN)
        self.conversation_manager.clear_health_data_session(phone)
        
        message = f"""Muraho {patient_name}! Tuzagukusanya amakuru y'ubuzima bwawe.

Ubanza, twubaze ku bubabare:
Ni gute ububabare bwawe ubu? (Hitamo umubare)

1 = Nta bubabare
2-3 = Ububabare buke
4-6 = Ububabare bwo hagati  
7-8 = Ububabare bukomeye
9-10 = Ububabare bukabije

Subiza n'umubare gusa (1-10):"""
        
        return {
            'response_message': message,
            'action': 'collect_pain_level',
            'next_state': MenuState.COLLECTING_PAIN.value
        }
    
    def _process_health_data_input(self, phone: str, message: str, current_state: str) -> Dict:
        """Process health data input step by step"""
        try:
            # Extract number from message
            number_match = re.search(r'\d+\.?\d*', message.strip())
            if not number_match:
                return self._request_valid_number(phone, current_state)
            
            value = float(number_match.group())
            
            if current_state == 'collecting_pain':
                if not (1 <= value <= 10):
                    return self._request_valid_range(phone, current_state, 1, 10)
                
                self.conversation_manager.store_health_data(phone, 'pain', value)
                self.conversation_manager.update_conversation_state(phone, MenuState.COLLECTING_WOUND)
                
                patient_name = self.conversation_manager.get_conversation(phone)['patient_info']['name']
                message = f"""Murakoze {patient_name}! Ububabare: {self.translations.get_pain_level_description(value)}

Ubwo, gukira kw'ikibago cyawe:
Ni gute ikibago cyawe gikira? (Hitamo umubare)

1-3 = Ntikiri neza (gitukura, gisukuye)
4-6 = Gikira gahoro
7-8 = Gikira neza
9-10 = Girakira neza cyane

Subiza n'umubare gusa (1-10):"""
                
                return {
                    'response_message': message,
                    'action': 'collect_wound_healing',
                    'next_state': MenuState.COLLECTING_WOUND.value
                }
            
            elif current_state == 'collecting_wound':
                if not (1 <= value <= 10):
                    return self._request_valid_range(phone, current_state, 1, 10)
                
                self.conversation_manager.store_health_data(phone, 'wound', value)
                self.conversation_manager.update_conversation_state(phone, MenuState.COLLECTING_TEMPERATURE)
                
                patient_name = self.conversation_manager.get_conversation(phone)['patient_info']['name']
                message = f"""Murakoze {patient_name}! Gukira kw'ikibago: {value}/10

Ubwo, umushyuha wawe:
Ni angahe umushyuha wawe? 

Urugero: 36.5, 37.0, 38.2

Subiza n'umushyuha wawe mu degrees Celsius:"""
                
                return {
                    'response_message': message,
                    'action': 'collect_temperature',
                    'next_state': MenuState.COLLECTING_TEMPERATURE.value
                }
            
            elif current_state == 'collecting_temperature':
                if not (30 <= value <= 45):
                    return self._request_valid_temperature(phone)
                
                self.conversation_manager.store_health_data(phone, 'temperature', value)
                self.conversation_manager.update_conversation_state(phone, MenuState.COLLECTING_MOBILITY)
                
                patient_name = self.conversation_manager.get_conversation(phone)['patient_info']['name']
                temp_status = "bishaje" if value < 36 else "bisanzwe" if value < 37.5 else "umuriro" if value < 38.5 else "umuriro mukomeye"
                
                message = f"""Murakoze {patient_name}! Umushyuha: {value}°C ({temp_status})

Ubwo, ubushobozi bwawe bwo kugenda:
Ni gute ubushobozi bwawe bwo kugenda no gukora?

1-3 = Sinshobora kugenda neza
4-6 = Ngenda gahoro  
7-8 = Ngenda neza
9-10 = Ngenda nk'ubusanzwe

Subiza n'umubare gusa (1-10):"""
                
                return {
                    'response_message': message,
                    'action': 'collect_mobility',
                    'next_state': MenuState.COLLECTING_MOBILITY.value
                }
            
            elif current_state == 'collecting_mobility':
                if not (1 <= value <= 10):
                    return self._request_valid_range(phone, current_state, 1, 10)
                
                self.conversation_manager.store_health_data(phone, 'mobility', value)
                
                # Complete health data collection and analyze
                return self._complete_health_data_collection(phone)
        
        except ValueError:
            return self._request_valid_number(phone, current_state)
    
    def _complete_health_data_collection(self, phone: str) -> Dict:
        """Complete health data collection and provide analysis"""
        health_data = self.conversation_manager.get_health_data_session(phone)
        conversation = self.conversation_manager.get_conversation(phone)
        patient_name = conversation['patient_info']['name']
        
        # Extract values for analysis
        patient_data = {
            'pain': health_data.get('pain', {}).get('value', 5),
            'wound': health_data.get('wound', {}).get('value', 5),
            'temperature': health_data.get('temperature', {}).get('value', 37.0),
            'mobility': health_data.get('mobility', {}).get('value', 5)
        }
        
        # Start free conversation mode
        self.conversation_manager.update_conversation_state(phone, MenuState.FREE_CONVERSATION)
        
        return {
            'response_message': f"""Murakoze cyane {patient_name}! Twakusanyije amakuru yawe:

• Ububabare: {patient_data['pain']}/10
• Gukira kw'ikibago: {patient_data['wound']}/10  
• Umushyuha: {patient_data['temperature']}°C
• Ubushobozi bwo kugenda: {patient_data['mobility']}/10

Ubu ushobora kutwandikira ikibazo cyose cyangwa icyo ubabaje ku buzima bwawe. Tuzagusubiza ubunahi tunagufasha:""",
            'action': 'analyze_and_advise',
            'patient_data': patient_data,
            'next_state': MenuState.FREE_CONVERSATION.value
        }
    
    def _start_question_mode(self, phone: str, patient_name: str) -> Dict:
        """Start question/free conversation mode"""
        self.conversation_manager.update_conversation_state(phone, MenuState.FREE_CONVERSATION)
        
        message = self.translations.get_translation('messages.free_conversation_prompt')
        
        return {
            'response_message': message,
            'action': 'start_free_conversation',
            'next_state': MenuState.FREE_CONVERSATION.value
        }
    
    def _process_free_conversation(self, phone: str, message: str, patient_name: str) -> Dict:
        """Process free conversation message"""
        # Check if it's an emergency
        if self.translations.detect_emergency(message):
            self.conversation_manager.update_conversation_state(phone, MenuState.EMERGENCY_MODE)
            return self._handle_emergency_detected(phone, message, patient_name)
        
        # Normal conversation - generate AI response
        return {
            'response_message': None,  # Will be generated by AI
            'action': 'generate_ai_response',
            'patient_message': message,
            'conversation_type': 'free_conversation',
            'next_state': MenuState.FREE_CONVERSATION.value
        }
    
    def _start_emergency_mode(self, phone: str, patient_name: str) -> Dict:
        """Start emergency mode"""
        message = f"""🚨 {patient_name}, turi mu bwoba bw'ihutirwa.

Ni iki kinabaye? Subiza n'amakuru arambuye:
- Ububabare bukomeye?
- Umuriro mukomeye?
- Amaraso?
- Ubushobozi buke bwo guhumeka?
- Ikindi kintu gikomeye?

Twese turagusubiza vuba!"""
        
        return {
            'response_message': message,
            'action': 'emergency_assessment',
            'next_state': MenuState.EMERGENCY_MODE.value
        }
    
    def _process_emergency_mode(self, phone: str, message: str, patient_name: str) -> Dict:
        """Process emergency mode message"""
        return {
            'response_message': None,  # Will be handled by emergency protocol
            'action': 'handle_emergency',
            'emergency_details': message,
            'next_state': MenuState.EMERGENCY_MODE.value
        }
    
    def _show_recovery_status(self, phone: str, patient_name: str) -> Dict:
        """Show patient's recovery status"""
        # Get recent health data and show progress
        conversation = self.conversation_manager.get_conversation(phone)
        
        # This would normally fetch from patient history
        message = f"""Muraho {patient_name}! Uko mukira:

📊 Raporo y'ubuzima bwawe:
• Imitsi 3 ishize: Ukiri neza
• Ububabare bugabanye: ✅
• Ikibago gikira: ✅  
• Umushyuha usanzwe: ✅

Komeza ukurikiza amahoro na muganga!

Hitamo ikindi:
1. Gutanga amakuru mashya
2. Kubaza ikibazo 
0. Kurangiza"""
        
        return {
            'response_message': message,
            'action': 'show_status',
            'next_state': 'main_menu'  # Return to main menu
        }
    
    def _connect_to_doctor(self, phone: str, patient_name: str) -> Dict:
        """Connect patient to doctor"""
        message = f"""Muraho {patient_name}!

🩺 Guhana umuganga:
Tugiye kumenyesha umuganga wawe ko usaba kuvugana nawe.

Azagukurikira mu gitondo cya mbere (saa 2-4)

Cyangwa wamuhamagara kuri:
📞 +250-XXX-XXXX (Muganga mukuru)
📞 +250-XXX-XXXX (Umuforomo w'ihutirwa)

Hari ikindi ushaka?
1. Gutanga amakuru y'ubuzima
2. Kubaza ikibazo
0. Kurangiza"""
        
        return {
            'response_message': message,
            'action': 'alert_doctor',
            'next_state': 'main_menu'
        }
    
    def _end_conversation(self, phone: str, patient_name: str) -> Dict:
        """End conversation"""
        self.conversation_manager.end_conversation(phone)
        
        message = self.translations.get_translation('messages.end_conversation')
        
        return {
            'response_message': message,
            'action': 'end_conversation',
            'next_state': MenuState.COMPLETED.value
        }
    
    def _send_main_menu(self, phone: str, patient_name: str) -> Dict:
        """Send main menu"""
        self.conversation_manager.update_conversation_state(phone, MenuState.MAIN_MENU)
        menu_message = self.generate_main_menu(patient_name)
        
        return {
            'response_message': menu_message,
            'action': 'show_main_menu',
            'next_state': MenuState.MAIN_MENU.value
        }
    
    def _send_main_menu_with_error(self, phone: str, patient_name: str) -> Dict:
        """Send main menu with error message"""
        menu_message = f"""Ntibigezweho {patient_name}! Hitamo umubare muri aya:

{self.generate_main_menu(patient_name)}"""
        
        return {
            'response_message': menu_message,
            'action': 'show_main_menu_error',
            'next_state': MenuState.MAIN_MENU.value
        }
    
    def _request_valid_number(self, phone: str, current_state: str) -> Dict:
        """Request valid number input"""
        field_name = current_state.replace('collecting_', '')
        
        if field_name == 'pain':
            message = "Nyabuneka subiza n'umubare gusa kuva 1 kugeza 10 kuri ububabare:"
        elif field_name == 'wound':
            message = "Nyabuneka subiza n'umubare gusa kuva 1 kugeza 10 kuri gukira kw'ikibago:"
        elif field_name == 'temperature':
            message = "Nyabuneka subiza n'umushyuha wawe. Urugero: 36.5, 37.2:"
        elif field_name == 'mobility':
            message = "Nyabuneka subiza n'umubare gusa kuva 1 kugeza 10 kuri ubushobozi bwo kugenda:"
        else:
            message = "Nyabuneka subiza n'umubare mwiza:"
        
        return {
            'response_message': message,
            'action': 'request_valid_input',
            'next_state': current_state
        }
    
    def _request_valid_range(self, phone: str, current_state: str, min_val: int, max_val: int) -> Dict:
        """Request valid range input"""
        message = f"Nyabuneka subiza n'umubare kuva {min_val} kugeza {max_val}:"
        
        return {
            'response_message': message,
            'action': 'request_valid_range',
            'next_state': current_state
        }
    
    def _request_valid_temperature(self, phone: str) -> Dict:
        """Request valid temperature input"""
        message = "Nyabuneka subiza n'umushyuha mwiza. Urugero: 36.5, 37.0, 38.5:"
        
        return {
            'response_message': message,
            'action': 'request_valid_temperature',
            'next_state': 'collecting_temperature'
        }
    
    def _handle_emergency_detected(self, phone: str, message: str, patient_name: str) -> Dict:
        """Handle emergency detected in free conversation"""
        response = f"""🚨 BYIHUTIRWA! {patient_name}

Twabonye ko wavuze ikibazo gikomeye. Tugiye kwihutira gufasha:

1. Hamagara umuganga wawe VUBA
2. Cyangwa jya mu bitaro byihutirwa
3. Hamagara: 912 (ihutirwa)

Tugiye kumenyesha umuganga wawe UBUNYANGAMUGAYO!

Komeza utubwire ibindi byimbitse:"""
        
        return {
            'response_message': response,
            'action': 'emergency_detected',
            'emergency_message': message,
            'next_state': MenuState.EMERGENCY_MODE.value
        }


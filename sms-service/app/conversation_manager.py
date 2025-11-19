# sms-service/app/conversation_manager.py
"""
Conversation State Manager for PostCare SMS Service
Manages patient conversation states, USSD menus, and conversation flows
"""

import json
import pickle
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Any

class ConversationState(Enum):
    """Patient conversation states"""
    INITIAL = "initial"
    USSD_MENU = "ussd_menu"
    COLLECTING_HEALTH_DATA = "collecting_health_data"
    FREE_CONVERSATION = "free_conversation"
    WAITING_FOR_ADVICE = "waiting_for_advice"
    EMERGENCY_MODE = "emergency_mode"
    ENDED = "ended"

class USSDMenuOption(Enum):
    """USSD menu options"""
    HEALTH_DATA = "1"
    ASK_QUESTION = "2"
    EMERGENCY_HELP = "3"
    RECOVERY_STATUS = "4"
    SPEAK_TO_DOCTOR = "5"
    EXIT = "0"

class ConversationManager:
    """Manages patient conversation states and flows"""
    
    def __init__(self, data_file='conversation_states.pkl'):
        self.data_file = data_file
        self.conversations = self.load_conversation_data()
        self.session_timeout = 1800  # 30 minutes
        print(f"💬 Conversation Manager initialized ({len(self.conversations)} active conversations)")
    
    def load_conversation_data(self):
        """Load conversation data from file"""
        try:
            with open(self.data_file, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            print("📁 No existing conversation data file found, starting fresh")
            return {}
        except Exception as e:
            print(f"⚠️ Error loading conversation data: {e}")
            return {}
    
    def save_conversation_data(self):
        """Save conversation data to file"""
        try:
            with open(self.data_file, 'wb') as f:
                pickle.dump(self.conversations, f)
        except Exception as e:
            print(f"❌ Error saving conversation data: {e}")
    
    def start_conversation(self, patient_id: str, phone: str, patient_info: Dict) -> Dict:
        """Start a new conversation with a patient"""
        conversation_id = f"{patient_id}_{int(time.time())}"
        
        self.conversations[phone] = {
            'conversation_id': conversation_id,
            'patient_id': patient_id,
            'phone': phone,
            'patient_info': patient_info,
            'state': ConversationState.INITIAL.value,
            'started_at': datetime.now().isoformat(),
            'last_activity': datetime.now().isoformat(),
            'message_history': [],
            'health_data_session': {},
            'context': {},
            'language': patient_info.get('language', 'rw')  # Default to Kinyarwanda
        }
        
        self.save_conversation_data()
        print(f"💬 Started conversation for {patient_info.get('name', patient_id)} ({phone})")
        
        return self.conversations[phone]
    
    def get_conversation(self, phone: str) -> Optional[Dict]:
        """Get active conversation for a phone number"""
        conversation = self.conversations.get(phone)
        
        if conversation:
            # Check if conversation has timed out
            last_activity = datetime.fromisoformat(conversation['last_activity'])
            if datetime.now() - last_activity > timedelta(seconds=self.session_timeout):
                print(f"⏰ Conversation timed out for {phone}")
                self.end_conversation(phone)
                return None
        
        return conversation
    
    def update_conversation_state(self, phone: str, new_state: ConversationState, context: Dict = None):
        """Update conversation state"""
        conversation = self.conversations.get(phone)
        if conversation:
            conversation['state'] = new_state.value
            conversation['last_activity'] = datetime.now().isoformat()
            
            if context:
                conversation['context'].update(context)
            
            self.save_conversation_data()
            print(f"💬 Updated conversation state for {phone}: {new_state.value}")
    
    def add_message_to_history(self, phone: str, message: str, sender: str, message_type: str = "text"):
        """Add message to conversation history"""
        conversation = self.conversations.get(phone)
        if conversation:
            message_record = {
                'timestamp': datetime.now().isoformat(),
                'sender': sender,  # 'patient' or 'system'
                'message': message,
                'type': message_type,  # 'text', 'ussd', 'health_data', etc.
            }
            
            conversation['message_history'].append(message_record)
            conversation['last_activity'] = datetime.now().isoformat()
            
            # Keep only last 50 messages to prevent file from growing too large
            if len(conversation['message_history']) > 50:
                conversation['message_history'] = conversation['message_history'][-50:]
            
            self.save_conversation_data()
    
    def process_ussd_selection(self, phone: str, selection: str) -> Dict:
        """Process USSD menu selection"""
        conversation = self.get_conversation(phone)
        if not conversation:
            return {'error': 'No active conversation'}
        
        try:
            option = USSDMenuOption(selection)
            
            if option == USSDMenuOption.HEALTH_DATA:
                self.update_conversation_state(phone, ConversationState.COLLECTING_HEALTH_DATA)
                return {
                    'action': 'collect_health_data',
                    'next_state': ConversationState.COLLECTING_HEALTH_DATA.value
                }
            
            elif option == USSDMenuOption.ASK_QUESTION:
                self.update_conversation_state(phone, ConversationState.FREE_CONVERSATION)
                return {
                    'action': 'start_free_conversation',
                    'next_state': ConversationState.FREE_CONVERSATION.value
                }
            
            elif option == USSDMenuOption.EMERGENCY_HELP:
                self.update_conversation_state(phone, ConversationState.EMERGENCY_MODE)
                return {
                    'action': 'emergency_mode',
                    'next_state': ConversationState.EMERGENCY_MODE.value
                }
            
            elif option == USSDMenuOption.RECOVERY_STATUS:
                return {
                    'action': 'show_recovery_status',
                    'next_state': conversation['state']  # Stay in current state
                }
            
            elif option == USSDMenuOption.SPEAK_TO_DOCTOR:
                return {
                    'action': 'connect_to_doctor',
                    'next_state': conversation['state']
                }
            
            elif option == USSDMenuOption.EXIT:
                self.end_conversation(phone)
                return {
                    'action': 'end_conversation',
                    'next_state': ConversationState.ENDED.value
                }
            
        except ValueError:
            return {'error': 'Invalid menu selection'}
    
    def store_health_data(self, phone: str, data_type: str, value: Any):
        """Store health data during collection session"""
        conversation = self.conversations.get(phone)
        if conversation:
            if 'health_data_session' not in conversation:
                conversation['health_data_session'] = {}
            
            conversation['health_data_session'][data_type] = {
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
            
            conversation['last_activity'] = datetime.now().isoformat()
            self.save_conversation_data()
    
    def get_health_data_session(self, phone: str) -> Dict:
        """Get current health data collection session"""
        conversation = self.conversations.get(phone)
        if conversation:
            return conversation.get('health_data_session', {})
        return {}
    
    def clear_health_data_session(self, phone: str):
        """Clear health data collection session"""
        conversation = self.conversations.get(phone)
        if conversation:
            conversation['health_data_session'] = {}
            self.save_conversation_data()
    
    def end_conversation(self, phone: str):
        """End conversation and clean up"""
        if phone in self.conversations:
            conversation = self.conversations[phone]
            conversation['state'] = ConversationState.ENDED.value
            conversation['ended_at'] = datetime.now().isoformat()
            
            # Archive completed conversation (could be moved to a separate file)
            # For now, just mark as ended
            self.save_conversation_data()
            print(f"💬 Ended conversation for {phone}")
    
    def get_conversation_context(self, phone: str) -> Dict:
        """Get conversation context for AI processing"""
        conversation = self.get_conversation(phone)
        if not conversation:
            return {}
        
        # Get recent message history for context
        recent_messages = conversation.get('message_history', [])[-10:]  # Last 10 messages
        
        return {
            'patient_info': conversation.get('patient_info', {}),
            'current_state': conversation.get('state'),
            'recent_messages': recent_messages,
            'health_data_session': conversation.get('health_data_session', {}),
            'language': conversation.get('language', 'rw'),
            'conversation_duration': self._calculate_duration(conversation),
            'context': conversation.get('context', {})
        }
    
    def _calculate_duration(self, conversation: Dict) -> int:
        """Calculate conversation duration in minutes"""
        try:
            started = datetime.fromisoformat(conversation['started_at'])
            now = datetime.now()
            return int((now - started).total_seconds() / 60)
        except:
            return 0
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up conversations older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        phones_to_remove = []
        
        for phone, conversation in self.conversations.items():
            try:
                last_activity = datetime.fromisoformat(conversation['last_activity'])
                if last_activity < cutoff_time:
                    phones_to_remove.append(phone)
            except:
                phones_to_remove.append(phone)  # Remove invalid entries
        
        for phone in phones_to_remove:
            del self.conversations[phone]
        
        if phones_to_remove:
            self.save_conversation_data()
            print(f"🧹 Cleaned up {len(phones_to_remove)} old conversations")
    
    def get_statistics(self) -> Dict:
        """Get conversation statistics"""
        total_conversations = len(self.conversations)
        
        state_counts = {}
        for conversation in self.conversations.values():
            state = conversation.get('state', 'unknown')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        return {
            'total_active_conversations': total_conversations,
            'state_distribution': state_counts,
            'session_timeout_minutes': self.session_timeout // 60
        }


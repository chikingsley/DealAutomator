import anthropic
from app.core.config import settings
import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self):
        self.client = anthropic.Client(api_key=settings.ANTHROPIC_API_KEY)
        self.conversation_context = {}
        self.system_prompt = """You are a specialized parser and conversational agent for affiliate marketing deals. You can:
1. Parse and extract structured deal information
2. Handle natural language queries about deals
3. Maintain conversation context
4. Verify and validate deal information
5. Provide clear feedback and suggestions"""

    async def handle_message(self, user_id: str, message: str) -> Dict:
        """Handle incoming messages and maintain conversation context"""
        try:
            # Update conversation context
            if user_id not in self.conversation_context:
                self.conversation_context[user_id] = []
            
            # Add message to context
            self.conversation_context[user_id].append({
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            })

            # Detect message intent
            if any(query in message.lower() for query in ["show deals", "current deals", "active deals"]):
                return await self._handle_deal_query(message)
            elif any(query in message.lower() for query in ["check column", "verify structure", "database schema"]):
                return await self._handle_schema_query(message)
            elif "parse deal" in message.lower():
                return await self.parse_deal(message)
            else:
                return await self._handle_general_conversation(user_id, message)

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return {"error": "Failed to process message", "details": str(e)}

    async def parse_deal(self, text: str) -> Dict:
        """Parse deal information and handle verification"""
        try:
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0,
                system=self.system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Parse this deal text and return JSON with verification summary:\n{text}"
                }]
            )
            
            try:
                content = response.content[0].text
                parsed_data = json.loads(content)
                validated_data = await self._validate_parsed_data(parsed_data)
                
                if validated_data:
                    verification_summary = self._generate_verification_summary(validated_data)
                    return {
                        "data": validated_data,
                        "verification": verification_summary,
                        "requires_confirmation": True
                    }
                return None
                
            except (IndexError, KeyError, json.JSONDecodeError) as e:
                logger.error(f"Failed to parse Claude response: {str(e)}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Claude API: {str(e)}")
            return None

    async def _validate_parsed_data(self, data: Dict) -> Dict:
        """Enhanced validation with detailed feedback"""
        required_fields = ['geo', 'language_code', 'pricing_model']
        validation_errors = []
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                validation_errors.append(f"Missing required field: {field}")

        # Validate data types and formats
        if 'cpa_amount' in data and not isinstance(data['cpa_amount'], (int, float)):
            validation_errors.append("CPA amount must be a number")
        
        if 'expiration_date' in data:
            try:
                datetime.fromisoformat(data['expiration_date'])
            except ValueError:
                validation_errors.append("Invalid expiration date format")

        # Clean and standardize data
        if 'sources' in data and isinstance(data['sources'], list):
            data['sources'] = [self._standardize_source(s) for s in data['sources']]

        if validation_errors:
            logger.error("Validation errors: " + ", ".join(validation_errors))
            data['validation_errors'] = validation_errors
            
        return data

    def _standardize_source(self, source: str) -> str:
        """Standardize traffic source names"""
        source = source.lower().strip()
        for standard, variants in settings.SOURCE_MAPPING.items():
            if source in [v.lower() for v in variants]:
                return standard
        return source.upper()

    def _generate_verification_summary(self, data: Dict) -> Dict:
        """Generate human-readable verification summary"""
        return {
            "summary": f"Deal for {data.get('partner_name', 'Unknown Partner')}",
            "key_points": [
                f"Geographic Region: {data.get('geo', 'Not specified')}",
                f"Pricing Model: {data.get('pricing_model', 'Not specified')}",
                f"Traffic Sources: {', '.join(data.get('sources', []))}",
            ],
            "warnings": data.get('validation_errors', []),
            "requires_attention": bool(data.get('validation_errors', []))
        }

    async def _handle_deal_query(self, message: str) -> Dict:
        """Handle queries about current deals"""
        # Implementation would interact with NotionService to fetch active deals
        pass

    async def _handle_schema_query(self, message: str) -> Dict:
        """Handle database schema verification queries"""
        # Implementation would interact with NotionService to verify schema
        pass

    async def _handle_general_conversation(self, user_id: str, message: str) -> Dict:
        """Handle general conversation with context"""
        try:
            # Get recent conversation context
            recent_context = self.conversation_context[user_id][-5:]  # Last 5 messages
            
            response = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                temperature=0.7,
                system=self.system_prompt,
                messages=[{
                    "role": msg["role"],
                    "content": msg["content"]
                } for msg in recent_context]
            )
            
            return {
                "type": "conversation",
                "response": response.content
            }
            
        except Exception as e:
            logger.error(f"Error in conversation handling: {str(e)}")
            return {"error": "Failed to process conversation"}

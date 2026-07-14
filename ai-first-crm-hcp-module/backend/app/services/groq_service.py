import os
import json
from typing import Dict, Any, Optional
from groq import Groq
from app.core.config import settings


class GroqService:
    """
    Service for interacting with Groq API using gemma2-9b-it model.
    Provides structured extraction capabilities for CRM interactions.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "gemma2-9b-it")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        self.client = Groq(api_key=self.api_key)
    
    def extract_interaction(self, conversation_text: str) -> Dict[str, Any]:
        """
        Extract structured interaction data from conversation text using Groq LLM.
        
        Args:
            conversation_text: The raw conversation text from the interaction
            
        Returns:
            Dictionary containing extracted fields:
            - doctor_name: Name of the doctor/HCP
            - hospital: Hospital or organization name
            - interaction_date: Date of the interaction
            - products_discussed: List of products discussed
            - doctor_feedback: Feedback from the doctor
            - follow_up_date: Date for follow-up
            - meeting_outcome: Outcome of the meeting
            - summary: Summary of the interaction
            
            Returns null for any missing information.
        """
        # Structured prompt for extraction
        system_prompt = """You are an expert at extracting structured information from healthcare professional (HCP) interaction notes. 
Extract the following fields from the conversation text and return ONLY valid JSON:

- doctor_name: Full name of the doctor/healthcare professional
- hospital: Hospital or organization name where they work
- interaction_date: Date when the interaction occurred (in YYYY-MM-DD format if possible)
- products_discussed: List of products, medications, or treatments discussed
- doctor_feedback: Any feedback, concerns, or opinions expressed by the doctor
- follow_up_date: Date for any scheduled follow-up (in YYYY-MM-DD format if possible)
- meeting_outcome: Overall outcome of the meeting (e.g., "positive", "negative", "neutral", "scheduled follow-up", "requested information")
- summary: Brief summary of the interaction (2-3 sentences)

IMPORTANT:
- Return ONLY valid JSON, no additional text or explanation
- If information is not found in the text, use null for that field
- products_discussed should be an array of strings, or null if none found
- Ensure all dates are in YYYY-MM-DD format when possible
- Be precise and extract exact information when available"""

        user_prompt = f"""Extract structured information from the following HCP interaction conversation:

{conversation_text}

Return the result as valid JSON with the fields: doctor_name, hospital, interaction_date, products_discussed, doctor_feedback, follow_up_date, meeting_outcome, summary"""

        try:
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=1024,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content
            extracted_data = json.loads(content)
            
            # Validate and clean the extracted data
            cleaned_data = self._validate_extracted_data(extracted_data)
            
            return {
                "success": True,
                "data": cleaned_data,
                "raw_response": content
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_response": response.choices[0].message.content if response else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Groq API error: {str(e)}",
                "raw_response": None
            }
    
    def _validate_extracted_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the extracted data to ensure it matches expected schema.
        
        Args:
            data: Raw extracted data from LLM
            
        Returns:
            Cleaned and validated data
        """
        expected_fields = {
            "doctor_name": None,
            "hospital": None,
            "interaction_date": None,
            "products_discussed": None,
            "doctor_feedback": None,
            "follow_up_date": None,
            "meeting_outcome": None,
            "summary": None
        }
        
        # Merge with extracted data
        for field, default_value in expected_fields.items():
            if field in data:
                value = data[field]
                
                # Handle empty strings
                if value == "" or value == "null" or value is None:
                    expected_fields[field] = None
                # Ensure products_discussed is a list
                elif field == "products_discussed" and not isinstance(value, list):
                    if isinstance(value, str):
                        # Split by comma if it's a string
                        expected_fields[field] = [item.strip() for item in value.split(",") if item.strip()]
                    else:
                        expected_fields[field] = None
                else:
                    expected_fields[field] = value
            else:
                expected_fields[field] = default_value
        
        return expected_fields
    
    def extract_edit_modifications(self, user_input: str) -> Dict[str, Any]:
        """
        Extract modification requests from user input for editing an interaction.
        
        Args:
            user_input: The user's request to modify an interaction
            
        Returns:
            Dictionary containing extracted modification fields:
            - discussion: Updated discussion text
            - summary: Updated summary
            - follow_up_date: Updated follow-up date (YYYY-MM-DD format)
            - interaction_date: Updated interaction date (YYYY-MM-DD format)
            
            Returns null for fields that are not being modified.
        """
        system_prompt = """You are an expert at understanding modification requests for healthcare professional (HCP) interaction records.
Extract the modification details from the user's request and return ONLY valid JSON.

The user may want to modify:
- discussion: The discussion/notes of the interaction
- summary: The summary of the interaction
- follow_up_date: The follow-up date (in YYYY-MM-DD format)
- interaction_date: The interaction date (in YYYY-MM-DD format)

IMPORTANT:
- Return ONLY valid JSON, no additional text or explanation
- If a field is not being modified, use null for that field
- Only include fields that the user explicitly wants to change
- Extract exact values when provided
- For dates, use YYYY-MM-DD format"""

        user_prompt = f"""Extract the modification details from the following user request:

{user_input}

Return the result as valid JSON with the fields: discussion, summary, follow_up_date, interaction_date"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=512,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            extracted_data = json.loads(content)
            
            # Validate and clean the extracted data
            cleaned_data = self._validate_edit_modifications(extracted_data)
            
            return {
                "success": True,
                "data": cleaned_data,
                "raw_response": content
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_response": response.choices[0].message.content if response else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Groq API error: {str(e)}",
                "raw_response": None
            }
    
    def _validate_edit_modifications(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean the extracted modification data.
        
        Args:
            data: Raw extracted modification data from LLM
            
        Returns:
            Cleaned and validated modification data
        """
        expected_fields = {
            "discussion": None,
            "summary": None,
            "follow_up_date": None,
            "interaction_date": None
        }
        
        for field, default_value in expected_fields.items():
            if field in data:
                value = data[field]
                
                if value == "" or value == "null" or value is None:
                    expected_fields[field] = None
                else:
                    expected_fields[field] = value
            else:
                expected_fields[field] = default_value
        
        return expected_fields
    
    def generate_response(self, user_message: str, context: str = None) -> str:
        system_prompt = """You are a helpful AI assistant for a Healthcare Professional (HCP) CRM system. 
Your role is to help sales representatives log interactions, search for information, and get recommendations.
Be professional, concise, and helpful in your responses."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        if context:
            messages.insert(1, {"role": "system", "content": f"Context: {context}"})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=512
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error generating response: {str(e)}"


# Singleton instance
_groq_service: Optional[GroqService] = None


def get_groq_service() -> GroqService:
    """
    Get or create the Groq service singleton instance.
    
    Returns:
        GroqService instance
    """
    global _groq_service
    
    if _groq_service is None:
        _groq_service = GroqService()
    
    return _groq_service


def extract_interaction(conversation_text: str) -> Dict[str, Any]:
    """
    Convenience function to extract interaction data from conversation text.
    
    Args:
        conversation_text: The raw conversation text from the interaction
        
    Returns:
        Dictionary containing extracted fields or error information
    """
    service = get_groq_service()
    return service.extract_interaction(conversation_text)


def extract_edit_modifications(user_input: str) -> Dict[str, Any]:
    """
    Convenience function to extract edit modifications from user input.
    
    Args:
        user_input: The user's request to modify an interaction
        
    Returns:
        Dictionary containing extracted modification fields or error information
    """
    service = get_groq_service()
    return service.extract_edit_modifications(user_input)


if __name__ == "__main__":
    # Test the service
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Test conversation
    test_conversation = """
    I had a meeting with Dr. Sarah Johnson at City Hospital yesterday. 
    We discussed the new cardiovascular medication CardiMax and the diabetes treatment DiabCare.
    Dr. Johnson seemed interested in CardiMax but had some concerns about the pricing.
    She asked for more clinical data and we scheduled a follow-up meeting for next Friday.
    Overall, the meeting went well and she's considering a trial.
    """
    
    print("Testing Groq Service...")
    print(f"Model: {os.getenv('GROQ_MODEL', 'gemma2-9b-it')}")
    print(f"\nInput conversation:\n{test_conversation}\n")
    
    result = extract_interaction(test_conversation)
    
    if result["success"]:
        print("Extraction successful!")
        print("\nExtracted data:")
        print(json.dumps(result["data"], indent=2))
    else:
        print("Extraction failed!")
        print(f"Error: {result['error']}")
        if result.get("raw_response"):
            print(f"Raw response: {result['raw_response']}")

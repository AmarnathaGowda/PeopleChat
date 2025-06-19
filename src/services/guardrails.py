"""
Guardrails service for content filtering and security
"""
import re
from typing import List, Dict, Any, Optional
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from utils.logger import get_logger

logger = get_logger(__name__)


class GuardrailsService:
    """Service for implementing security guardrails"""
    
    def __init__(self):
        # Initialize Presidio engines
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # Patterns for detecting potential security threats
        self.injection_patterns = [
            # SQL injection patterns
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(from|where|table)\b)",
            # Command injection patterns
            r"(;|\||&|`|\$\(|<\()",
            # Path traversal
            r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/)",
        ]
        
        # Sensitive information patterns
        self.sensitive_patterns = {
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
            "api_key": r"\b(api[_-]?key|apikey)\s*[:=]\s*['\"]?([a-zA-Z0-9]{32,})['\"]?\b",
        }
    
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in text using Presidio
        
        Args:
            text: Text to analyze
            
        Returns:
            List of PII entities found
        """
        try:
            results = self.analyzer.analyze(
                text=text,
                language='en',
                entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON", "LOCATION"]
            )
            
            pii_entities = []
            for result in results:
                pii_entities.append({
                    "type": result.entity_type,
                    "start": result.start,
                    "end": result.end,
                    "score": result.score,
                    "text": text[result.start:result.end]
                })
            
            return pii_entities
        except Exception as e:
            logger.error(f"PII detection error: {str(e)}")
            return []
    
    def anonymize_pii(self, text: str) -> str:
        """
        Anonymize PII in text
        
        Args:
            text: Text to anonymize
            
        Returns:
            Anonymized text
        """
        try:
            # First detect PII
            results = self.analyzer.analyze(text=text, language='en')
            
            # Then anonymize
            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=results
            )
            
            return anonymized_result.text
        except Exception as e:
            logger.error(f"PII anonymization error: {str(e)}")
            return text
    
    def detect_injection_attempts(self, text: str) -> bool:
        """
        Detect potential injection attempts
        
        Args:
            text: Text to check
            
        Returns:
            True if injection attempt detected
        """
        text_lower = text.lower()
        
        for pattern in self.injection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.warning(f"Potential injection attempt detected: {text[:100]}...")
                return True
        
        return False
    
    def sanitize_output(self, text: str, user_context: Optional[Dict] = None) -> str:
        """
        Sanitize output before sending to user
        
        Args:
            text: Text to sanitize
            user_context: Optional user context for role-based filtering
            
        Returns:
            Sanitized text
        """
        # Remove any detected sensitive patterns
        for pattern_name, pattern in self.sensitive_patterns.items():
            text = re.sub(pattern, "[REDACTED]", text, flags=re.IGNORECASE)
        
        # Additional sanitization based on user role
        if user_context and user_context.get("role") != "admin":
            # Remove internal system information
            text = re.sub(r"(error:|exception:|traceback:).*", "[SYSTEM_ERROR]", text, flags=re.IGNORECASE)
        
        return text
    
    def validate_input(self, text: str, max_length: int = 5000) -> Dict[str, Any]:
        """
        Validate user input
        
        Args:
            text: Input text to validate
            max_length: Maximum allowed length
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check length
        if len(text) > max_length:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Input exceeds maximum length of {max_length} characters")
        
        # Check for injection attempts
        if self.detect_injection_attempts(text):
            validation_result["valid"] = False
            validation_result["errors"].append("Potential security threat detected")
        
        # Check for PII
        pii_entities = self.detect_pii(text)
        if pii_entities:
            validation_result["warnings"].append(f"PII detected: {[e['type'] for e in pii_entities]}")
        
        # Check for empty input
        if not text.strip():
            validation_result["valid"] = False
            validation_result["errors"].append("Input cannot be empty")
        
        return validation_result


# Singleton instance
guardrails_service = GuardrailsService()
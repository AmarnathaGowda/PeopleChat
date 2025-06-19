"""
Test guardrails service
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.guardrails import guardrails_service


def test_pii_detection():
    """Test PII detection"""
    print("\n=== Testing PII Detection ===")
    
    test_texts = [
        "My email is john.doe@example.com",
        "Call me at 555-123-4567",
        "My name is John Doe and I live in New York",
        "My SSN is 123-45-6789",
        "Normal text without any PII"
    ]
    
    for text in test_texts:
        print(f"\nText: {text}")
        pii_entities = guardrails_service.detect_pii(text)
        if pii_entities:
            print("  PII Detected:")
            for entity in pii_entities:
                print(f"    - {entity['type']}: {entity['text']}")
        else:
            print("  No PII detected")


def test_injection_detection():
    """Test injection detection"""
    print("\n=== Testing Injection Detection ===")
    
    test_inputs = [
        "SELECT * FROM users WHERE id = 1",
        "Normal query about users",
        "'; DROP TABLE users; --",
        "../../etc/passwd",
        "Hello, how are you?"
    ]
    
    for input_text in test_inputs:
        is_injection = guardrails_service.detect_injection_attempts(input_text)
        print(f"Input: {input_text}")
        print(f"  Injection detected: {is_injection}")


def test_input_validation():
    """Test input validation"""
    print("\n=== Testing Input Validation ===")
    
    test_cases = [
        "Normal input text",
        "",  # Empty input
        "a" * 6000,  # Too long
        "SELECT * FROM users",  # SQL injection
        "My email is test@example.com"  # Contains PII
    ]
    
    for test_input in test_cases:
        result = guardrails_service.validate_input(test_input)
        print(f"\nInput: {test_input[:50]}{'...' if len(test_input) > 50 else ''}")
        print(f"  Valid: {result['valid']}")
        if result['errors']:
            print(f"  Errors: {result['errors']}")
        if result['warnings']:
            print(f"  Warnings: {result['warnings']}")


def main():
    """Run all tests"""
    print("Starting guardrails tests...")
    
    test_pii_detection()
    test_injection_detection()
    test_input_validation()
    
    print("\n=== Tests Complete ===")


if __name__ == "__main__":
    main()
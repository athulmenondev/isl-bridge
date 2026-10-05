import sys
import os

# Add src folder to module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from isl_nlp_parser import ISLParser

def test_isl_grammar_rules():
    parser = ISLParser()
    
    test_cases = [
        ("The boy is eating an apple", ["BOY", "APPLE", "EAT"]),
        ("I am going to school", ["I", "SCHOOL", "GO"]),
        ("She buys a new car", ["SHE", "NEW", "CAR", "BUY"])
    ]
    
    print("\n--- RUNNING UNIT TESTS ---")
    passed = 0
    for idx, (sentence, expected) in enumerate(test_cases, 1):
        result = parser.parse(sentence)
        is_correct = result == expected
        print(f"Test {idx}: '{sentence}' -> {result} | Passed: {is_correct}")
        if is_correct: 
            passed += 1

    print(f"\nResults: {passed}/{len(test_cases)} Passed")

if __name__ == "__main__":
    test_isl_grammar_rules()

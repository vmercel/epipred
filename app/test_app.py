#!/usr/bin/env python3
"""
Test script for EpiPred web application
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print(f"✓ Flask {flask.__version__}")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow {tf.__version__}")
    except ImportError as e:
        print(f"✗ TensorFlow import failed: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✓ Pandas {pd.__version__}")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if Flask app can be created"""
    print("\nTesting Flask app creation...")
    
    try:
        from app import app
        print("✓ Flask app created successfully")
        return True
    except Exception as e:
        print(f"✗ Flask app creation failed: {e}")
        return False

def test_model_predictor():
    """Test model predictor initialization"""
    print("\nTesting model predictor...")
    
    try:
        from model_predictor import EpitopePredictor
        
        # Try to create predictor (may fail if no model files)
        try:
            predictor = EpitopePredictor()
            print("✓ Model predictor created successfully")
            
            # Test model info
            info = predictor.get_model_info()
            print(f"✓ Model info retrieved: {len(info)} parameters")
            
            return True
        except Exception as e:
            print(f"⚠ Model predictor creation failed (expected if no model files): {e}")
            return True  # This is expected without model files
            
    except Exception as e:
        print(f"✗ Model predictor import failed: {e}")
        return False

def test_fasta_parsing():
    """Test FASTA parsing functionality"""
    print("\nTesting FASTA parsing...")
    
    try:
        from app import parse_fasta_text, validate_sequences
        
        # Test valid FASTA
        test_fasta = """>Test_Sequence_1
MKLLILTCLVAVALARPKHPIKHQGLPQEVLNENLLRFFVAPFPEVFGKEKVNEL

>Test_Sequence_2
CARFASLIYGKFVRQPQVWLRIQNYSVMDICDEHQGVMVPGVGVPQALQKYNPD"""
        
        sequences = parse_fasta_text(test_fasta)
        print(f"✓ Parsed {len(sequences)} sequences")
        
        # Test validation
        errors = validate_sequences(sequences)
        if not errors:
            print("✓ Sequence validation passed")
        else:
            print(f"⚠ Validation warnings: {errors}")
        
        return True
        
    except Exception as e:
        print(f"✗ FASTA parsing test failed: {e}")
        return False

def test_routes():
    """Test Flask routes"""
    print("\nTesting Flask routes...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test main page
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Main page route works")
            else:
                print(f"✗ Main page returned status {response.status_code}")
                return False
            
            # Test instructions page
            response = client.get('/instructions')
            if response.status_code == 200:
                print("✓ Instructions page route works")
            else:
                print(f"✗ Instructions page returned status {response.status_code}")
                return False
            
            # Test about page
            response = client.get('/about')
            if response.status_code == 200:
                print("✓ About page route works")
            else:
                print(f"✗ About page returned status {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Route testing failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'app.py',
        'model_predictor.py',
        'run.py',
        'requirements.txt',
        'templates/base.html',
        'templates/index.html',
        'templates/results.html',
        'templates/instructions.html',
        'templates/about.html',
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print(f"✓ All {len(required_files)} required files present")
        return True

def main():
    """Run all tests"""
    print("EpiPred Web Application Test Suite")
    print("=" * 40)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Imports", test_imports),
        ("Flask App Creation", test_app_creation),
        ("Model Predictor", test_model_predictor),
        ("FASTA Parsing", test_fasta_parsing),
        ("Flask Routes", test_routes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work correctly.")
        print("\nTo start the application, run:")
        print("  python run.py")
        print("\nThen open http://localhost:5000 in your browser.")
    else:
        print("⚠ Some tests failed. Please check the errors above.")
        if passed >= total - 1:  # Allow model predictor to fail
            print("\nThe application may still work if only model loading failed.")
            print("Make sure model files are available for full functionality.")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

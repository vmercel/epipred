#!/usr/bin/env python3
"""
Test script for deployment compatibility
"""

import sys
import os

def test_basic_imports():
    """Test basic Python imports"""
    print("Testing basic imports...")
    
    try:
        import flask
        print(f"✓ Flask {flask.__version__}")
    except ImportError as e:
        print(f"✗ Flask: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✓ NumPy {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy: {e}")
        return False
    
    try:
        import pandas as pd
        print(f"✓ Pandas {pd.__version__}")
    except ImportError as e:
        print(f"✗ Pandas: {e}")
        return False
    
    return True

def test_tensorflow():
    """Test TensorFlow import"""
    print("\nTesting TensorFlow...")
    
    try:
        import tensorflow as tf
        print(f"✓ TensorFlow {tf.__version__}")
        return True
    except ImportError as e:
        print(f"⚠ TensorFlow not available: {e}")
        print("  App will run in demo mode")
        return False

def test_model_predictor():
    """Test model predictor"""
    print("\nTesting model predictor...")
    
    try:
        from model_predictor import EpitopePredictor
        predictor = EpitopePredictor()
        
        if predictor.model is None:
            print("⚠ Model not loaded - will use demo mode")
        else:
            print("✓ Model loaded successfully")
        
        # Test prediction with demo sequence
        test_seq = "MKLLILTCLVAVALARPKHPIKHQGLPQEVLNENLLRFFVAPFPEVFGKEKVNEL"
        b_epitopes, t_epitopes = predictor.predict_epitopes(test_seq)
        
        print(f"✓ Prediction test: {len(b_epitopes)} B-cell, {len(t_epitopes)} T-cell epitopes")
        return True
        
    except Exception as e:
        print(f"✗ Model predictor failed: {e}")
        return False

def test_flask_app():
    """Test Flask app creation"""
    print("\nTesting Flask app...")
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✓ Health endpoint working")
            else:
                print(f"⚠ Health endpoint returned {response.status_code}")
            
            # Test main page
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Main page working")
            else:
                print(f"⚠ Main page returned {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("EpiPred Deployment Test")
    print("=" * 30)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("TensorFlow", test_tensorflow),
        ("Model Predictor", test_model_predictor),
        ("Flask App", test_flask_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 30)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed >= 3:  # Allow TensorFlow to fail
        print("🎉 Deployment should work!")
        if passed < total:
            print("⚠ Some features may be limited (demo mode)")
    else:
        print("❌ Deployment may have issues")
    
    return passed >= 3

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

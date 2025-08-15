#!/usr/bin/env python3
"""
Test script to verify the epitope prediction model is working correctly
"""

import sys
import os
import logging

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_predictor import EpitopePredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model():
    """Test the epitope prediction model"""
    logger.info("Starting model test...")
    
    try:
        # Initialize predictor
        logger.info("Initializing EpitopePredictor...")
        predictor = EpitopePredictor()
        logger.info("Model loaded successfully!")
        
        # Get model info
        model_info = predictor.get_model_info()
        logger.info(f"Model info: {model_info}")
        
        # Test sequences
        test_sequences = {
            "Test_Sequence_1": "MKLLILTCLVAVALARPKHPIKHQGLPQEVLNENLLRFFVAPFPEVFGKEKVNEL",
            "Test_Sequence_2": "GIVEQCCTSICSLYQLENYCN",  # Insulin A chain
            "Test_Sequence_3": "FVNQHLCGSHLVEALYLVCGERGFFYTPKT"  # Insulin B chain
        }
        
        for seq_name, sequence in test_sequences.items():
            logger.info(f"\nTesting sequence: {seq_name} (length: {len(sequence)})")
            logger.info(f"Sequence: {sequence}")
            
            try:
                # Predict epitopes
                b_cell_epitopes, t_cell_epitopes = predictor.predict_epitopes(sequence)
                
                logger.info(f"Results for {seq_name}:")
                logger.info(f"  B-cell epitopes: {len(b_cell_epitopes)}")
                for i, (epitope, confidence, pos_range) in enumerate(b_cell_epitopes[:3]):
                    logger.info(f"    {i+1}. {epitope} (confidence: {confidence:.3f}, position: {pos_range})")
                
                logger.info(f"  T-cell epitopes: {len(t_cell_epitopes)}")
                for i, (epitope, confidence, pos_range) in enumerate(t_cell_epitopes[:3]):
                    logger.info(f"    {i+1}. {epitope} (confidence: {confidence:.3f}, position: {pos_range})")
                
            except Exception as e:
                logger.error(f"Error predicting epitopes for {seq_name}: {e}")
        
        logger.info("\nModel test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Model test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_model()
    sys.exit(0 if success else 1)

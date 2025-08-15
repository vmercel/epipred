#!/usr/bin/env python3
"""
Epitope Prediction Model Interface
Loads and uses the trained deep learning model for epitope prediction
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
import logging

# Optional imports for deployment compatibility
try:
    import sklearn
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available - some features may be limited")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EpitopePredictor:
    """
    Epitope prediction class that loads the trained model and performs predictions
    """
    
    def __init__(self, model_path=None):
        """
        Initialize the predictor with the trained model
        
        Args:
            model_path (str): Path to the model file. If None, uses default path.
        """
        # Amino acid to number mapping (same as used in training)
        self.amino_acid_to_num = {
            'A': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8,
            'K': 9, 'L': 10, 'M': 11, 'N': 12, 'P': 13, 'Q': 14, 'R': 15,
            'S': 16, 'T': 17, 'V': 18, 'W': 19, 'Y': 20, 'X': 0  # X for unknown
        }
        
        # Class mapping (same as used in training)
        self.class_mapping = {
            'B_cell_negative': 0,
            'B_cell_positive': 1,
            'T_cell_MHC_negative': 2,
            'T_cell_MHC_positive': 3
        }
        
        # Reverse mapping for predictions
        self.idx_to_class = {v: k for k, v in self.class_mapping.items()}
        
        # Model parameters
        self.window_size = 20
        self.step_size = 1
        self.confidence_threshold = 0.5
        
        # Load the model
        self.model = self._load_model(model_path)
        
    def _load_model(self, model_path=None):
        """
        Load the trained model
        
        Args:
            model_path (str): Path to model file
            
        Returns:
            tensorflow.keras.Model: Loaded model
        """
        if model_path is None:
            # Try different model formats in order of preference
            possible_paths = [
                'models/epitope_model.keras',
                'models/epitope_model.h5',
                'models/epitope_model_savedmodel',
                '../epitope_model.keras',
                '../epitope_model.h5',
                '../epitope_model_savedmodel',
                'epitope_model.keras',
                'epitope_model.h5',
                'epitope_model_savedmodel'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if model_path is None:
                raise FileNotFoundError("No trained model found. Please ensure the model file exists.")
        
        try:
            logger.info(f"Loading model from: {model_path}")

            if model_path.endswith('.keras') or model_path.endswith('.h5'):
                model = keras.models.load_model(model_path, compile=False)
            else:
                # Assume SavedModel format
                model = tf.saved_model.load(model_path)

            logger.info("Model loaded successfully")

            # Test the model with a dummy input to ensure it works
            try:
                dummy_input = np.array([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]])
                if hasattr(model, 'predict'):
                    _ = model.predict(dummy_input, verbose=0)
                else:
                    _ = model(dummy_input)
                logger.info("Model test prediction successful")
            except Exception as test_error:
                logger.warning(f"Model test failed: {test_error}")

            return model

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise RuntimeError(f"Failed to load model from {model_path}: {e}")
    
    def encode_sequence(self, sequence):
        """
        Encode amino acid sequence to numerical representation
        
        Args:
            sequence (str): Amino acid sequence
            
        Returns:
            list: Encoded sequence
        """
        return [self.amino_acid_to_num.get(aa.upper(), 0) for aa in sequence]
    
    def sliding_window_prediction(self, sequence):
        """
        Perform sliding window prediction on a protein sequence
        
        Args:
            sequence (str): Protein sequence
            
        Returns:
            tuple: (b_cell_epitopes, t_cell_epitopes) lists with (epitope, confidence, position_range)
        """
        logger.debug(f"Starting sliding window prediction for sequence of length {len(sequence)}")
        b_cell_epitopes = []
        t_cell_epitopes = []
        
        if len(sequence) < self.window_size:
            logger.warning(f"Sequence too short ({len(sequence)} < {self.window_size})")
            return b_cell_epitopes, t_cell_epitopes
        
        # Prepare batch data for efficient prediction
        subseq_list = []
        positions = []
        
        for i in range(0, len(sequence) - self.window_size + 1, self.step_size):
            sub_seq = sequence[i:i + self.window_size]
            encoded_sub_seq = self.encode_sequence(sub_seq)
            subseq_list.append(encoded_sub_seq)
            positions.append((i, i + self.window_size))
        
        if not subseq_list:
            logger.warning("No subsequences generated for prediction")
            return b_cell_epitopes, t_cell_epitopes
        
        logger.debug(f"Generated {len(subseq_list)} subsequences for prediction")
        
        # Convert to numpy array for batch prediction
        padded_subseq_array = np.array(subseq_list)
        
        try:
            logger.debug(f"Performing batch prediction on {padded_subseq_array.shape} array")
            
            # Perform batch predictions
            if hasattr(self.model, 'predict'):
                predicted_probs = self.model.predict(padded_subseq_array, batch_size=64, verbose=0)
            else:
                # For SavedModel format
                predicted_probs = self.model(padded_subseq_array).numpy()
            
            logger.debug(f"Model prediction completed, output shape: {predicted_probs.shape}")
            
            # Process predictions
            for i, (probs, (start_pos, end_pos)) in enumerate(zip(predicted_probs, positions)):
                predicted_class = np.argmax(probs)
                confidence = np.max(probs)
                predicted_label = self.idx_to_class[predicted_class]
                
                # Only include predictions above threshold
                if confidence >= self.confidence_threshold:
                    sub_seq = sequence[start_pos:end_pos]
                    pos_range = f"{start_pos+1}-{end_pos}"  # 1-based indexing for display
                    
                    if predicted_label == "B_cell_positive":
                        b_cell_epitopes.append((sub_seq, float(confidence), pos_range))
                    elif predicted_label == "T_cell_MHC_positive":
                        t_cell_epitopes.append((sub_seq, float(confidence), pos_range))
            
            logger.debug(f"Prediction processing completed: {len(b_cell_epitopes)} B-cell, {len(t_cell_epitopes)} T-cell epitopes above threshold")
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}")
            raise
        
        return b_cell_epitopes, t_cell_epitopes
    
    def predict_epitopes(self, sequence, threshold=None):
        """
        Main prediction function
        
        Args:
            sequence (str): Protein sequence
            threshold (float): Confidence threshold (optional)
            
        Returns:
            tuple: (b_cell_epitopes, t_cell_epitopes)
        """
        logger.info(f"Starting epitope prediction for sequence of length {len(sequence)}")
        
        if threshold is not None:
            original_threshold = self.confidence_threshold
            self.confidence_threshold = threshold
            logger.debug(f"Using custom threshold: {threshold}")
        
        try:
            # Clean the sequence
            clean_sequence = ''.join(c.upper() for c in sequence if c.upper() in self.amino_acid_to_num)
            
            if len(clean_sequence) != len(sequence):
                logger.warning(f"Sequence contained invalid characters. Cleaned: {len(sequence)} -> {len(clean_sequence)}")
            
            # Perform prediction
            b_cell_epitopes, t_cell_epitopes = self.sliding_window_prediction(clean_sequence)
            
            # Sort by confidence (highest first)
            b_cell_epitopes.sort(key=lambda x: x[1], reverse=True)
            t_cell_epitopes.sort(key=lambda x: x[1], reverse=True)
            
            logger.info(f"Prediction completed: {len(b_cell_epitopes)} B-cell, {len(t_cell_epitopes)} T-cell epitopes found")
            
            return b_cell_epitopes, t_cell_epitopes
            
        finally:
            if threshold is not None:
                self.confidence_threshold = original_threshold
    
    def get_sequence_markup(self, sequence, epitopes, epitope_type='B-cell'):
        """
        Generate sequence markup for visualization
        
        Args:
            sequence (str): Original sequence
            epitopes (list): List of epitopes with positions
            epitope_type (str): Type of epitopes ('B-cell' or 'T-cell')
            
        Returns:
            str: Marked up sequence
        """
        markup = ['.' for _ in sequence]  # Default to non-epitope
        
        for epitope, confidence, pos_range in epitopes:
            start, end = map(int, pos_range.split('-'))
            start -= 1  # Convert to 0-based indexing
            end -= 1
            
            # Mark epitope positions
            marker = 'E' if epitope_type == 'B-cell' else 'T'
            for i in range(start, min(end + 1, len(markup))):
                markup[i] = marker
        
        return ''.join(markup)
    
    def set_confidence_threshold(self, threshold):
        """
        Set the confidence threshold for predictions
        
        Args:
            threshold (float): New threshold value (0.0 to 1.0)
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
        else:
            raise ValueError("Threshold must be between 0.0 and 1.0")
    
    def get_model_info(self):
        """
        Get information about the loaded model
        
        Returns:
            dict: Model information
        """
        info = {
            'window_size': self.window_size,
            'step_size': self.step_size,
            'confidence_threshold': self.confidence_threshold,
            'classes': list(self.class_mapping.keys()),
            'amino_acids': list(self.amino_acid_to_num.keys())
        }
        
        if hasattr(self.model, 'summary'):
            try:
                # Get model summary as string
                import io
                import sys
                old_stdout = sys.stdout
                sys.stdout = buffer = io.StringIO()
                self.model.summary()
                sys.stdout = old_stdout
                info['model_summary'] = buffer.getvalue()
            except:
                info['model_summary'] = "Model summary not available"
        
        return info

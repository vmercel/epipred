#!/usr/bin/env python3
"""
Epitope Prediction Web Tool
Similar to BepiPred-2.0 for B-cell and T-cell epitope prediction
"""

import os
import json
import uuid
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
from io import StringIO, BytesIO
import tempfile

# Import our custom prediction module
from model_predictor import EpitopePredictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('epitope_prediction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize the predictor with error handling
predictor = None
try:
    logger.info("Initializing EpitopePredictor...")
    predictor = EpitopePredictor()
    logger.info("Model loaded successfully")
    
    # Log model information
    model_info = predictor.get_model_info()
    logger.info(f"Model configuration: {model_info}")
    
except Exception as e:
    logger.error(f"Failed to load model: {e}")
    predictor = None

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'fasta', 'fa', 'fas'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with sequence input interface"""
    logger.info("Serving main page")
    return render_template('index.html')

@app.route('/instructions')
def instructions():
    """Instructions page"""
    logger.info("Serving instructions page")
    return render_template('instructions.html')

@app.route('/about')
def about():
    """About page with method information"""
    logger.info("Serving about page")
    return render_template('about.html')

@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    from datetime import datetime
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': predictor is not None,
        'version': '1.0.0'
    })

@app.route('/status')
def status():
    """System status endpoint for monitoring"""
    logger.info("Status check requested")
    
    status_info = {
        'model_loaded': predictor is not None,
        'timestamp': datetime.now().isoformat(),
        'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER'])
    }
    
    if predictor:
        try:
            model_info = predictor.get_model_info()
            status_info.update({
                'model_info': model_info,
                'model_ready': True
            })
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            status_info.update({
                'model_ready': False,
                'model_error': str(e)
            })
    else:
        status_info.update({
            'model_ready': False,
            'model_error': 'Model not loaded'
        })
    
    logger.info(f"Status check result: {status_info}")
    return jsonify(status_info)

@app.route('/predict', methods=['POST'])
def predict():
    """Handle sequence prediction requests"""
    logger.info("Received prediction request")
    
    # Check if predictor is available
    if predictor is None:
        logger.error("Prediction service is unavailable - model not loaded")
        flash('Prediction service is currently unavailable. Please check that the model files are properly installed.', 'error')
        return redirect(url_for('index'))

    try:
        # Get input data
        sequence_text = request.form.get('sequence_text', '').strip()
        uploaded_file = request.files.get('sequence_file')
        
        logger.info(f"Input - Text: {len(sequence_text)} chars, File: {'Yes' if uploaded_file and uploaded_file.filename else 'No'}")

        sequences = {}

        # Process text input
        if sequence_text:
            try:
                logger.info("Parsing sequence text input")
                sequences.update(parse_fasta_text(sequence_text))
                logger.info(f"Parsed {len(sequences)} sequences from text input")
            except Exception as e:
                logger.error(f"Error parsing sequence text: {str(e)}")
                flash(f'Error parsing sequence text: {str(e)}', 'error')
                return redirect(url_for('index'))

        # Process uploaded file
        if uploaded_file and uploaded_file.filename != '' and allowed_file(uploaded_file.filename):
            try:
                filename = secure_filename(uploaded_file.filename)
                file_content = uploaded_file.read().decode('utf-8')
                logger.info(f"Processing uploaded file: {filename} ({len(file_content)} chars)")
                
                file_sequences = parse_fasta_text(file_content)
                sequences.update(file_sequences)
                logger.info(f"Parsed {len(file_sequences)} sequences from uploaded file")
            except UnicodeDecodeError:
                logger.error("Unicode decode error when reading uploaded file")
                flash('Error reading file. Please ensure the file is in text format with UTF-8 encoding.', 'error')
                return redirect(url_for('index'))
            except Exception as e:
                logger.error(f"Error processing uploaded file: {str(e)}")
                flash(f'Error processing uploaded file: {str(e)}', 'error')
                return redirect(url_for('index'))

        if not sequences:
            logger.warning("No sequences provided in request")
            flash('Please provide protein sequences in FASTA format.', 'error')
            return redirect(url_for('index'))

        logger.info(f"Total sequences to process: {len(sequences)}")

        # Validate sequences
        validation_errors = validate_sequences(sequences)
        if validation_errors:
            logger.warning(f"Sequence validation failed: {len(validation_errors)} errors")
            for error in validation_errors:
                logger.warning(f"Validation error: {error}")
                flash(error, 'error')
            return redirect(url_for('index'))
        
        logger.info("Sequence validation passed")
        
        # Generate job ID
        job_id = str(uuid.uuid4())
        logger.info(f"Generated job ID: {job_id}")
        
        # Perform predictions
        results = {}
        failed_sequences = []

        for seq_name, seq in sequences.items():
            try:
                logger.info(f"Predicting epitopes for sequence: {seq_name} (length: {len(seq)})")
                
                # Call the model predictor
                b_cell_epitopes, t_cell_epitopes = predictor.predict_epitopes(seq)
                
                logger.info(f"Prediction completed for {seq_name}: {len(b_cell_epitopes)} B-cell, {len(t_cell_epitopes)} T-cell epitopes")
                
                results[seq_name] = {
                    'sequence': seq,
                    'b_cell_epitopes': b_cell_epitopes,
                    't_cell_epitopes': t_cell_epitopes,
                    'length': len(seq)
                }
                
                # Log detailed results
                if b_cell_epitopes:
                    logger.info(f"B-cell epitopes for {seq_name}: {[(ep[0], f'{ep[1]:.3f}', ep[2]) for ep in b_cell_epitopes[:3]]}")
                if t_cell_epitopes:
                    logger.info(f"T-cell epitopes for {seq_name}: {[(ep[0], f'{ep[1]:.3f}', ep[2]) for ep in t_cell_epitopes[:3]]}")
                
            except Exception as e:
                logger.error(f"Prediction failed for sequence {seq_name}: {e}")
                failed_sequences.append(seq_name)

        # Check if any predictions succeeded
        if not results:
            logger.error("All predictions failed")
            flash('Prediction failed for all sequences. Please check your input and try again.', 'error')
            return redirect(url_for('index'))

        logger.info(f"Prediction completed successfully for {len(results)} sequences")

        # Warn about failed sequences
        if failed_sequences:
            logger.warning(f"Prediction failed for {len(failed_sequences)} sequences: {failed_sequences}")
            flash(f'Prediction failed for {len(failed_sequences)} sequence(s): {", ".join(failed_sequences[:3])}{"..." if len(failed_sequences) > 3 else ""}', 'warning')
        
        # Store results (in production, use a database)
        results_data = {
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'total_sequences': len(sequences),
            'model_info': predictor.get_model_info() if predictor else {}
        }
        
        # Save results to temporary file
        results_file = os.path.join(app.config['UPLOAD_FOLDER'], f'{job_id}_results.json')
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Results saved to: {results_file}")
        logger.info(f"Prediction request completed successfully for job: {job_id}")
        
        return render_template('results.html', 
                             job_id=job_id, 
                             results=results_data,
                             enumerate=enumerate)
    
    except Exception as e:
        logger.error(f"Unexpected error during prediction: {str(e)}")
        flash(f'An error occurred during prediction: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<job_id>/<format>')
def download_results(job_id, format):
    """Download results in specified format"""
    logger.info(f"Download request - Job ID: {job_id}, Format: {format}")
    
    try:
        results_file = os.path.join(app.config['UPLOAD_FOLDER'], f'{job_id}_results.json')
        
        if not os.path.exists(results_file):
            logger.warning(f"Results file not found: {results_file}")
            flash('Results not found or expired.', 'error')
            return redirect(url_for('index'))
        
        with open(results_file, 'r') as f:
            results_data = json.load(f)
        
        logger.info(f"Generating {format.upper()} download for job {job_id}")
        
        if format.lower() == 'csv':
            return download_csv(results_data, job_id)
        elif format.lower() == 'json':
            return download_json(results_data, job_id)
        else:
            logger.warning(f"Invalid download format requested: {format}")
            flash('Invalid download format.', 'error')
            return redirect(url_for('index'))
    
    except Exception as e:
        logger.error(f"Error downloading results for job {job_id}: {str(e)}")
        flash(f'Error downloading results: {str(e)}', 'error')
        return redirect(url_for('index'))

def parse_fasta_text(text):
    """Parse FASTA format text and return dictionary of sequences"""
    logger.debug("Parsing FASTA text input")
    sequences = {}
    current_name = None
    current_seq = []
    
    for line in text.strip().split('\n'):
        line = line.strip()
        if line.startswith('>'):
            if current_name and current_seq:
                sequences[current_name] = ''.join(current_seq)
            current_name = line[1:].strip() or f"Sequence_{len(sequences)+1}"
            current_seq = []
        elif line and current_name:
            # Remove any non-amino acid characters
            clean_seq = ''.join(c.upper() for c in line if c.upper() in 'ACDEFGHIKLMNPQRSTVWY')
            current_seq.append(clean_seq)
    
    if current_name and current_seq:
        sequences[current_name] = ''.join(current_seq)
    
    logger.debug(f"Parsed {len(sequences)} sequences from FASTA text")
    return sequences

def validate_sequences(sequences):
    """Validate input sequences"""
    logger.debug(f"Validating {len(sequences)} sequences")
    errors = []
    
    if len(sequences) > 50:
        errors.append("Maximum 50 sequences allowed per submission.")
    
    total_length = sum(len(seq) for seq in sequences.values())
    if total_length > 300000:
        errors.append("Total sequence length exceeds 300,000 amino acids.")
    
    for name, seq in sequences.items():
        if len(seq) < 10:
            errors.append(f"Sequence '{name}' is too short (minimum 10 amino acids).")
        elif len(seq) > 6000:
            errors.append(f"Sequence '{name}' is too long (maximum 6000 amino acids).")
        
        # Check for invalid characters
        valid_aa = set('ACDEFGHIKLMNPQRSTVWY')
        invalid_chars = set(seq.upper()) - valid_aa
        if invalid_chars:
            errors.append(f"Sequence '{name}' contains invalid characters: {', '.join(invalid_chars)}")
    
    if errors:
        logger.warning(f"Sequence validation failed with {len(errors)} errors")
    else:
        logger.debug("Sequence validation passed")
    
    return errors

def download_csv(results_data, job_id):
    """Generate CSV download"""
    logger.info(f"Generating CSV download for job {job_id}")
    rows = []
    
    for seq_name, data in results_data['results'].items():
        # B-cell epitopes
        for epitope, confidence, pos_range in data['b_cell_epitopes']:
            rows.append({
                'Sequence_Name': seq_name,
                'Epitope_Type': 'B-cell',
                'Epitope_Sequence': epitope,
                'Confidence': confidence,
                'Position_Range': pos_range,
                'Full_Sequence': data['sequence']
            })
        
        # T-cell epitopes
        for epitope, confidence, pos_range in data['t_cell_epitopes']:
            rows.append({
                'Sequence_Name': seq_name,
                'Epitope_Type': 'T-cell',
                'Epitope_Sequence': epitope,
                'Confidence': confidence,
                'Position_Range': pos_range,
                'Full_Sequence': data['sequence']
            })
    
    df = pd.DataFrame(rows)
    logger.info(f"Generated CSV with {len(rows)} epitope predictions")
    
    # Create CSV in memory
    output = StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Convert to bytes
    mem = BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    
    return send_file(mem, 
                     as_attachment=True, 
                     download_name=f'epitope_predictions_{job_id}.csv',
                     mimetype='text/csv')

def download_json(results_data, job_id):
    """Generate JSON download"""
    logger.info(f"Generating JSON download for job {job_id}")
    mem = BytesIO()
    mem.write(json.dumps(results_data, indent=2).encode('utf-8'))
    mem.seek(0)
    
    return send_file(mem,
                     as_attachment=True,
                     download_name=f'epitope_predictions_{job_id}.json',
                     mimetype='application/json')

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    logger.info(f"Upload directory created/verified: {app.config['UPLOAD_FOLDER']}")
    
    # Log startup information
    logger.info("Starting EpiPred web application")
    logger.info(f"Model status: {'Loaded' if predictor else 'Failed to load'}")
    
    if predictor:
        model_info = predictor.get_model_info()
        logger.info(f"Model ready - Window size: {model_info['window_size']}, Threshold: {model_info['confidence_threshold']}")
    
    # Run the application
    logger.info("Starting Flask development server on 0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

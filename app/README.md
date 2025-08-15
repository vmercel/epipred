# EpiPred - Epitope Prediction Web Tool

A web-based tool for predicting B-cell and T-cell epitopes from protein sequences using advanced deep learning with attention mechanisms and bidirectional LSTM networks.

## Features

- **Advanced Deep Learning**: Attention-based neural networks with bidirectional LSTM
- **Multi-target Prediction**: Both B-cell and T-cell epitope prediction
- **Interactive Interface**: User-friendly web interface similar to BepiPred-2.0
- **Flexible Input**: Support for text input and file upload (FASTA format)
- **Real-time Visualization**: Interactive sequence markup and confidence scoring
- **Multiple Export Formats**: Download results in CSV or JSON format
- **Responsive Design**: Works on desktop and mobile devices

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the application files**
   ```bash
   cd app/
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure model files are available**

   The application looks for trained model files in the following locations (in order of preference):
   - `models/epitope_model.keras`
   - `models/epitope_model.h5`
   - `models/epitope_model_savedmodel/`
   - `../epitope_model.keras`
   - `../epitope_model.h5`
   - `../epitope_model_savedmodel/`
   - `epitope_model.keras`
   - `epitope_model.h5`
   - `epitope_model_savedmodel/`

   The model files should be placed in the `models/` directory within the app folder.

4. **Run the application**
   ```bash
   python run.py
   ```
   
   Or alternatively:
   ```bash
   python app.py
   ```

5. **Access the web interface**
   
   Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### Input Formats

The tool accepts protein sequences in FASTA format:

```
>Sequence_Name_1
MKLLILTCLVAVALARPKHPIKHQGLPQEVLNENLLRFFVAPFPEVFGKEKVNEL

>Sequence_Name_2  
CARFASLIYGKFVRQPQVWLRIQNYSVMDICDEHQGVMVPGVGVPQALQKYNPD
```

### Submission Limits

- **Maximum sequences**: 50 per submission
- **Maximum total length**: 300,000 amino acids
- **Sequence length range**: 10-6,000 amino acids each
- **File size limit**: 16 MB

### Input Methods

1. **Text Input**: Paste sequences directly into the text area
2. **File Upload**: Upload FASTA files (.txt, .fasta, .fa, .fas)

### Results Interpretation

- **Confidence Scores**: Range from 0.0 to 1.0 (higher = more confident)
- **Sequence Markup**: 
  - `B` = B-cell epitope regions
  - `T` = T-cell epitope regions  
  - `.` = Non-epitope regions
- **Interactive Threshold**: Adjust confidence threshold to filter results
- **Position Ranges**: 1-based indexing (first amino acid = position 1)

## Configuration

### Environment Variables

- `FLASK_DEBUG`: Set to 'true' for debug mode (default: false)
- `FLASK_HOST`: Host address (default: 0.0.0.0)
- `FLASK_PORT`: Port number (default: 5000)

### Example

```bash
export FLASK_DEBUG=true
export FLASK_PORT=8080
python run.py
```

## Sample Input Files

Two sample FASTA files are provided for testing:

1. **`test_sequences.fasta`** - Small test file with 3 sequences (good for quick testing)
2. **`sample_input.fasta`** - Larger sample with 10 diverse protein sequences including:
   - Human Insulin chains
   - Viral proteins (SARS-CoV-2, HIV, Influenza, Zika)
   - Bacterial antigens (Tuberculosis, Hepatitis B)
   - Cancer-related proteins (p53)
   - Parasitic proteins (Malaria)

### How to Use Sample Files:

1. **Via Web Interface:**
   - Go to http://localhost:5000
   - Click "Upload a FASTA file"
   - Select either `test_sequences.fasta` or `sample_input.fasta`
   - Click "Predict Epitopes"

2. **Copy and Paste:**
   - Open either sample file in a text editor
   - Copy the contents
   - Paste into the text area on the web interface
   - Click "Predict Epitopes"

## File Structure

```
app/
├── app.py                 # Main Flask application
├── model_predictor.py     # Model loading and prediction logic
├── run.py                 # Application launcher
├── test_app.py           # Test script
├── start.sh              # Linux/Mac startup script
├── start.bat             # Windows startup script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── test_sequences.fasta  # Small test file
├── sample_input.fasta    # Larger sample file
├── models/               # Model files directory
│   ├── epitope_model.keras
│   ├── epitope_model.h5
│   └── epitope_model_savedmodel/
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── results.html
│   ├── instructions.html
│   └── about.html
└── static/               # Static files
    ├── css/
    │   └── style.css
    ├── js/
    │   └── main.js
    └── uploads/          # Temporary file storage
```

## API Endpoints

- `GET /` - Main page
- `POST /predict` - Submit sequences for prediction
- `GET /instructions` - Usage instructions
- `GET /about` - Method information
- `GET /download/<job_id>/<format>` - Download results

## Troubleshooting

### Common Issues

1. **Model not found error**
   - Ensure model files are in the correct location
   - Check file permissions

2. **Import errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

3. **Memory errors**
   - Reduce batch size for large sequences
   - Process fewer sequences at once

4. **Port already in use**
   - Change port: `export FLASK_PORT=8080`
   - Or kill existing process

### Performance Tips

- Use smaller batch sizes for very long sequences
- Consider using GPU acceleration for TensorFlow if available
- Limit concurrent users in production environments

## Development

### Adding New Features

1. **Backend**: Modify `app.py` and `model_predictor.py`
2. **Frontend**: Update templates and static files
3. **Styling**: Modify `static/css/style.css`
4. **JavaScript**: Update `static/js/main.js`

### Testing

```bash
# Test with example sequences
curl -X POST http://localhost:5000/predict \
  -F "sequence_text=>Test\nMKLLILTCLVAVALARPKHPIKHQGLPQEVLNENLLRFFVAPFPEVFGKEKVNEL"
```

## License

This project is provided as-is for research and educational purposes.

## Support

For technical issues or questions about the method, please refer to:
- Instructions page in the web interface
- About page for method details
- This README file for setup help

## Citation

If you use EpiPred in your research, please cite:

```
EpiPred: Advanced Epitope Prediction Using Attention-based Deep Learning.
Bioinformatics and Computational Biology (2024)
DOI: 10.xxxx/xxxxxx
```

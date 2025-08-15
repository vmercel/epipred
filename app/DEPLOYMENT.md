# EpiPred Deployment Guide

## 🚀 Render.com Deployment

### Quick Deploy Steps:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy EpiPred to Render"
   git push origin main
   ```

2. **Connect to Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing your EpiPred app

3. **Configure Service:**
   - **Name:** `epitope-predictor`
   - **Environment:** `Python`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements-minimal.txt`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 wsgi:app`
   - **Python Version:** `3.12.0`

4. **Environment Variables:**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=false
   PYTHON_VERSION=3.12.0
   ```

5. **Deploy:** Click "Create Web Service"

### Alternative: Use render.yaml

If you have `render.yaml` in your repository, Render will automatically use it:

```yaml
services:
  - type: web
    name: epitope-predictor
    env: python
    plan: free
    buildCommand: |
      pip install --upgrade pip
      pip install -r requirements-minimal.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --timeout 300 --workers 1 wsgi:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      - key: FLASK_ENV
        value: production
```

## 🐳 Docker Deployment

### Create Dockerfile:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-minimal.txt .
RUN pip install --no-cache-dir -r requirements-minimal.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p static/uploads

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "300", "wsgi:app"]
```

### Build and Run:

```bash
docker build -t epipred .
docker run -p 5000:5000 epipred
```

## ☁️ Heroku Deployment

### Setup:

1. **Install Heroku CLI**
2. **Login:** `heroku login`
3. **Create app:** `heroku create your-app-name`
4. **Set Python version:** Ensure `runtime.txt` contains `python-3.12.0`
5. **Deploy:**
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Heroku Configuration:

```bash
heroku config:set FLASK_ENV=production
heroku config:set FLASK_DEBUG=false
```

## 🔧 Troubleshooting Deployment Issues

### Common Problems:

1. **Scikit-learn compilation errors:**
   - Use `requirements-minimal.txt` instead of `requirements.txt`
   - Remove scikit-learn dependency if not essential

2. **TensorFlow size issues:**
   - Use `tensorflow-cpu` instead of `tensorflow`
   - Consider using TensorFlow Lite for smaller deployments

3. **Memory issues:**
   - Reduce model size or use model quantization
   - Limit concurrent requests with gunicorn workers

4. **Build timeout:**
   - Use pre-compiled wheels
   - Remove unnecessary dependencies
   - Use Docker with cached layers

### Memory Optimization:

```python
# In model_predictor.py, add memory management
import gc
import tensorflow as tf

# After model loading
tf.keras.backend.clear_session()
gc.collect()
```

### Performance Settings:

```bash
# Gunicorn configuration for production
gunicorn --bind 0.0.0.0:$PORT \
         --timeout 300 \
         --workers 1 \
         --max-requests 1000 \
         --max-requests-jitter 100 \
         --preload \
         wsgi:app
```

## 📊 Monitoring

### Health Check Endpoint:

Add to your Flask app:

```python
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}
```

### Logging Configuration:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🔒 Security Considerations

1. **Environment Variables:**
   - Set `SECRET_KEY` in production
   - Use environment-specific configurations

2. **File Uploads:**
   - Validate file types and sizes
   - Use temporary storage for uploads
   - Clean up uploaded files regularly

3. **Rate Limiting:**
   - Consider adding rate limiting for API endpoints
   - Monitor resource usage

## 📝 Deployment Checklist

- [ ] Model files are in `models/` directory
- [ ] `requirements-minimal.txt` is used for deployment
- [ ] `wsgi.py` is configured as entry point
- [ ] Environment variables are set
- [ ] Health check endpoint is working
- [ ] File upload directory is writable
- [ ] Logging is configured
- [ ] Error handling is in place
- [ ] Security settings are applied

## 🎯 Production Recommendations

1. **Use a CDN** for static files
2. **Enable HTTPS** (Render provides this automatically)
3. **Set up monitoring** and alerting
4. **Regular backups** of any persistent data
5. **Performance testing** with expected load
6. **Error tracking** (e.g., Sentry)

Your EpiPred application should now be ready for production deployment! 🚀

# Face Recognition API 🔍

> **⚠️ PROPRIETARY SOFTWARE NOTICE ⚠️**  
> This is proprietary software owned by **Tekly IT Solutions**.  
> Commercial use requires a valid license. Contact Tekly IT Solutions for licensing.

A robust, real-time face verification system with camera integration, built using deep learning technologies including RetinaFace for detection, ArcFace (InsightFace) for embeddings, and FAISS for fast similarity search.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-green.svg)](https://opencv.org)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

## 🚀 Features

- **Real-time Face Detection**: Uses RetinaFace for accurate face localization
- **Face Embedding**: ArcFace (InsightFace) for robust 512-dimensional face embeddings
- **Fast Search**: FAISS for efficient similarity search across large datasets
- **Camera Integration**: Real-time verification and live mode with webcam
- **Data Augmentation**: Automatic image augmentation for better training
- **Quality Control**: Built-in image quality validation
- **Model Persistence**: Save and load trained models with FAISS indices
- **Interactive CLI**: Menu-driven interface for verification and management
- **Modular Architecture**: Clean, maintainable code structure

## 📋 Requirements

- Python 3.8+
- Webcam (for camera features)
- At least 4GB RAM (recommended 8GB+)
- GPU support (optional, for faster processing)

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Tekly-Solutions/Face-Recognition-API.git
cd Face-Recognition-API
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Additional Requirements (if needed)

```bash
# For GPU support (optional)
pip install onnxruntime-gpu

# For CUDA support (optional)
pip install mxnet-cu112  # Replace with your CUDA version
```

## 📁 Project Structure

```
Face-Recognition-API/
│
├── config/                  # Configuration files
│   ├── config.py           # Main configuration
│   └── settings.yaml       # YAML settings
│
├── dataset/                 # Face dataset (organize by person)
│   ├── person1/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   └── person2/
│       ├── img1.jpg
│       └── img2.jpg
│
├── models/                  # Trained models (auto-generated)
│   ├── enhanced_face_model.pkl
│   └── enhanced_face_index.faiss
│
├── src/                     # Source code
│   ├── api/                # API endpoints
│   ├── core/               # Core functionality
│   ├── services/           # Business logic
│   └── utils/              # Utilities
│
├── scripts/                 # Training and management scripts
├── tests/                   # Test files
├── main.py                  # Main application entry point
└── requirements.txt         # Python dependencies
```

## 🎯 Quick Start

### 1. Prepare Your Dataset

Organize your face images in the following structure:

```
dataset/
├── john_doe/
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── photo3.jpg
├── jane_smith/
│   ├── image1.jpg
│   └── image2.jpg
```

**Tips for good results:**

- Use 3-5 clear photos per person
- Ensure faces are well-lit and clearly visible
- Include different angles and expressions
- Use high-quality images (minimum 640×640)

### 2. Train the Model

```bash
python scripts/train_model.py
```

Or use interactive training:

```bash
python scripts/interactive_training.py
```

### 3. Run the Application

```bash
python main.py
```

### 4. Use the Interactive Menu

```
🎯 ENHANCED MENU:
1. 🔍 Verify single image file
2. 📊 Get top 5 matches
3. 📷 Capture & Verify (Camera)
4. 🎥 Live Verification Mode
5. ⚙️ Change threshold
6. 📈 System info
7. 🚪 Exit
```

## 📖 Detailed Usage

### Training Options

```bash
# Basic training
python scripts/train_model.py

# Training with custom options
python scripts/train_model.py --dataset /path/to/dataset --threshold 0.7

# Training without augmentation
python scripts/train_model.py --no-augmentation

# Training with custom augmentation count
python scripts/train_model.py --augmentations 5
```

### Camera Features

#### Live Verification Mode

- Real-time face detection and verification
- Visual feedback with confidence scores
- Press ESC to exit

#### Capture & Verify

- Position face in frame
- Press SPACE to capture
- Automatic verification of captured image

### API Usage (Future Feature)

```python
from src.services.verification_service import FaceVerificationSystem

# Initialize system
system = FaceVerificationSystem()
system.load_model()

# Verify a face
result, confidence = system.verify_face("path/to/image.jpg")
print(f"Person: {result}, Confidence: {confidence:.3f}")
```

## ⚙️ Configuration

Edit `config/config.py` to customize:

```python
@dataclass
class ModelConfig:
    detection_size: Tuple[int, int] = (160, 160)  # Face detection size
    threshold: float = 0.6                        # Verification threshold

@dataclass
class CameraConfig:
    frame_width: int = 640                        # Camera resolution
    frame_height: int = 480
    fps: int = 30

@dataclass
class DatasetConfig:
    dataset_path: str = "dataset"                 # Dataset location
    supported_formats: tuple = ('.jpg', '.jpeg', '.png', '.bmp')
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/unit/
python -m pytest tests/integration/

# Run with coverage
python -m pytest tests/ --cov=src/
```

## 📊 Model Performance

### Accuracy Metrics

- **Face Detection**: RetinaFace with >95% accuracy
- **Face Recognition**: ArcFace embeddings with cosine similarity
- **Speed**: Real-time processing at 30+ FPS (with GPU)

### Supported Image Formats

- JPEG, PNG, BMP
- Minimum resolution: 80×80 pixels
- Recommended: 640×640 or higher

## 🚀 Deployment Options

### Docker Deployment

```bash
# Build Docker image
docker build -t face-recognition-api .

# Run container
docker run -p 8000:8000 face-recognition-api
```

### Cloud Deployment

- **Google Colab**: For experimentation and demos
- **AWS/Azure/GCP**: For production deployment
- **Docker**: For containerized deployment

## 🔧 Troubleshooting

### Common Issues

**1. "ImportError: No module named 'insightface'"**

```bash
pip install insightface
```

**2. "CUDA out of memory"**

- Reduce `detection_size` in config
- Use CPU mode: Set `ctx_id=-1` in embedding service

**3. "No faces detected"**

- Ensure images are well-lit and faces are clearly visible
- Check image quality (not blurry, good resolution)
- Verify face is facing forward

**4. "Low accuracy"**

- Add more training images per person (3-5 recommended)
- Use higher quality images
- Adjust verification threshold

### Performance Optimization

**For faster processing:**

- Use GPU acceleration
- Reduce image resolution
- Optimize detection parameters

**For better accuracy:**

- Use more training images
- Enable data augmentation
- Fine-tune threshold values

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install

# Run linting
flake8 src/
black src/

# Run type checking
mypy src/
```

## 📝 License

**PROPRIETARY SOFTWARE - NOT OPEN SOURCE**

This Face Recognition API is proprietary software owned by **Tekly IT Solutions**.

⚠️ **IMPORTANT NOTICE**: This software is NOT licensed under MIT, Apache, GPL, or any other open-source license.

**Usage Requirements:**

- Commercial use requires a valid license agreement with Tekly IT Solutions
- Unauthorized use, copying, or distribution is strictly prohibited
- For licensing inquiries, contact: **Tekly IT Solutions**

See the [LICENSE](LICENSE) file for complete terms and conditions.

## 🙏 Acknowledgments

- **RetinaFace**: For robust face detection
- **InsightFace**: For high-quality face embeddings
- **FAISS**: For efficient similarity search
- **OpenCV**: For image processing capabilities

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Tekly-Solutions/Face-Recognition-API/issues)
- **Documentation**: [Wiki](https://github.com/Tekly-Solutions/Face-Recognition-API/wiki)
- **Email**: support@tekly-solutions.com

## 🔄 Changelog

### v1.0.0 (Current)

- Initial release
- Real-time face verification
- Camera integration
- Model training pipeline
- Interactive CLI interface

---

**Made with ❤️ by Tekly Solutions**

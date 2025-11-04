import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

function Train({ apiBaseUrl, onError, onSuccess }) {
  const [personName, setPersonName] = useState("");
  const [images, setImages] = useState([]); // { file, preview }
  const [loading, setLoading] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const newImages = files.map((file) => ({
      file,
      preview: URL.createObjectURL(file),
    }));
    setImages((prev) => [...prev, ...newImages]);
  };

  const convertToBase64 = async (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
    });
  };

  const handleTrain = async () => {
    if (!personName.trim()) {
      onError(new Error("Person name is required"));
      return;
    }
    if (images.length === 0) {
      onError(new Error("At least one image is required"));
      return;
    }

    setLoading(true);
    try {
      const base64Images = await Promise.all(
        images.map((img) => convertToBase64(img.file))
      );

      const response = await axios.post(`${apiBaseUrl}/train`, {
        person_name: personName,
        images: base64Images,
      });

      onSuccess(
        `Successfully trained ${response.data.person_name} with ${
          response.data.images_saved || base64Images.length
        } images`
      );
      setPersonName("");
      setImages([]);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      onError(err);
    } finally {
      setLoading(false);
    }
  };

  const removeImage = (index) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  const startCamera = async () => {
    if (cameraActive) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setCameraActive(true);
    } catch (err) {
      onError(err);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setCameraActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const canvas = canvasRef.current || document.createElement("canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        // Create a File from blob so existing code works
        const file = new File([blob], `capture_${Date.now()}.jpg`, {
          type: "image/jpeg",
        });
        const preview = URL.createObjectURL(blob);
        setImages((prev) => [...prev, { file, preview }]);
      },
      "image/jpeg",
      0.9
    );
  };

  useEffect(() => {
    // cleanup on unmount
    return () => {
      stopCamera();
      // revoke object URLs
      images.forEach((img) => {
        try {
          URL.revokeObjectURL(img.preview);
        } catch (e) {}
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="component-container">
      <h2>📸 Train New Face</h2>

      <div className="form-group">
        <label>Person Name:</label>
        <input
          type="text"
          value={personName}
          onChange={(e) => setPersonName(e.target.value)}
          placeholder="Enter person's name"
          className="input"
        />
      </div>

      <div className="form-group">
        <label>Upload Images:</label>
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          ref={fileInputRef}
          className="file-input"
        />
        <p className="text-muted">
          Select or capture 3-5 clear front-facing photos for best results
        </p>
      </div>

      <div className="form-group">
        <label>Capture from camera:</label>
        <div className="camera-controls">
          {!cameraActive ? (
            <button className="btn" onClick={startCamera}>
              Open Camera
            </button>
          ) : (
            <>
              <video
                ref={videoRef}
                autoPlay
                muted
                playsInline
                style={{ maxWidth: "320px", borderRadius: 6 }}
              />
              <div style={{ marginTop: 8 }}>
                <button className="btn btn-primary" onClick={capturePhoto}>
                  Capture
                </button>
                <button
                  className="btn"
                  onClick={stopCamera}
                  style={{ marginLeft: 8 }}
                >
                  Close Camera
                </button>
              </div>
            </>
          )}
        </div>
        {/* hidden canvas used for capture if needed */}
        <canvas ref={canvasRef} style={{ display: "none" }} />
      </div>

      {images.length > 0 && (
        <div className="image-gallery">
          <h4>Selected Images ({images.length}):</h4>
          <div className="gallery-grid">
            {images.map((img, index) => (
              <div key={index} className="gallery-item">
                <img src={img.preview} alt={`Preview ${index}`} />
                <button
                  className="remove-btn"
                  onClick={() => removeImage(index)}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={handleTrain}
        disabled={loading || !personName.trim() || images.length === 0}
        className="btn btn-primary"
      >
        {loading ? "🔄 Training..." : "✅ Train Face"}
      </button>
    </div>
  );
}

export default Train;

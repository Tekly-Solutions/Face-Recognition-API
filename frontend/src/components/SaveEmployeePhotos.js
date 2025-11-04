import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

function SaveEmployeePhotos({ apiBaseUrl, onError, onSuccess }) {
  const [employeeId, setEmployeeId] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [images, setImages] = useState([]);
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
    return () => {
      stopCamera();
      images.forEach((img) => {
        try {
          URL.revokeObjectURL(img.preview);
        } catch (e) {}
      });
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSave = async () => {
    if (!employeeId.trim() || !firstName.trim() || !lastName.trim()) {
      onError(new Error("All fields are required"));
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

      const response = await axios.post(`${apiBaseUrl}/save-employee-photos`, {
        employee_id: employeeId,
        first_name: firstName,
        last_name: lastName,
        photos: base64Images,
      });

      onSuccess(`Successfully saved photos for ${response.data.folder_name}`);
      setEmployeeId("");
      setFirstName("");
      setLastName("");
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

  return (
    <div className="component-container">
      <h2>👔 Save Employee Photos</h2>

      <div className="form-group">
        <label>Employee ID:</label>
        <input
          type="text"
          value={employeeId}
          onChange={(e) => setEmployeeId(e.target.value)}
          placeholder="e.g., EMP001"
          className="input"
        />
      </div>

      <div className="form-group">
        <label>First Name:</label>
        <input
          type="text"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          placeholder="First name"
          className="input"
        />
      </div>

      <div className="form-group">
        <label>Last Name:</label>
        <input
          type="text"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          placeholder="Last name"
          className="input"
        />
      </div>

      <div className="form-group">
        <label>Upload Photos:</label>
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileSelect}
          ref={fileInputRef}
          className="file-input"
        />
        <p className="text-muted">
          Upload or capture employee photos (without training)
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
        onClick={handleSave}
        disabled={
          loading ||
          !employeeId.trim() ||
          !firstName.trim() ||
          !lastName.trim() ||
          images.length === 0
        }
        className="btn btn-primary"
      >
        {loading ? "🔄 Saving..." : "💾 Save Photos"}
      </button>
    </div>
  );
}

export default SaveEmployeePhotos;

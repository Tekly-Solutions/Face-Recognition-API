import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

function Verify({ apiBaseUrl, onError, onSuccess }) {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [verificationMode, setVerificationMode] = useState("file"); // "file" or "live"
  const [liveResult, setLiveResult] = useState(null);
  const [autoVerifying, setAutoVerifying] = useState(false);
  const [verificationFrequency, setVerificationFrequency] = useState(2000); // ms between verifications

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const verificationIntervalRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
      if (verificationIntervalRef.current) {
        clearInterval(verificationIntervalRef.current);
      }
    };
  }, []);

  // Auto-verify when in live mode
  useEffect(() => {
    if (!autoVerifying || !cameraActive) {
      if (verificationIntervalRef.current) {
        clearInterval(verificationIntervalRef.current);
      }
      return;
    }

    const performVerification = async () => {
      if (!videoRef.current || !canvasRef.current) return;

      const canvas = canvasRef.current;
      const video = videoRef.current;
      const ctx = canvas.getContext("2d");

      if (ctx && video.readyState === video.HAVE_ENOUGH_DATA) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(async (blob) => {
          if (!blob) return;

          try {
            const base64 = await new Promise((resolve) => {
              const reader = new FileReader();
              reader.onload = () => resolve(reader.result);
              reader.readAsDataURL(blob);
            });

            const response = await axios.post(`${apiBaseUrl}/verify`, {
              image: base64,
            });

            setLiveResult(response.data);
          } catch (err) {
            console.error("Verification error:", err);
          }
        }, "image/jpeg");
      }
    };

    verificationIntervalRef.current = setInterval(
      performVerification,
      verificationFrequency
    );

    return () => {
      if (verificationIntervalRef.current) {
        clearInterval(verificationIntervalRef.current);
      }
    };
  }, [autoVerifying, cameraActive, verificationFrequency, apiBaseUrl]);

  const convertToBase64 = async (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
    });
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 } },
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setCameraActive(true);
        setLiveResult(null);
      }
    } catch (err) {
      onError(err);
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
    }
    setCameraActive(false);
    setAutoVerifying(false);
    setLiveResult(null);
  };

  const toggleAutoVerify = () => {
    setAutoVerifying(!autoVerifying);
  };

  const captureAndVerify = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext("2d");

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(async (blob) => {
      if (!blob) return;

      setLoading(true);
      try {
        const base64 = await convertToBase64(blob);
        const response = await axios.post(`${apiBaseUrl}/verify`, {
          image: base64,
        });

        setResult(response.data);
        if (response.data.verified) {
          onSuccess(`Face verified as ${response.data.person_name}`);
        } else {
          onSuccess("Face captured but person is unknown");
        }
      } catch (err) {
        onError(err);
      } finally {
        setLoading(false);
      }
    }, "image/jpeg");
  };

  const handleVerify = async () => {
    if (!image) {
      onError(new Error("Please select an image"));
      return;
    }

    setLoading(true);
    try {
      const base64Image = await convertToBase64(image);
      const response = await axios.post(`${apiBaseUrl}/verify`, {
        image: base64Image,
      });

      setResult(response.data);
      if (response.data.verified) {
        onSuccess(`Face verified as ${response.data.person_name}`);
      } else {
        onSuccess("Face verified but person is unknown");
      }
    } catch (err) {
      onError(err);
    } finally {
      setLoading(false);
    }
  };

  const clearImage = () => {
    setImage(null);
    setPreview(null);
    setResult(null);
    fileInputRef.current.value = "";
  };

  const handleVerificationFrequencyChange = (e) => {
    setVerificationFrequency(parseInt(e.target.value));
  };

  return (
    <div className="component-container">
      <h2>✅ Verify Face</h2>

      {/* Mode Selection */}
      <div className="form-group">
        <label>Verification Mode:</label>
        <div className="mode-selector">
          <button
            onClick={() => {
              setVerificationMode("file");
              stopCamera();
            }}
            className={`btn ${
              verificationMode === "file" ? "btn-primary" : "btn-secondary"
            }`}
          >
            📁 Upload Image
          </button>
          <button
            onClick={() => {
              setVerificationMode("live");
              startCamera();
            }}
            className={`btn ${
              verificationMode === "live" ? "btn-primary" : "btn-secondary"
            }`}
          >
            📹 Live Camera
          </button>
        </div>
      </div>

      {/* File Upload Mode */}
      {verificationMode === "file" && (
        <>
          <div className="form-group">
            <label>Upload Image:</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              ref={fileInputRef}
              className="file-input"
            />
          </div>

          {preview && (
            <div className="preview-container">
              <img src={preview} alt="Preview" className="preview-image" />
              <button onClick={clearImage} className="btn btn-secondary">
                Clear Image
              </button>
            </div>
          )}

          <button
            onClick={handleVerify}
            disabled={loading || !image}
            className="btn btn-primary"
          >
            {loading ? "🔄 Verifying..." : "✅ Verify Face"}
          </button>
        </>
      )}

      {/* Live Camera Mode */}
      {verificationMode === "live" && (
        <>
          <div className="camera-container">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              style={{
                width: "100%",
                maxWidth: "600px",
                borderRadius: "8px",
                border: "2px solid #4CAF50",
              }}
            />
            <canvas
              ref={canvasRef}
              style={{ display: "none" }}
              width={1280}
              height={720}
            />
          </div>

          <div className="camera-controls">
            <button
              onClick={stopCamera}
              disabled={!cameraActive}
              className="btn btn-danger"
            >
              🛑 Stop Camera
            </button>

            <button
              onClick={captureAndVerify}
              disabled={!cameraActive || loading}
              className="btn btn-primary"
            >
              {loading ? "🔄 Verifying..." : "📸 Capture & Verify"}
            </button>

            <button
              onClick={toggleAutoVerify}
              disabled={!cameraActive}
              className={`btn ${
                autoVerifying ? "btn-warning" : "btn-secondary"
              }`}
            >
              {autoVerifying ? "⏸ Stop Auto-Verify" : "▶️ Auto-Verify"}
            </button>
          </div>

          {autoVerifying && (
            <div className="form-group">
              <label>Verification Frequency (ms):</label>
              <input
                type="range"
                min="500"
                max="5000"
                step="500"
                value={verificationFrequency}
                onChange={handleVerificationFrequencyChange}
                className="slider"
              />
              <span>{verificationFrequency}ms</span>
            </div>
          )}

          {liveResult && (
            <div
              className={`result-card ${
                liveResult.verified ? "verified" : "not-verified"
              }`}
              style={{ marginTop: "20px" }}
            >
              <h4>{liveResult.verified ? "✅ Verified" : "❌ Not Verified"}</h4>
              {liveResult.person_name && (
                <p>
                  <strong>Person:</strong> {liveResult.person_name}
                </p>
              )}
              {liveResult.confidence !== undefined && (
                <p>
                  <strong>Confidence:</strong>{" "}
                  {(liveResult.confidence * 100).toFixed(2)}%
                </p>
              )}
              {liveResult.message && (
                <p>
                  <strong>Message:</strong> {liveResult.message}
                </p>
              )}
              <p>
                <strong>Threshold:</strong>{" "}
                {(liveResult.threshold * 100).toFixed(2)}%
              </p>
            </div>
          )}
        </>
      )}

      {/* Verification Result (File Mode) */}
      {verificationMode === "file" && result && (
        <div
          className={`result-card ${
            result.verified ? "verified" : "not-verified"
          }`}
        >
          <h4>{result.verified ? "✅ Verified" : "❌ Not Verified"}</h4>
          {result.person_name && (
            <p>
              <strong>Person:</strong> {result.person_name}
            </p>
          )}
          {result.confidence !== undefined && (
            <p>
              <strong>Confidence:</strong>{" "}
              {(result.confidence * 100).toFixed(2)}%
            </p>
          )}
          {result.message && (
            <p>
              <strong>Message:</strong> {result.message}
            </p>
          )}
          <p>
            <strong>Threshold:</strong> {(result.threshold * 100).toFixed(2)}%
          </p>
        </div>
      )}
    </div>
  );
}

export default Verify;

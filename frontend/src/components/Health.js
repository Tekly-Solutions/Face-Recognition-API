import React, { useState, useEffect } from "react";
import axios from "axios";

function Health({ apiBaseUrl, onError, onSuccess }) {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkHealth = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiBaseUrl}/health`);
      setHealthData(response.data);
      onSuccess("Health check successful");
    } catch (err) {
      onError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkHealth();
  }, []);

  return (
    <div className="component-container">
      <h2>🏥 System Health Check</h2>
      <button
        onClick={checkHealth}
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? "Checking..." : "Check Health"}
      </button>

      {healthData && (
        <div className="health-card">
          <div className="health-item">
            <span>Status:</span>
            <strong className={`status-${healthData.status}`}>
              {healthData.status.toUpperCase()}
            </strong>
          </div>
          <div className="health-item">
            <span>Service:</span>
            <strong>{healthData.service}</strong>
          </div>
          <div className="health-item">
            <span>Faces in Database:</span>
            <strong>{healthData.faces_in_database}</strong>
          </div>
          <div className="health-item">
            <span>System Initialized:</span>
            <strong>
              {healthData.system_initialized ? "✅ Yes" : "❌ No"}
            </strong>
          </div>
        </div>
      )}
    </div>
  );
}

export default Health;

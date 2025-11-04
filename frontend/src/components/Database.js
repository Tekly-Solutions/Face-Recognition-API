import React, { useState, useEffect } from "react";
import axios from "axios";

function Database({ apiBaseUrl, onError, onSuccess }) {
  const [dbInfo, setDbInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchDatabaseInfo = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${apiBaseUrl}/database`);
      setDbInfo(response.data);
      onSuccess("Database info loaded");
    } catch (err) {
      onError(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRebuild = async () => {
    if (
      window.confirm(
        "Are you sure you want to rebuild the model? This may take a few minutes."
      )
    ) {
      setLoading(true);
      try {
        const response = await axios.post(`${apiBaseUrl}/rebuild`);
        onSuccess("Model rebuilt successfully");
        fetchDatabaseInfo();
      } catch (err) {
        onError(err);
      } finally {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchDatabaseInfo();
  }, []);

  return (
    <div className="component-container">
      <h2>📊 Database Information</h2>

      <div className="button-group">
        <button
          onClick={fetchDatabaseInfo}
          disabled={loading}
          className="btn btn-secondary"
        >
          🔄 Refresh
        </button>
        <button
          onClick={handleRebuild}
          disabled={loading}
          className="btn btn-warning"
        >
          🔨 Rebuild Model
        </button>
      </div>

      {dbInfo && (
        <div className="database-info">
          <div className="info-card">
            <h3>📈 Statistics</h3>
            <div className="info-row">
              <span>Total Faces:</span>
              <strong>{dbInfo.total_faces}</strong>
            </div>
            <div className="info-row">
              <span>Unique Persons:</span>
              <strong>{dbInfo.unique_persons}</strong>
            </div>
            <div className="info-row">
              <span>Threshold:</span>
              <strong>{(dbInfo.threshold * 100).toFixed(2)}%</strong>
            </div>
          </div>

          {dbInfo.persons.length > 0 && (
            <div className="info-card">
              <h3>👥 Trained Persons</h3>
              <ul className="persons-list">
                {dbInfo.persons.map((person, index) => (
                  <li key={index}>
                    <span className="person-name">{person}</span>
                    <span className="person-count">
                      {dbInfo.person_image_counts[person] || 0} images
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {dbInfo.persons.length === 0 && (
            <div className="info-card empty-state">
              <p>📭 No persons trained yet</p>
              <p>Start by training new faces using the Train tab</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Database;

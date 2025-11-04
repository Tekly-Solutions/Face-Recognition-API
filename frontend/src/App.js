import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";
import Health from "./components/Health";
import Train from "./components/Train";
import Verify from "./components/Verify";
import Database from "./components/Database";
import SaveEmployeePhotos from "./components/SaveEmployeePhotos";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function App() {
  const [activeTab, setActiveTab] = useState("health");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const clearMessages = () => {
    setError(null);
    setSuccess(null);
  };

  const handleError = (err) => {
    setError(err.response?.data?.detail || err.message || "An error occurred");
    setSuccess(null);
  };

  const handleSuccess = (message) => {
    setSuccess(message);
    setError(null);
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎭 Face Recognition System</h1>
        <p>Advanced face recognition with training and verification</p>
      </header>

      <nav className="app-nav">
        <button
          className={`nav-btn ${activeTab === "health" ? "active" : ""}`}
          onClick={() => {
            setActiveTab("health");
            clearMessages();
          }}
        >
          🏥 Health
        </button>
        <button
          className={`nav-btn ${activeTab === "train" ? "active" : ""}`}
          onClick={() => {
            setActiveTab("train");
            clearMessages();
          }}
        >
          📸 Train
        </button>
        <button
          className={`nav-btn ${activeTab === "verify" ? "active" : ""}`}
          onClick={() => {
            setActiveTab("verify");
            clearMessages();
          }}
        >
          ✅ Verify
        </button>
        <button
          className={`nav-btn ${activeTab === "save-employee" ? "active" : ""}`}
          onClick={() => {
            setActiveTab("save-employee");
            clearMessages();
          }}
        >
          👔 Save Employee
        </button>
        <button
          className={`nav-btn ${activeTab === "database" ? "active" : ""}`}
          onClick={() => {
            setActiveTab("database");
            clearMessages();
          }}
        >
          📊 Database
        </button>
      </nav>

      <main className="app-main">
        {error && (
          <div className="alert alert-error">
            ❌ {error}
            <button className="close-btn" onClick={() => setError(null)}>
              ×
            </button>
          </div>
        )}
        {success && (
          <div className="alert alert-success">
            ✅ {success}
            <button className="close-btn" onClick={() => setSuccess(null)}>
              ×
            </button>
          </div>
        )}

        <div className="content">
          {activeTab === "health" && (
            <Health
              apiBaseUrl={API_BASE_URL}
              onError={handleError}
              onSuccess={handleSuccess}
            />
          )}
          {activeTab === "train" && (
            <Train
              apiBaseUrl={API_BASE_URL}
              onError={handleError}
              onSuccess={handleSuccess}
            />
          )}
          {activeTab === "verify" && (
            <Verify
              apiBaseUrl={API_BASE_URL}
              onError={handleError}
              onSuccess={handleSuccess}
            />
          )}
          {activeTab === "save-employee" && (
            <SaveEmployeePhotos
              apiBaseUrl={API_BASE_URL}
              onError={handleError}
              onSuccess={handleSuccess}
            />
          )}
          {activeTab === "database" && (
            <Database
              apiBaseUrl={API_BASE_URL}
              onError={handleError}
              onSuccess={handleSuccess}
            />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; 2025 Tekly IT Solutions. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;

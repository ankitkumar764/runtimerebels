import React, { useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import Papa from "papaparse";
import { ArrowLeft, ArrowRight, UploadCloud, CheckCircle, AlertCircle, Trash2, MessageSquare } from "lucide-react";

export default function Upload() {
  const navigate = useNavigate();
  
  // State variables
  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [parsedData, setParsedData] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // File drop handler
  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError(null);
    setSuccess(false);
    setParsedData(null);
    setUploadProgress(0);
    
    if (rejectedFiles && rejectedFiles.length > 0) {
      const rejectReason = rejectedFiles[0].errors[0]?.code;
      if (rejectReason === "file-too-large") {
        setError("File is too large. Maximum size is 10MB.");
      } else if (rejectReason === "file-invalid-type") {
        setError("Invalid file format. Please upload JSON, CSV, or TXT.");
      } else {
        setError("Unable to accept this file.");
      }
      return;
    }

    if (acceptedFiles && acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      setFile(selectedFile);
      handleFileUpload(selectedFile);
    }
  }, []);

  // Configure react-dropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    maxSize: 10 * 1024 * 1024, // 10MB
    accept: {
      "application/json": [".json"],
      "text/csv": [".csv"],
      "text/plain": [".txt"]
    }
  });

  // Handle file parsing and uploading to backend
  const handleFileUpload = async (selectedFile) => {
    setIsUploading(true);
    setUploadProgress(10);

    // Simulate progress while uploading/parsing
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90;
        }
        return prev + 15;
      });
    }, 100);

    try {
      // 1. Send file to backend API
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      clearInterval(interval);
      setUploadProgress(100);

      if (response.ok) {
        const result = await response.json();
        setParsedData({
          messageCount: result.messages,
          preview: result.preview
        });
        setSuccess(true);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Server failed to parse the file.");
      }
    } catch (apiError) {
      console.warn("Backend API upload failed, falling back to client-side parsing...", apiError);
      
      // Fallback: Parse file locally in the browser if backend API is not responding
      try {
        const text = await selectedFile.text();
        let messages = [];
        const ext = selectedFile.name.split(".").pop().toLowerCase();

        if (ext === "json") {
          const data = JSON.parse(text);
          if (Array.isArray(data)) {
            messages = data.map((item) => ({
              sender: item.sender || item.from || "Unknown",
              text: item.text || item.content || "",
              timestamp: item.timestamp || item.date || ""
            })).filter(item => item.text);
          } else {
            throw new Error("JSON file must contain an array of messages.");
          }
        } else if (ext === "csv") {
          const parseResult = Papa.parse(text, { header: true, skipEmptyLines: true });
          messages = parseResult.data.map((row) => {
            const sender = row.sender || row.from || Object.values(row)[0] || "Unknown";
            const text = row.text || row.content || row.message || Object.values(row)[1] || "";
            const timestamp = row.timestamp || row.date || Object.values(row)[2] || "";
            return { sender, text, timestamp };
          }).filter(item => item.text);
        } else if (ext === "txt") {
          const lines = text.split("\n");
          messages = lines.map((line) => {
            if (line.includes(":")) {
              const parts = line.split(":", 2);
              let sender = parts[0].trim().replace("[", "").replace("]", "");
              if (sender.includes(" - ")) {
                sender = sender.split(" - ").pop().trim();
              }
              const text = parts[1].trim();
              return { sender, text, timestamp: "" };
            }
            return null;
          }).filter(item => item !== null && item.text);
        }

        if (messages.length === 0) {
          throw new Error("No valid messages found in the file.");
        }

        setParsedData({
          messageCount: messages.length,
          preview: messages.slice(0, 3)
        });
        setSuccess(true);
      } catch (localError) {
        setError(localError.message || "Unable to parse file. Please check format.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  // Clear current file selection
  const clearFile = () => {
    setFile(null);
    setParsedData(null);
    setSuccess(false);
    setError(null);
    setUploadProgress(0);
  };

  return (
    <div style={{
      minHeight: "100vh",
      backgroundColor: "var(--bmw-canvas)",
      color: "var(--bmw-ink)",
      padding: "40px 24px",
      boxSizing: "border-box",
      display: "flex",
      flexDirection: "column",
      alignItems: "center"
    }}>
      <div style={{ maxWidth: "800px", width: "100%" }}>
        
        {/* Back Link */}
        <button 
          onClick={() => navigate("/")}
          style={{
            background: "none",
            border: "none",
            color: "var(--bmw-muted)",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontSize: "14px",
            fontWeight: "500",
            cursor: "pointer",
            marginBottom: "32px",
            padding: 0
          }}
        >
          <ArrowLeft size={16} /> Back to Home
        </button>

        {/* Title */}
        <h2 className="bmw-display-sm" style={{ fontSize: "32px", marginBottom: "8px" }}>
          📂 Upload Your Chat History
        </h2>
        <p className="bmw-body-md" style={{ marginBottom: "32px", color: "var(--bmw-body)" }}>
          Your clone needs to learn how you talk. Upload your chat history exports from WhatsApp, Telegram, or any messaging app to get started.
        </p>

        {/* Drag & Drop Zone */}
        {!file && (
          <div 
            {...getRootProps()} 
            style={{
              border: isDragActive 
                ? "2px dashed var(--bmw-blue)" 
                : "2px dashed var(--bmw-hairline-strong)",
              backgroundColor: isDragActive 
                ? "rgba(28, 105, 212, 0.04)" 
                : "var(--bmw-surface-card)",
              padding: "60px 40px",
              textAlign: "center",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
          >
            <input {...getInputProps()} />
            <UploadCloud size={48} color="var(--bmw-muted)" style={{ marginBottom: "16px" }} />
            <h4 className="bmw-label-uppercase" style={{ fontSize: "14px", color: "var(--bmw-ink)", marginBottom: "8px" }}>
              {isDragActive ? "Drop the file here" : "Drag & Drop your file here"}
            </h4>
            <p className="bmw-body-sm" style={{ margin: "0 0 16px 0" }}>
              or click to browse from your computer
            </p>
            <div style={{ 
              display: "flex", 
              justifyContent: "center", 
              gap: "12px", 
              fontSize: "12px", 
              color: "var(--bmw-muted)" 
            }}>
              <span>Supported: .JSON, .CSV, .TXT</span>
              <span>•</span>
              <span>Max size: 10MB</span>
            </div>
          </div>
        )}

        {/* Error Alert Box */}
        {error && (
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            border: "1px solid var(--bmw-error)",
            backgroundColor: "rgba(220, 38, 38, 0.04)",
            padding: "16px 20px",
            marginTop: "20px",
            color: "var(--bmw-error)"
          }}>
            <AlertCircle size={20} />
            <span style={{ fontSize: "14px", fontWeight: "500" }}>{error}</span>
          </div>
        )}

        {/* Processing Indicator */}
        {isUploading && (
          <div className="bmw-card" style={{ marginTop: "24px" }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
              <span className="bmw-label-uppercase" style={{ fontSize: "12px" }}>Uploading and Parsing File...</span>
              <span style={{ fontSize: "12px", fontWeight: "700" }}>{uploadProgress}%</span>
            </div>
            <div style={{ width: "100%", backgroundColor: "var(--bmw-surface-strong)", height: "6px" }}>
              <div 
                style={{ 
                  backgroundColor: "var(--bmw-blue)", 
                  height: "100%", 
                  width: `${uploadProgress}%`, 
                  transition: "width 0.2s ease" 
                }} 
              />
            </div>
          </div>
        )}

        {/* Upload Success Details */}
        {success && parsedData && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px", marginTop: "24px" }}>
            
            {/* File details card */}
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              border: "1px solid var(--bmw-success)",
              backgroundColor: "rgba(34, 197, 94, 0.04)",
              padding: "16px 24px",
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                <CheckCircle size={24} color="var(--bmw-success)" />
                <div>
                  <h4 style={{ margin: 0, fontSize: "15px", fontWeight: "700" }}>
                    File Uploaded Successfully!
                  </h4>
                  <p className="bmw-body-sm" style={{ margin: 0, color: "var(--bmw-muted)" }}>
                    {file?.name} ({ (file?.size / (1024 * 1024)).toFixed(2) } MB)
                  </p>
                </div>
              </div>
              <button 
                onClick={clearFile}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--bmw-error)",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                  fontSize: "12px",
                  fontWeight: "700",
                  textTransform: "uppercase",
                  letterSpacing: "1px"
                }}
              >
                <Trash2 size={14} /> Remove
              </button>
            </div>

            {/* Found Message Count banner */}
            <div style={{
              backgroundColor: "var(--bmw-surface-soft)",
              border: "1px solid var(--bmw-hairline)",
              padding: "16px 24px"
            }}>
              <span className="bmw-label-uppercase" style={{ fontSize: "11px", color: "var(--bmw-muted)" }}>Data Ingested</span>
              <h3 style={{ margin: "4px 0 0 0", fontSize: "28px", fontWeight: "800", color: "var(--bmw-blue)" }}>
                {parsedData.messageCount.toLocaleString()} messages parsed
              </h3>
            </div>

            {/* Previews of messages */}
            <div className="bmw-card" style={{ margin: 0 }}>
              <h4 className="bmw-label-uppercase" style={{ fontSize: "12px", color: "var(--bmw-ink)", marginBottom: "16px" }}>
                📱 Chat Logs Preview (First {parsedData.preview.length} messages)
              </h4>
              <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                {parsedData.preview.map((msg, index) => (
                  <div 
                    key={index}
                    style={{
                      padding: "12px 16px",
                      backgroundColor: msg.sender.toLowerCase() === "you" ? "rgba(28, 105, 212, 0.05)" : "var(--bmw-surface-soft)",
                      borderLeft: msg.sender.toLowerCase() === "you" ? "4px solid var(--bmw-blue)" : "4px solid var(--bmw-hairline-strong)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "4px" }}>
                      <span style={{ fontWeight: "700", fontSize: "12px", textTransform: "uppercase", letterSpacing: "1px" }}>
                        {msg.sender}
                      </span>
                      {msg.timestamp && (
                        <span style={{ fontSize: "11px", color: "var(--bmw-muted)" }}>
                          {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      )}
                    </div>
                    <p style={{ margin: 0, fontSize: "14px", color: "var(--bmw-ink)", lineHeight: "1.4" }}>
                      {msg.text}
                    </p>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )}

        {/* Continue Actions */}
        <div style={{
          display: "flex",
          justifyContent: "flex-end",
          marginTop: "40px",
          borderTop: "1px solid var(--bmw-hairline)",
          paddingTop: "24px"
        }}>
          <button 
            className="bmw-btn-primary"
            disabled={!success}
            onClick={() => navigate("/dashboard")}
            style={{ display: "flex", alignItems: "center", gap: "10px" }}
          >
            Continue to Dashboard <ArrowRight size={16} />
          </button>
        </div>

      </div>
    </div>
  );
}

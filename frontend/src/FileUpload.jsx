import { useRef, useState } from "react";
import "./FileUpload.css";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");
  const [uploading, setUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (
      droppedFile &&
      (droppedFile.type === "application/pdf" || droppedFile.type === "text/plain")
    ) {
      setFile(droppedFile);
      setStatus("");
    } else {
      setStatus("❌ Please drop a PDF or text file");
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);
      setStatus("");
      setProgress(0);
    }
  };

  const uploadFile = async () => {
    if (!file) {
      setStatus("❌ Please select a file first");
      return;
    }

    const maxSizeBytes = 100 * 1024 * 1024;

    if (file.size > maxSizeBytes) {
      setStatus("❌ File is too large. Please use a file under 100MB.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setStatus("⏳ Uploading file to server...");
    setUploading(true);
    setProgress(0);

    try {
      const data = await new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        xhr.open("POST", "http://localhost:8000/upload");

        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const uploadPercent = Math.min(
              70,
              Math.round((event.loaded / event.total) * 70)
            );
            setProgress(uploadPercent);
            setStatus(`⏳ Uploading file... ${uploadPercent}%`);
          }
        };

        xhr.upload.onload = () => {
          setProgress(80);
          setStatus("⏳ Upload complete. Indexing document on server...");
        };

        xhr.onload = () => {
          try {
            const responseData = JSON.parse(xhr.responseText);

            if (xhr.status >= 200 && xhr.status < 300) {
              resolve(responseData);
              return;
            }

            reject(new Error(responseData?.detail || `HTTP error ${xhr.status}`));
          } catch {
            reject(new Error("Server returned an invalid response"));
          }
        };

        xhr.onerror = () => reject(new Error("Network error while uploading"));

        xhr.send(formData);
      });

      setProgress(100);
      setStatus("✨ Upload complete. Indexing your document...");

      setStatus(`✅ ${data.message}`);
      setUploadedFiles((prev) => [
        ...prev,
        {
          name: data.filename,
          chunks: data.total_chunks,
          uploadId: data.upload_id,
        },
      ]);
      setFile(null);
      setProgress(0);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      const errorMsg =
        err instanceof Error ? err.message : "Failed to upload";
      setStatus(`❌ Upload failed: ${errorMsg}`);
      setProgress(0);
    }

    setUploading(false);
  };

  return (
    <div className="upload-section">
      <h2>📄 Upload Document</h2>
      <p className="upload-subtitle">
        Upload a PDF or text file to start asking questions
      </p>

      <div
        className={`drop-zone ${isDragging ? "dragging" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          id="file-input"
          type="file"
          onChange={handleFileSelect}
          accept=".pdf,.txt"
          className="file-input-hidden"
        />

        <div className="drop-zone-content">
          <div className="drop-icon">📁</div>
          <p className="drop-text">
            {file
              ? `Selected: ${file.name}`
              : "Drag and drop your file here, or click to select"}
          </p>
          <p className="drop-hint">Supported: PDF, TXT (Max 100MB)</p>
        </div>

        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          className="choose-file-btn"
        >
          Choose File
        </button>
      </div>

      <div className="upload-meter">
        <div className="upload-meter-track">
          <div className="upload-meter-fill" style={{ width: `${progress}%` }} />
        </div>
        <span className="upload-meter-label">
          {uploading ? `${progress}%` : file ? "Ready to upload" : "Waiting for a file"}
        </span>
      </div>

      <div className="upload-actions">
        <button
          onClick={uploadFile}
          disabled={uploading || !file}
          className="upload-button"
        >
          {uploading ? "⏳ Uploading..." : "Upload"}
        </button>
      </div>

      {status && (
        <div
          className={`status-message ${
            status.includes("✅")
              ? "success"
              : status.includes("❌")
              ? "error"
              : "info"
          }`}
        >
          {status}
        </div>
      )}

      <div className="upload-tips">
        <div className="tip-card coral">
          <strong>Fastest results</strong>
          <span>Use clean PDFs or text files under 10MB if possible.</span>
        </div>
        <div className="tip-card blue">
          <strong>Still processing?</strong>
          <span>Large documents can take a moment to index after upload.</span>
        </div>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h3>📚 Uploaded Files</h3>
          <div className="files-list">
            {uploadedFiles.map((f, idx) => (
              <div key={idx} className="file-item">
                <span className="file-name">{f.name}</span>
                <span className="file-chunks">{f.chunks} chunks</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default FileUpload;

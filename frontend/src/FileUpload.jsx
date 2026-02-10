import { useState } from "react";

function FileUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const uploadFile = async () => {
    if (!file) {
      setStatus("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setStatus("Uploading...");

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setStatus(data.message || "Uploaded successfully");
    } catch (err) {
      setStatus("Upload failed");
    }
  };

  return (
    <div style={{ marginBottom: "30px" }}>
      <h3>📄 Upload Document</h3>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <br /><br />
      <button onClick={uploadFile}>Upload</button>
      <p>{status}</p>
    </div>
  );
}

export default FileUpload;

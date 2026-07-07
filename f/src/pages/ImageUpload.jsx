import { useState } from "react";
import axios from "axios";

export default function UploadImages() {
  const [files, setFiles] = useState([]);
  const [eventId, setEventId] = useState("990dc916-37fd-49d1-a050-86ff9a298352");
  const [photographerId, setPhotographerId] = useState("b8383b76-1bdc-44be-8c81-255b78932ffa");
  const [metadata, setMetadata] = useState("{\"camera\":\"iphone\",\"location\":\"chennai\"}");

  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleUpload = async () => {
    if (!files.length) {
      alert("Please select images");
      return;
    }

    const formData = new FormData();

    // Upload all images
    files.forEach((file) => {
      formData.append("files", file);
    });

    // Other form fields
    formData.append("event_id", eventId);
    formData.append("photographer_id", photographerId);
    formData.append("metadata", metadata);

    try {
      setLoading(true);

      const res = await axios.post(
        "http://localhost:8000/api/v1/images/upload-multiple",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setResponse(res.data);
    } catch (err) {
      console.error(err.response?.data || err);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto mt-10 max-w-xl rounded-lg bg-white p-6 shadow-lg">
      <h1 className="mb-6 text-2xl font-bold">
        Upload Images
      </h1>

      {/* Event ID */}
      <div className="mb-4">
        <label className="mb-1 block font-medium">
          Event ID
        </label>
        <input
          type="text"
          value={eventId}
          onChange={(e) => setEventId(e.target.value)}
          className="w-full rounded border p-2"
          placeholder="Enter Event ID"
        />
      </div>

      {/* Photographer ID */}
      <div className="mb-4">
        <label className="mb-1 block font-medium">
          Photographer ID
        </label>
        <input
          type="text"
          value={photographerId}
          onChange={(e) => setPhotographerId(e.target.value)}
          className="w-full rounded border p-2"
          placeholder="Enter Photographer ID"
        />
      </div>

      {/* Metadata */}
      <div className="mb-4">
        <label className="mb-1 block font-medium">
          Metadata
        </label>
        <textarea
          rows={4}
          value={metadata}
          onChange={(e) => setMetadata(e.target.value)}
          className="w-full rounded border p-2"
          placeholder='{"location":"Chennai","camera":"Sony A7IV"}'
        />
      </div>

      {/* Images */}
      <div className="mb-4">
        <label className="mb-1 block font-medium">
          Select Images
        </label>

        <input
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileChange}
          className="w-full rounded border p-2"
        />
      </div>

      {files.length > 0 && (
        <div className="mb-4 rounded bg-gray-100 p-3">
          <h3 className="font-semibold">Selected Files</h3>

          {files.map((file) => (
            <div key={file.name}>{file.name}</div>
          ))}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={loading}
        className="w-full rounded bg-blue-600 py-2 text-white hover:bg-blue-700"
      >
        {loading ? "Uploading..." : "Upload"}
      </button>

      {response && (
        <div className="mt-6 rounded bg-green-100 p-4">
          <h2 className="font-semibold">Response</h2>

          <pre className="mt-2 overflow-auto text-sm">
            {JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

const API_URL = import.meta.env?.VITE_API_URL || "http://localhost:8000";
const DEFAULT_EVENT_ID = "990dc916-37fd-49d1-a050-86ff9a298352";
const DEFAULT_PHOTOGRAPHER_ID = "b8383b76-1bdc-44be-8c81-255b78932ffa";
const DEFAULT_METADATA = '{"camera":"iphone","location":"chennai"}';

/* ---------- tiny inline icons ---------- */
const Icon = ({ d, className = "h-5 w-5" }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"
    strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
    <path d={d} />
  </svg>
);
const ICONS = {
  upload: "M12 16V4M7 9l5-5 5 5M4 16v4h16v-4",
  close: "M6 6l12 12M18 6L6 18",
  external: "M14 4h6v6M20 4l-9 9M18 14v6H4V6h6",
  spark: "M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z",
  check: "M5 12.5l4.5 4.5L19 7.5",
};

const fileKey = (f) => `${f.name}-${f.size}-${f.lastModified}`;
const formatSize = (b) =>
  b > 1024 * 1024 ? `${(b / 1024 / 1024).toFixed(1)} MB` : `${Math.max(1, Math.round(b / 1024))} KB`;

export default function UploadImages() {
  const [files, setFiles] = useState([]);
  const [eventId, setEventId] = useState(DEFAULT_EVENT_ID);
  const [photographerId, setPhotographerId] = useState(DEFAULT_PHOTOGRAPHER_ID);
  const [metadata, setMetadata] = useState(DEFAULT_METADATA);

  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState("");
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  /* thumbnails: create once per file list, revoke on change */
  const previews = useMemo(
    () => files.map((f) => ({ key: fileKey(f), file: f, url: URL.createObjectURL(f) })),
    [files]
  );
  useEffect(() => () => previews.forEach((p) => URL.revokeObjectURL(p.url)), [previews]);

  /* live JSON validation */
  const metaError = useMemo(() => {
    if (!metadata.trim()) return "";
    try {
      JSON.parse(metadata);
      return "";
    } catch {
      return "Metadata must be valid JSON.";
    }
  }, [metadata]);

  const addFiles = (list) => {
    const incoming = Array.from(list || []).filter((f) => f.type.startsWith("image/"));
    if (incoming.length === 0) return;
    setFiles((prev) => {
      const seen = new Set(prev.map(fileKey));
      return [...prev, ...incoming.filter((f) => !seen.has(fileKey(f)))];
    });
    setResponse(null);
    setError("");
  };

  const handleFileChange = (e) => {
    addFiles(e.target.files);
    e.target.value = "";
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    addFiles(e.dataTransfer.files);
  };

  const removeFile = (key) => setFiles((prev) => prev.filter((f) => fileKey(f) !== key));

  const handleUpload = async () => {
    if (files.length === 0) return setError("Add at least one image.");
    if (!eventId.trim()) return setError("Enter the event ID.");
    if (!photographerId.trim()) return setError("Enter the photographer ID.");
    if (metaError) return setError(metaError);

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("event_id", eventId.trim());
    formData.append("photographer_id", photographerId.trim());
    formData.append("metadata", metadata);

    try {
      setLoading(true);
      setProgress(0);
      setResponse(null);
      setError("");

      // axios sets the multipart boundary itself, so no manual Content-Type
      const res = await axios.post(`${API_URL}/api/v1/images/upload-multiple`, formData, {
        onUploadProgress: (e) => {
          if (e.total) setProgress(Math.round((e.loaded * 100) / e.total));
        },
      });

      console.log("Upload response:", res.data);
      setResponse(res.data);
      setFiles([]);
    } catch (err) {
      console.error("Upload error:", err.response?.data || err);
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Upload failed. Check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  const uploaded = response?.images || [];
  const fieldClass =
    "mt-1.5 w-full rounded-xl border border-white/10 bg-black/60 px-3.5 py-3 text-sm text-white placeholder-white/25 outline-none transition focus:border-violet-300/60 focus:ring-2 focus:ring-violet-400/20";

  return (
    <div className="lm-root relative min-h-screen overflow-hidden bg-black text-white">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');
        .lm-root { font-family: 'Sora', system-ui, sans-serif; }
        .lm-grad { background-image: linear-gradient(110deg,#a78bfa 0%,#f472b6 55%,#fdba74 100%); }
        .lm-grid { background-image: linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px); background-size: 56px 56px; mask-image: radial-gradient(ellipse at 50% 0%, #000 20%, transparent 70%); -webkit-mask-image: radial-gradient(ellipse at 50% 0%, #000 20%, transparent 70%); }
        @keyframes lm-drift { 0%,100% { transform: translate3d(0,0,0) } 50% { transform: translate3d(30px,-20px,0) } }
        .lm-blob { animation: lm-drift 14s ease-in-out infinite; }
        @media (prefers-reduced-motion: reduce) { .lm-blob { animation: none } }
      `}</style>

      {/* ambient background */}
      <div className="lm-grid pointer-events-none absolute inset-0" />
      <div className="lm-blob pointer-events-none absolute -left-32 -top-32 h-[28rem] w-[28rem] rounded-full bg-violet-600/25 blur-[120px]" />
      <div className="lm-blob pointer-events-none absolute -right-24 top-40 h-[24rem] w-[24rem] rounded-full bg-pink-500/20 blur-[120px]" style={{ animationDelay: "-6s" }} />

      <div className="relative mx-auto max-w-7xl px-4 pb-20 sm:px-6">
        {/* top bar */}
        <header className="flex items-center justify-between py-6">
          <div className="flex items-center gap-2.5">
            <span className="lm-grad flex h-8 w-8 items-center justify-center rounded-xl text-black">
              <Icon d={ICONS.spark} className="h-4 w-4" />
            </span>
            <span className="text-lg font-semibold tracking-tight">Lumen</span>
          </div>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-white/60 backdrop-blur">
            Photographer console
          </span>
        </header>

        {/* hero */}
        <section className="mx-auto max-w-3xl pb-12 pt-8 text-center">
          <h1 className="text-4xl font-semibold leading-[1.1] tracking-tight sm:text-5xl">
            Upload event photos.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-base text-white/55 sm:text-lg">
            Drop a batch in. Guests can find their own photos with a selfie as soon as the upload finishes.
          </p>
        </section>

        <div className="grid gap-6 lg:grid-cols-[400px_1fr]">
          {/* ---------- settings panel ---------- */}
          <aside className="h-fit rounded-3xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur-xl lg:sticky lg:top-6">
            <label className="block text-xs font-medium text-white/50" htmlFor="event-id">Event ID</label>
            <input id="event-id" type="text" value={eventId}
              onChange={(e) => setEventId(e.target.value)} placeholder="Paste the event ID"
              className={fieldClass} />

            <label className="mt-4 block text-xs font-medium text-white/50" htmlFor="photographer-id">Photographer ID</label>
            <input id="photographer-id" type="text" value={photographerId}
              onChange={(e) => setPhotographerId(e.target.value)} placeholder="Paste the photographer ID"
              className={fieldClass} />

            <label className="mt-4 block text-xs font-medium text-white/50" htmlFor="metadata">Metadata (JSON)</label>
            <textarea id="metadata" rows={4} value={metadata} spellCheck={false}
              onChange={(e) => setMetadata(e.target.value)}
              placeholder='{"location":"Chennai","camera":"Sony A7IV"}'
              className={`${fieldClass} resize-none font-mono text-xs leading-relaxed ${
                metaError ? "border-rose-400/50 focus:border-rose-400/70 focus:ring-rose-400/20" : ""
              }`} />
            {metaError && <p className="mt-1.5 text-xs text-rose-300">{metaError}</p>}

            <button onClick={handleUpload} disabled={loading || files.length === 0 || !!metaError}
              className="lm-grad mt-6 w-full rounded-2xl py-3.5 font-semibold text-black shadow-[0_8px_40px_-8px_rgba(244,114,182,0.6)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-35 disabled:shadow-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">
              {loading
                ? `Uploading… ${progress}%`
                : files.length > 0
                ? `Upload ${files.length} photo${files.length !== 1 ? "s" : ""}`
                : "Upload photos"}
            </button>

            {loading && (
              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-white/10" role="progressbar"
                aria-valuenow={progress} aria-valuemin={0} aria-valuemax={100}>
                <div className="lm-grad h-full rounded-full transition-all duration-200" style={{ width: `${progress}%` }} />
              </div>
            )}

            {error && (
              <div role="alert" className="mt-4 rounded-xl border border-rose-400/30 bg-rose-500/10 p-3.5 text-sm text-rose-200">
                {error}
              </div>
            )}
          </aside>

          {/* ---------- main column ---------- */}
          <main className="space-y-6">
            {/* drop zone + queue */}
            <section className="rounded-3xl border border-white/10 bg-white/[0.02] p-5 sm:p-6">
              <div
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
                onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && inputRef.current?.click()}
                role="button" tabIndex={0} aria-label="Select images to upload"
                className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed px-6 py-12 text-center transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-400 ${
                  dragging ? "border-pink-300/70 bg-pink-400/10" : "border-white/15 bg-black/40 hover:border-violet-300/50"
                }`}
              >
                <span className="flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-violet-300">
                  <Icon d={ICONS.upload} className="h-6 w-6" />
                </span>
                <p className="mt-4 text-base font-medium">Drop photos here or click to browse</p>
                <p className="mt-1 text-sm text-white/40">JPG, PNG or WebP. Add as many as you need.</p>
                <input ref={inputRef} type="file" multiple accept="image/*" onChange={handleFileChange} className="hidden" />
              </div>

              {previews.length > 0 && (
                <div className="mt-6">
                  <div className="mb-3 flex items-center justify-between">
                    <h2 className="text-sm font-medium text-white/80">
                      {previews.length} ready to upload
                    </h2>
                    <button onClick={() => setFiles([])} disabled={loading}
                      className="text-xs text-white/50 transition hover:text-white disabled:opacity-40">
                      Clear all
                    </button>
                  </div>

                  <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-5 xl:grid-cols-6">
                    {previews.map((p) => (
                      <div key={p.key} className="group relative aspect-square overflow-hidden rounded-xl border border-white/10 bg-white/5">
                        <img src={p.url} alt={p.file.name} className="h-full w-full object-cover" />
                        <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 to-transparent p-2 pt-6">
                          <p className="truncate text-[11px] text-white/80">{p.file.name}</p>
                          <p className="text-[10px] text-white/40">{formatSize(p.file.size)}</p>
                        </div>
                        <button onClick={() => removeFile(p.key)} disabled={loading}
                          aria-label={`Remove ${p.file.name}`}
                          className="absolute right-1.5 top-1.5 rounded-full bg-black/70 p-1 text-white/80 opacity-0 backdrop-blur transition hover:text-white focus-visible:opacity-100 group-hover:opacity-100">
                          <Icon d={ICONS.close} className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </section>

            {/* uploaded results */}
            {uploaded.length > 0 && (
              <section className="rounded-3xl border border-white/10 bg-white/[0.02] p-5 sm:p-6">
                <div className="mb-5 flex items-center gap-3">
                  <span className="lm-grad flex h-9 w-9 items-center justify-center rounded-full text-black">
                    <Icon d={ICONS.check} className="h-5 w-5" />
                  </span>
                  <div>
                    <h2 className="text-xl font-semibold tracking-tight">
                      {uploaded.length} photo{uploaded.length !== 1 ? "s" : ""} uploaded
                    </h2>
                    <p className="text-sm text-white/45">They're now searchable in this event.</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
                  {uploaded.map((image) => (
                    <a key={image.id} href={image.cloudinary_url} target="_blank" rel="noopener noreferrer"
                      className="group relative block aspect-[4/5] overflow-hidden rounded-2xl border border-white/10 bg-white/5 transition hover:border-violet-300/50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-400">
                      <img src={image.cloudinary_url} alt="Uploaded photo" loading="lazy"
                        className="h-full w-full object-cover transition duration-500 group-hover:scale-105" />
                      <div className="absolute inset-x-0 bottom-0 flex items-end justify-between gap-2 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-3 pt-10">
                        <p className="min-w-0 break-all text-[10px] leading-snug text-white/55">{image.id}</p>
                        <Icon d={ICONS.external} className="h-4 w-4 shrink-0 text-white/70" />
                      </div>
                    </a>
                  ))}
                </div>
              </section>
            )}

            {/* raw response */}
            {response && (
              <details className="rounded-2xl border border-white/10 bg-white/[0.02] p-4">
                <summary className="cursor-pointer text-sm text-white/60 transition hover:text-white">
                  Raw API response
                </summary>
                <pre className="mt-3 max-h-80 overflow-auto rounded-xl bg-black/70 p-4 text-xs text-violet-200/90">
                  {JSON.stringify(response, null, 2)}
                </pre>
              </details>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
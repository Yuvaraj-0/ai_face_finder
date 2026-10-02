import { useEffect, useMemo, useRef, useState } from "react";
import axios from "axios";

const API_URL = import.meta.env?.VITE_API_URL || "http://localhost:8000";
const DEFAULT_EVENT_ID = "990dc916-37fd-49d1-a050-86ff9a298352";
const MAX_MB = 10;

/* ---------- tiny inline icons ---------- */
const Icon = ({ d, className = "h-5 w-5" }) => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"
    strokeLinecap="round" strokeLinejoin="round" className={className} aria-hidden="true">
    <path d={d} />
  </svg>
);
const ICONS = {
  camera: "M4 8h3l2-3h6l2 3h3v11H4zM12 17a4 4 0 100-8 4 4 0 000 8z",
  image: "M4 5h16v14H4zM4 16l5-5 4 4 3-3 4 4M9 9.5h.01",
  close: "M6 6l12 12M18 6L6 18",
  left: "M15 5l-7 7 7 7",
  right: "M9 5l7 7-7 7",
  external: "M14 4h6v6M20 4l-9 9M18 14v6H4V6h6",
  spark: "M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z",
  swap: "M7 7h13M16 3l4 4-4 4M17 17H4M8 13l-4 4 4 4",
};

/* ---------- camera modal ---------- */
function CameraModal({ onCapture, onClose }) {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [err, setErr] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 1280 } },
          audio: false,
        });
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop());
          return;
        }
        streamRef.current = stream;
        videoRef.current.srcObject = stream;
        setReady(true);
      } catch {
        setErr("Camera blocked or unavailable. Allow camera access, or upload from your gallery.");
      }
    })();
    return () => {
      cancelled = true;
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const snap = () => {
    const v = videoRef.current;
    if (!v || !v.videoWidth) return;
    const c = document.createElement("canvas");
    c.width = v.videoWidth;
    c.height = v.videoHeight;
    c.getContext("2d").drawImage(v, 0, 0); // un-mirrored for accurate matching
    c.toBlob(
      (b) => b && onCapture(new File([b], `selfie-${Date.now()}.jpg`, { type: "image/jpeg" })),
      "image/jpeg",
      0.92
    );
  };

  return (
    <div role="dialog" aria-modal="true" aria-label="Take a selfie"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-md">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-black p-5 shadow-[0_0_80px_-20px_rgba(139,124,255,0.5)]">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Take a selfie</h3>
          <button onClick={onClose} aria-label="Close camera"
            className="rounded-full p-2 text-white/60 transition hover:bg-white/10 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-400">
            <Icon d={ICONS.close} />
          </button>
        </div>

        <div className="relative aspect-square overflow-hidden rounded-2xl bg-white/5">
          {err ? (
            <p className="flex h-full items-center justify-center p-6 text-center text-sm text-white/60">{err}</p>
          ) : (
            <>
              <video ref={videoRef} autoPlay playsInline muted
                className="h-full w-full -scale-x-100 object-cover" />
              <FaceCorners />
              {!ready && (
                <div className="absolute inset-0 flex items-center justify-center text-sm text-white/50">
                  Starting camera…
                </div>
              )}
            </>
          )}
        </div>

        <p className="mt-3 text-center text-xs text-white/50">
          Face the light, look straight ahead, and remove sunglasses.
        </p>

        <button onClick={snap} disabled={!ready}
          className="lm-grad mt-4 w-full rounded-2xl py-3 font-semibold text-black transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">
          Capture selfie
        </button>
      </div>
    </div>
  );
}

/* ---------- face-frame corner brackets ---------- */
function FaceCorners({ active = false }) {
  const base = `absolute h-8 w-8 border-violet-300/80 transition-colors ${active ? "border-pink-300" : ""}`;
  return (
    <div className="pointer-events-none absolute inset-4">
      <span className={`${base} left-0 top-0 rounded-tl-2xl border-l-2 border-t-2`} />
      <span className={`${base} right-0 top-0 rounded-tr-2xl border-r-2 border-t-2`} />
      <span className={`${base} bottom-0 left-0 rounded-bl-2xl border-b-2 border-l-2`} />
      <span className={`${base} bottom-0 right-0 rounded-br-2xl border-b-2 border-r-2`} />
    </div>
  );
}

/* ---------- lightbox ---------- */
function Lightbox({ items, index, setIndex, onClose }) {
  const item = items[index];

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowLeft") setIndex((i) => (i - 1 + items.length) % items.length);
      if (e.key === "ArrowRight") setIndex((i) => (i + 1) % items.length);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [items.length, onClose, setIndex]);

  return (
    <div role="dialog" aria-modal="true" aria-label="Photo preview"
      className="fixed inset-0 z-50 flex flex-col bg-black/95 backdrop-blur-xl" onClick={onClose}>
      <div className="flex items-center justify-between p-4" onClick={(e) => e.stopPropagation()}>
        <span className="text-sm text-white/60">{index + 1} of {items.length}</span>
        <div className="flex items-center gap-2">
          <a href={item.image_url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-2 rounded-full border border-white/15 px-4 py-2 text-sm text-white transition hover:bg-white/10">
            <Icon d={ICONS.external} className="h-4 w-4" /> Open original
          </a>
          <button onClick={onClose} aria-label="Close preview"
            className="rounded-full p-2 text-white/70 transition hover:bg-white/10 hover:text-white">
            <Icon d={ICONS.close} />
          </button>
        </div>
      </div>

      <div className="relative flex min-h-0 flex-1 items-center justify-center px-4 pb-6">
        <button onClick={(e) => { e.stopPropagation(); setIndex((index - 1 + items.length) % items.length); }}
          aria-label="Previous photo"
          className="absolute left-3 z-10 rounded-full border border-white/10 bg-black/60 p-3 text-white backdrop-blur transition hover:bg-white/10">
          <Icon d={ICONS.left} />
        </button>
        <img src={item.image_url} alt={`Match ${index + 1}`}
          className="max-h-full max-w-full rounded-2xl object-contain"
          onClick={(e) => e.stopPropagation()} />
        <button onClick={(e) => { e.stopPropagation(); setIndex((index + 1) % items.length); }}
          aria-label="Next photo"
          className="absolute right-3 z-10 rounded-full border border-white/10 bg-black/60 p-3 text-white backdrop-blur transition hover:bg-white/10">
          <Icon d={ICONS.right} />
        </button>
      </div>
    </div>
  );
}

/* ---------- main ---------- */
export default function ImageSearch() {
  const [file, setFile] = useState(null);
  const [eventId, setEventId] = useState(DEFAULT_EVENT_ID);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState("");
  const [cameraOpen, setCameraOpen] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [lightbox, setLightbox] = useState(null);
  const galleryRef = useRef(null);

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);
  useEffect(() => () => previewUrl && URL.revokeObjectURL(previewUrl), [previewUrl]);

  const acceptFile = (f) => {
    if (!f) return;
    if (!["image/jpeg", "image/png", "image/webp"].includes(f.type)) {
      setError("Use a JPG, PNG or WebP image.");
      return;
    }
    if (f.size > MAX_MB * 1024 * 1024) {
      setError(`Image is too large. Keep it under ${MAX_MB} MB.`);
      return;
    }
    setFile(f);
    setResults([]);
    setSearched(false);
    setError("");
  };

  const handleGallery = (e) => {
    acceptFile(e.target.files?.[0]);
    e.target.value = ""; // allow re-picking the same file
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    acceptFile(e.dataTransfer.files?.[0]);
  };

  const handleSearch = async () => {
    if (!file) return setError("Add a selfie or photo of your face first.");
    if (!eventId.trim()) return setError("Enter the event ID.");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("event_id", eventId.trim());

    try {
      setLoading(true);
      setResults([]);
      setError("");
      const { data } = await axios.post(`${API_URL}/search/`, formData);
      setResults(data.matches || []);
      setSearched(true);
    } catch (err) {
      console.error("Search error:", err.response?.data || err);
      setResults([]);
      setSearched(false);
      setError(err.response?.data?.detail || "Search failed. Check your connection and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="lm-root relative min-h-screen overflow-hidden bg-black text-white">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');
        .lm-root { font-family: 'Sora', system-ui, sans-serif; }
        .lm-grad { background-image: linear-gradient(110deg,#a78bfa 0%,#f472b6 55%,#fdba74 100%); }
        .lm-grid { background-image: linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px); background-size: 56px 56px; mask-image: radial-gradient(ellipse at 50% 0%, #000 20%, transparent 70%); -webkit-mask-image: radial-gradient(ellipse at 50% 0%, #000 20%, transparent 70%); }
        @keyframes lm-scan { 0% { top: 4%; opacity: 0 } 10% { opacity: 1 } 90% { opacity: 1 } 100% { top: 94%; opacity: 0 } }
        @keyframes lm-shimmer { 0% { background-position: -400px 0 } 100% { background-position: 400px 0 } }
        @keyframes lm-drift { 0%,100% { transform: translate3d(0,0,0) } 50% { transform: translate3d(30px,-20px,0) } }
        .lm-scan { position:absolute; left:6%; right:6%; height:2px; border-radius:2px; background: linear-gradient(90deg,transparent,#c4b5fd,#f9a8d4,transparent); box-shadow: 0 0 24px 4px rgba(244,114,182,.55); animation: lm-scan 1.8s ease-in-out infinite; }
        .lm-skel { background: linear-gradient(90deg,rgba(255,255,255,.04) 25%,rgba(255,255,255,.10) 50%,rgba(255,255,255,.04) 75%); background-size: 800px 100%; animation: lm-shimmer 1.4s linear infinite; }
        .lm-blob { animation: lm-drift 14s ease-in-out infinite; }
        @media (prefers-reduced-motion: reduce) { .lm-scan, .lm-skel, .lm-blob { animation: none } }
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
            Face search for event albums
          </span>
        </header>

        {/* hero */}
        <section className="mx-auto max-w-3xl pb-12 pt-10 text-center">
          <h1 className="text-4xl font-semibold leading-[1.1] tracking-tight sm:text-6xl">
            Find every photo you're in.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-base text-white/55 sm:text-lg">
            Add one clear selfie. We scan the whole event album and return only the photos with your face.
          </p>
        </section>

        <div className="grid gap-6 lg:grid-cols-[400px_1fr]">
          {/* ---------- control panel ---------- */}
          <aside className="h-fit rounded-3xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur-xl lg:sticky lg:top-6">
            {/* face frame */}
            <div
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              className={`relative aspect-square overflow-hidden rounded-2xl border transition ${
                dragging ? "border-pink-300/70 bg-pink-400/10" : "border-white/10 bg-black/60"
              }`}
            >
              {previewUrl ? (
                <>
                  <img src={previewUrl} alt="Your face to search with" className="h-full w-full object-cover" />
                  {loading && <div className="lm-scan" />}
                  {loading && <div className="absolute inset-0 bg-black/30" />}
                </>
              ) : (
                <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center">
                  <span className="flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-white/5 text-violet-300">
                    <Icon d={ICONS.camera} className="h-6 w-6" />
                  </span>
                  <p className="text-sm text-white/70">Drop a photo here, or use the buttons below</p>
                  <p className="text-xs text-white/40">JPG, PNG or WebP · up to {MAX_MB} MB</p>
                </div>
              )}
              <FaceCorners active={loading} />
            </div>

            {file && !loading && (
              <p className="mt-2 truncate text-center text-xs text-white/40">{file.name}</p>
            )}

            {/* source buttons */}
            <div className="mt-4 grid grid-cols-2 gap-3">
              <button onClick={() => setCameraOpen(true)} disabled={loading}
                className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 py-3 text-sm font-medium transition hover:border-violet-300/50 hover:bg-white/10 disabled:opacity-40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-400">
                <Icon d={ICONS.camera} className="h-4 w-4" /> Take selfie
              </button>
              <button onClick={() => galleryRef.current?.click()} disabled={loading}
                className="flex items-center justify-center gap-2 rounded-xl border border-white/10 bg-white/5 py-3 text-sm font-medium transition hover:border-pink-300/50 hover:bg-white/10 disabled:opacity-40 focus-visible:outline focus-visible:outline-2 focus-visible:outline-pink-400">
                <Icon d={file ? ICONS.swap : ICONS.image} className="h-4 w-4" /> {file ? "Change photo" : "From gallery"}
              </button>
              <input ref={galleryRef} type="file" accept="image/jpeg,image/png,image/webp"
                onChange={handleGallery} className="hidden" />
            </div>

            {/* event id */}
            <label className="mt-5 block text-xs font-medium text-white/50" htmlFor="event-id">
              Event ID
            </label>
            <input id="event-id" type="text" value={eventId}
              onChange={(e) => setEventId(e.target.value)} placeholder="Paste your event ID"
              className="mt-1.5 w-full rounded-xl border border-white/10 bg-black/60 px-3.5 py-3 text-sm text-white placeholder-white/25 outline-none transition focus:border-violet-300/60 focus:ring-2 focus:ring-violet-400/20" />

            {/* search */}
            <button onClick={handleSearch} disabled={loading || !file}
              className="lm-grad mt-5 w-full rounded-2xl py-3.5 font-semibold text-black shadow-[0_8px_40px_-8px_rgba(244,114,182,0.6)] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-35 disabled:shadow-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white">
              {loading ? "Scanning album…" : "Find my photos"}
            </button>

            {error && (
              <div role="alert" className="mt-4 rounded-xl border border-rose-400/30 bg-rose-500/10 p-3.5 text-sm text-rose-200">
                {error}
              </div>
            )}
          </aside>

          {/* ---------- results ---------- */}
          <main className="min-h-[28rem] rounded-3xl border border-white/10 bg-white/[0.02] p-5 sm:p-6">
            {/* idle */}
            {!loading && !searched && results.length === 0 && (
              <div className="flex h-full min-h-[24rem] flex-col items-center justify-center text-center">
                <div className="mb-5 grid grid-cols-3 gap-2 opacity-60">
                  {[...Array(6)].map((_, i) => (
                    <div key={i} className="h-16 w-16 rounded-xl border border-white/10 bg-white/[0.04]" />
                  ))}
                </div>
                <h2 className="text-lg font-medium">Your photos will appear here</h2>
                <p className="mt-1.5 max-w-sm text-sm text-white/45">
                  Add a selfie, check the event ID, then press Find my photos.
                </p>
              </div>
            )}

            {/* loading skeletons */}
            {loading && (
              <div>
                <p className="mb-4 text-sm text-white/55">Comparing your face against every photo in the event…</p>
                <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
                  {[...Array(8)].map((_, i) => (
                    <div key={i} className="lm-skel aspect-[4/5] rounded-2xl" />
                  ))}
                </div>
              </div>
            )}

            {/* no results */}
            {!loading && searched && results.length === 0 && !error && (
              <div className="flex h-full min-h-[24rem] flex-col items-center justify-center text-center">
                <h2 className="text-lg font-medium">No matches in this event</h2>
                <p className="mt-1.5 max-w-sm text-sm text-white/45">
                  Try a brighter, front-facing photo without sunglasses or filters, and confirm the event ID.
                </p>
              </div>
            )}

            {/* grid */}
            {!loading && results.length > 0 && (
              <div>
                <div className="mb-5 flex items-end justify-between">
                  <div>
                    <h2 className="text-2xl font-semibold tracking-tight">
                      {results.length} photo{results.length !== 1 ? "s" : ""} found
                    </h2>
                    <p className="mt-1 text-sm text-white/45">Sorted as returned by the album. Tap a photo to view it.</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-4">
                  {results.map((img, i) => (
                    <button key={img.image_id || i} onClick={() => setLightbox(i)}
                      className="group relative aspect-[4/5] overflow-hidden rounded-2xl border border-white/10 bg-white/5 text-left transition hover:border-violet-300/50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-violet-400">
                      <img src={img.image_url} alt={`Matching photo ${i + 1}`} loading="lazy"
                        className="h-full w-full object-cover transition duration-500 group-hover:scale-105" />
                      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-3 pt-10">
                        {img.score !== undefined && (
                          <>
                            <div className="mb-1.5 flex items-center justify-between text-xs">
                              <span className="text-white/60">Match</span>
                              <span className="font-semibold text-white">{(img.score * 100).toFixed(1)}%</span>
                            </div>
                            <div className="h-1 overflow-hidden rounded-full bg-white/15">
                              <div className="lm-grad h-full rounded-full"
                                style={{ width: `${Math.min(100, Math.max(0, img.score * 100))}%` }} />
                            </div>
                          </>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </main>
        </div>
      </div>

      {cameraOpen && (
        <CameraModal
          onClose={() => setCameraOpen(false)}
          onCapture={(f) => { acceptFile(f); setCameraOpen(false); }}
        />
      )}

      {lightbox !== null && (
        <Lightbox items={results} index={lightbox} setIndex={setLightbox} onClose={() => setLightbox(null)} />
      )}
    </div>
  );
}
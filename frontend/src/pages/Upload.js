import { useState, useRef } from "react";
import { Upload as UploadIcon, FileVideo, Activity, AlertTriangle, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import { api } from "@/lib/api";

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [drag, setDrag] = useState(false);
  const inputRef = useRef(null);

  const onSelect = (f) => {
    if (!f) return;
    setFile(f);
    setResult(null);
  };

  const onAnalyze = async () => {
    if (!file) {
      toast.error("Choose a video first");
      return;
    }
    setLoading(true);
    try {
      const r = await api.analyzeBiomech(null, file);
      setResult(r);
      toast.success("Biomech analysis complete");
    } catch (e) {
      toast.error("Analysis failed");
    } finally { setLoading(false); }
  };

  return (
    <div>
      <div className="overline text-white/40">Biomech Lab</div>
      <h1 className="font-display text-5xl font-black uppercase tracking-tighter mt-1 mb-2">Swing Analyzer</h1>
      <p className="text-white/50 text-sm mb-8 max-w-2xl">
        Upload a side-on or center-field swing clip. We extract elite kinematic features and return a biomech score,
        MLB comp, and prescriptive drills.
      </p>

      <div className={`grid gap-6 ${result ? "lg:grid-cols-5" : ""}`}>
        {/* Dropzone */}
        <div className={`${result ? "lg:col-span-2" : ""} surface p-6`}>
          <div
            onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => { e.preventDefault(); setDrag(false); onSelect(e.dataTransfer.files[0]); }}
            onClick={() => inputRef.current?.click()}
            className={`border-2 border-dashed cursor-pointer transition-all duration-150 p-12 text-center ${
              drag ? "border-[#007AFF] bg-[#007AFF]/5" : "border-white/15 hover:border-white/30"
            }`}
            data-testid="upload-dropzone"
          >
            <input
              ref={inputRef}
              type="file"
              accept="video/*"
              className="hidden"
              onChange={(e) => onSelect(e.target.files[0])}
              data-testid="upload-file-input"
            />
            {file ? (
              <div className="space-y-2">
                <FileVideo className="w-10 h-10 mx-auto text-[#007AFF]" />
                <div className="font-semibold">{file.name}</div>
                <div className="text-xs text-white/40">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
              </div>
            ) : (
              <div className="space-y-2">
                <UploadIcon className="w-10 h-10 mx-auto text-white/40" />
                <div className="font-semibold">Drop a swing clip here</div>
                <div className="text-xs text-white/50">or click to browse · .mp4, .mov, .webm</div>
              </div>
            )}
          </div>

          <button
            onClick={onAnalyze}
            disabled={!file || loading}
            data-testid="analyze-btn"
            className="mt-4 w-full inline-flex items-center justify-center gap-2 bg-[#007AFF] hover:bg-[#005bb5] disabled:opacity-40 text-white py-3 font-semibold transition-colors"
          >
            <Activity className="w-4 h-4" />
            {loading ? "Analyzing kinematics…" : "Run Biomech Analysis"}
          </button>

          {loading && (
            <div className="mt-4 font-mono text-[11px] text-white/50 space-y-0.5">
              <div>&gt; extracting pose landmarks (33 keypoints, 3D world)…</div>
              <div>&gt; isolating swing window, computing kinematics…</div>
              <div>&gt; benchmarking vs elite swing profile (z-scores)…</div>
              <div className="text-[#32D74B]">&gt; nearest-neighbor MLB comp…</div>
            </div>
          )}
        </div>

        {/* Results */}
        {result && (
          <div className="lg:col-span-3 space-y-4 fade-up">
            <div className="surface p-6">
              <div className="grid sm:grid-cols-3 gap-6">
                <div>
                  <div className="overline text-white/40 mb-1">Biomech Score</div>
                  <div className="font-display text-6xl font-black tabular" style={{ color: result.score >= 80 ? "#32D74B" : result.score >= 65 ? "#007AFF" : "#FF453A" }}>
                    {result.score}
                  </div>
                </div>
                <div>
                  <div className="overline text-white/40 mb-1">MLB Comp</div>
                  <div className="font-display text-2xl font-bold uppercase text-[#D4A437]">{result.mlb_comp}</div>
                  <div className="text-xs text-white/50 mt-1 tabular">{Math.round(result.similarity * 100)}% similarity</div>
                </div>
                <div>
                  <div className="overline text-white/40 mb-1">Diagnoses</div>
                  <div className="font-display text-2xl font-bold">
                    {result.diagnoses?.length || 0} <span className="text-white/40 text-sm">flags</span>
                  </div>
                  <div className="text-xs text-[#32D74B] mt-1">{result.strengths?.length || 0} strengths</div>
                </div>
              </div>
            </div>

            <div className="surface p-6">
              <div className="overline text-white/40 mb-4">Feature Breakdown</div>
              <div className="space-y-2">
                {Object.entries(result.feature_scores || {}).map(([k, v]) => (
                  <div key={k} className="grid grid-cols-12 items-center gap-2 py-1.5">
                    <div className="col-span-4 text-[11px] uppercase tracking-widest text-white/60">{k.replace(/_/g, " ")}</div>
                    <div className="col-span-3 tabular text-sm font-semibold">{v.value}{typeof v.value === "number" && k.includes("speed") ? " mph" : ""}</div>
                    <div className="col-span-3 tabular text-xs text-white/40">elite: {v.elite_avg}</div>
                    <div className={`col-span-2 tabular text-sm text-right font-semibold ${Math.abs(v.z_score) > 1 ? "text-[#FF453A]" : "text-[#32D74B]"}`}>
                      z = {v.z_score > 0 ? "+" : ""}{v.z_score}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {result.diagnoses?.length > 0 && (
              <div className="surface p-6">
                <div className="overline text-white/40 mb-4 flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> Diagnostics</div>
                <div className="space-y-3">
                  {result.diagnoses.map((d, i) => (
                    <div key={i} className="border border-white/10 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="pill" style={{
                          backgroundColor: d.severity === "critical" ? "rgba(255,69,58,0.15)" : "rgba(212,164,55,0.15)",
                          color: d.severity === "critical" ? "#FF453A" : "#D4A437",
                          border: `1px solid ${d.severity === "critical" ? "rgba(255,69,58,0.4)" : "rgba(212,164,55,0.4)"}`,
                        }}>{d.severity}</span>
                        <span className="text-[10px] text-white/40 uppercase tracking-widest">{d.feature.replace(/_/g, " ")}</span>
                      </div>
                      <p className="text-sm text-white/85">{d.message}</p>
                      <div className="mt-2 text-xs text-[#FF453A]">Estimated cost: {d.estimated_cost}</div>
                      <div className="mt-1 text-xs text-[#32D74B]"><span className="font-bold">FIX:</span> {d.fix}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.strengths?.length > 0 && (
              <div className="surface p-6 border-[#32D74B]/30">
                <div className="overline text-[#32D74B] mb-3 flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> Strengths</div>
                {result.strengths.map((s, i) => (
                  <div key={i} className="text-sm text-white/80 py-0.5">• {s.message}</div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

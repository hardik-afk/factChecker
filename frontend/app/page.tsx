"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Shield, Clock, AlertTriangle } from "lucide-react";
import { VibeInput } from "@/components/vibe-input";
import { TruthMeter } from "@/components/truth-meter";
import { RedFlagHighlighter } from "@/components/red-flag-highlighter";
import { ReasoningCard } from "@/components/reasoning-card";

// Mock History
const mockHistory = [
  { id: 1, text: "SpaceX successfully launches Starship system", score: 85, time: "2 hrs ago" },
  { id: 2, text: "Aliens land in Times Square", score: 10, time: "5 hrs ago" },
];

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [originalText, setOriginalText] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async (fd: FormData) => {
    setLoading(true);
    setError(null);
    setResult(null);

    // Save text to highlight later
    const textEntry = fd.get("text");
    if (textEntry && typeof textEntry === "string") setOriginalText(textEntry);
    else setOriginalText("Screenshot uploaded for analysis.");

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${apiUrl}/analyze`, {
        method: "POST",
        body: fd,
      });

      if (!res.ok) {
        throw new Error(await res.text());
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze vibe. Ensure the FastAPI server is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-80 border-r border-white/10 p-6 flex flex-col glass-card bg-black/10 hidden md:flex">
        <div className="flex items-center gap-3 mb-10 decoration-teal-500">
          <Shield className="w-8 h-8 text-teal-400" />
          <h1 className="text-2xl font-black tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-teal-300 to-emerald-400 drop-shadow-sm">VeriVibe</h1>
        </div>
        
        <h2 className="text-sm uppercase tracking-widest text-slate-400 mb-4 font-bold flex items-center gap-2">
          <Clock className="w-4 h-4" /> History
        </h2>
        
        <div className="flex flex-col gap-3">
          {mockHistory.map((item) => (
            <div key={item.id} className="p-3 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 transition cursor-pointer">
              <p className="text-sm truncate text-slate-200 mb-2">{item.text}</p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-400">{item.time}</span>
                <span className={`text-xs font-bold px-2 py-0.5 rounded ${item.score > 50 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>{item.score}%</span>
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-6 lg:p-12">
        <div className="max-w-5xl mx-auto space-y-8">
          
          <header className="mb-8">
            <h2 className="text-4xl font-extrabold tracking-tight text-white mb-3">Vibe Check</h2>
            <p className="text-slate-400 text-lg">Cross-verify claims against live news, spot hidden bias, and get a transparent integrity score instantly.</p>
          </header>

          <VibeInput onSubmit={handleSubmit} isLoading={loading} />

          {error && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="p-4 bg-red-500/10 border border-red-500/30 text-red-300 rounded-xl flex items-center gap-3">
              <AlertTriangle className="w-5 h-5" />
              {error}
            </motion.div>
          )}

          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div
                key="loading-skeleton"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col items-center justify-center py-16 space-y-6"
              >
                <div className="relative w-24 h-24 mb-4">
                  <div className="absolute inset-0 border-4 border-teal-500/20 rounded-full"></div>
                  <div className="absolute inset-0 border-4 border-teal-400 border-t-transparent rounded-full animate-spin shadow-[0_0_30px_rgba(45,212,191,0.5)]"></div>
                  <Shield className="absolute inset-0 m-auto w-8 h-8 text-teal-400 animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-teal-300 to-emerald-200">
                  Orchestrating agents... searching the web...
                </h3>
                <p className="text-slate-400 max-w-md text-center">
                  Our AI pipeline is currently checking high-authority sources and hunting for sensationalism patterns.
                </p>
              </motion.div>
            ) : result ? (
              <motion.div
                key="results"
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ duration: 0.5, staggerChildren: 0.1 }}
                className="grid grid-cols-1 lg:grid-cols-12 gap-6 pt-4"
              >
                <div className="col-span-1 lg:col-span-5 flex flex-col gap-6">
                   <TruthMeter score={result.vibe_score} />
                   <ReasoningCard 
                      explanation={result.ai_explanation}
                      verificationVibe={result.verification_vibe}
                      isConfirmed={result.is_confirmed}
                      sources={result.top_sources}
                   />
                </div>
                
                <div className="col-span-1 lg:col-span-7">
                  <RedFlagHighlighter text={originalText} flags={result.red_flags} />
                </div>
              </motion.div>
            ) : null}
          </AnimatePresence>
          
        </div>
      </main>
    </div>
  );
}

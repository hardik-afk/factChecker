"use client";

import { useState } from "react";
import { Send, UploadCloud, AlertCircle } from "lucide-react";

export function VibeInput({ onSubmit, isLoading }: { onSubmit: (data: FormData) => void, isLoading: boolean }) {
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text && !file) return;

    const fd = new FormData();
    if (text) fd.append("text", text);
    if (file) fd.append("file", file);
    onSubmit(fd);
  };

  return (
    <div className="glass-card rounded-3xl p-6 shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste a viral headline or news snippet here..."
          className="w-full h-32 bg-white/5 border border-white/10 rounded-xl p-4 text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-teal-500/50 resize-none transition-all"
        />

        <div className="flex items-center gap-4">
          <div className="relative flex-1 group">
            <input 
              type="file" 
              accept="image/png, image/jpeg" 
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            <div className="flex items-center justify-center gap-2 border-2 border-dashed border-white/20 rounded-xl p-3 bg-white/5 group-hover:bg-white/10 group-hover:border-teal-500/50 transition-colors">
              <UploadCloud className="w-5 h-5 text-teal-400" />
              <span className="text-sm font-medium text-slate-300">
                {file ? file.name : "Drop a screenshot here (PNG/JPG)"}
              </span>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading || (!text && !file)}
            className="bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-400 hover:to-emerald-500 disabled:opacity-50 disabled:cursor-wait text-white font-bold py-3 px-8 rounded-xl flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(20,184,166,0.5)] transition-all"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin"></div>
                Analyzing...
              </>
            ) : (
              <>
                Check Vibe
                <Send className="w-4 h-4 ml-1" />
              </>
            )}
          </button>
        </div>

        {file && (
          <div className="flex items-center gap-2 text-xs text-yellow-400/80 mt-2 bg-yellow-500/10 p-2 rounded-lg">
            <AlertCircle className="w-4 h-4" />
            <p><strong>Privacy Check:</strong> Your image will be securely processed by Gemini Vision and discarded immediately. Please ensure no PII is visible.</p>
          </div>
        )}

      </form>
    </div>
  );
}

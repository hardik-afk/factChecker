"use client";

import { ShieldCheck, ShieldAlert, Sparkles, Globe } from "lucide-react";
import { Badge } from "./ui/badge";

interface Source {
  name: string;
  url: string;
}

interface ReasoningCardProps {
  explanation: string;
  verificationVibe: string;
  isConfirmed: boolean;
  sources: Source[];
}

export function ReasoningCard({ explanation, verificationVibe, isConfirmed, sources }: ReasoningCardProps) {
  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      <div className="space-y-3">
        <h3 className="text-xl font-bold flex items-center gap-2 tracking-wide text-white">
          <Sparkles className="w-5 h-5 text-purple-400" />
          AI Reasoning
        </h3>
        <p className="text-slate-300 leading-relaxed bg-black/20 p-4 rounded-xl">
          {explanation}
        </p>
      </div>

      <div className="space-y-3 border-t border-white/10 pt-4">
        <h3 className="text-lg font-bold flex items-center justify-between tracking-wide text-white">
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-blue-400" />
            Live Web Verification
          </div>
          {isConfirmed ? (
            <div className="flex items-center gap-1 text-xs px-2 py-1 bg-green-500/20 text-green-300 rounded border border-green-500/30">
              <ShieldCheck className="w-3 h-3" /> Confirmed
            </div>
          ) : (
            <div className="flex items-center gap-1 text-xs px-2 py-1 bg-red-500/20 text-red-300 rounded border border-red-500/30">
              <ShieldAlert className="w-3 h-3" /> Unsubstantiated
            </div>
          )}
        </h3>
        <p className="text-slate-300 text-sm italic">
          "{verificationVibe}"
        </p>
        
        {sources && sources.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {sources.map((src, i) => (
              <a 
                key={i} 
                href={src.url} 
                target="_blank" 
                rel="noreferrer"
                className="text-xs bg-white/5 hover:bg-white/10 border border-white/20 px-3 py-1.5 rounded-full transition-colors flex items-center gap-1 text-blue-200"
              >
                {src.name}
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

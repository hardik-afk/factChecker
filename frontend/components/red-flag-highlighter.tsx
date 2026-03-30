"use client";

import { Tooltip, TooltipContent, TooltipTrigger } from "./ui/tooltip";

interface RedFlagHighlighterProps {
  text: string;
  flags: string[];
}

export function RedFlagHighlighter({ text, flags }: RedFlagHighlighterProps) {
  if (!text) return null;
  if (!flags || flags.length === 0) {
    return <p className="text-slate-300 leading-relaxed max-h-64 overflow-auto p-4">{text}</p>;
  }

  // Simple parser: Split text by flags (case insensitive)
  const regexPattern = new RegExp(`(${flags.join("|")})`, "gi");
  const parts = text.split(regexPattern);

  // A tiny helper to categorize why it was flagged based on config hints
  const getFlagCat = (fw: string) => {
    const f = fw.toLowerCase();
    if (["unbelievable", "shocking", "bombshell", "jaw-dropping", "destroy"].includes(f)) return "Sensationalism";
    if (["secret revealed", "you won't believe", "doctors hate"].includes(f)) return "Clickbait";
    return "Potential Bias";
  };

  return (
    <div className="glass-card rounded-2xl p-6 text-slate-200">
      <h3 className="text-xl font-bold mb-4 tracking-wide text-white">Red Flag Analysis</h3>
      <div className="leading-relaxed bg-black/20 p-4 rounded-xl max-h-64 overflow-y-auto">
        {parts.map((part, index) => {
          const isFlag = flags.find((f) => f.toLowerCase() === part.toLowerCase());
          
          if (isFlag) {
            const cat = getFlagCat(part);
            const colorClass = cat === "Sensationalism" 
              ? "bg-red-500/30 text-red-200 border-red-500/50" 
              : "bg-yellow-500/30 text-yellow-200 border-yellow-500/50";
              
            return (
              <Tooltip key={index}>
                <TooltipTrigger asChild>
                  <span className={`px-1 rounded border cursor-help ${colorClass} transition-colors hover:bg-opacity-50`}>
                    {part}
                  </span>
                </TooltipTrigger>
                <TooltipContent side="top" className="bg-slate-900 border-white/20 text-white">
                  <p className="font-semibold">{cat}</p>
                </TooltipContent>
              </Tooltip>
            );
          }
          return <span key={index}>{part}</span>;
        })}
      </div>
    </div>
  );
}

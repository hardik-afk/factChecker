"use client";

import { motion } from "framer-motion";

interface TruthMeterProps {
  score: number;
}

export function TruthMeter({ score }: TruthMeterProps) {
  // Map 0-100 to an SVG arc (half circle = from 0 to 180 degrees)
  // For a circle with r=50, circumference is 2*pi*50 = 314
  // Half circle is 157
  const radius = 50;
  const circumference = Math.PI * radius;
  
  // Calculate stroke dash offset
  const progress = score / 100;
  const strokeDashoffset = circumference - progress * circumference;

  let color = "stroke-red-500";
  let label = "Unreliable";
  if (score >= 40) {
    color = "stroke-yellow-400";
    label = "Mixed";
  }
  if (score >= 70) {
    color = "stroke-green-400";
    label = "Reliable";
  }

  return (
    <div className="flex flex-col items-center justify-center p-6 glass-card rounded-2xl relative">
      <h3 className="text-xl font-bold mb-4 tracking-wide text-white">Truth Meter</h3>
      
      <div className="relative w-48 h-28 overflow-hidden flex justify-center">
        <svg
          viewBox="0 0 120 60"
          className="w-full h-full drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]"
        >
          {/* Background Arc */}
          <path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="12"
            strokeLinecap="round"
          />
          {/* Animated Foreground Arc */}
          <motion.path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            className={`${color} glow-stroke`}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        </svg>

        {/* Score Readout */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 flex flex-col items-center">
          <motion.span 
            className="text-4xl font-extrabold"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
          >
            {Math.round(score)}%
          </motion.span>
        </div>
      </div>
      
      <motion.div 
        className="mt-2 text-sm uppercase tracking-widest font-semibold text-slate-300"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        {label}
      </motion.div>
    </div>
  );
}

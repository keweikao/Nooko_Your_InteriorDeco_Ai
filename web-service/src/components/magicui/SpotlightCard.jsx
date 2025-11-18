import { useState, useRef } from "react";
import { cn } from "@/lib/utils";

export function SpotlightCard({ title, description, icon, children, className }) {
  const cardRef = useRef(null);
  const [spotlight, setSpotlight] = useState({ x: 50, y: 50 });

  const handleMouseMove = (event) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 100;
    const y = ((event.clientY - rect.top) / rect.height) * 100;
    setSpotlight({ x, y });
  };

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      className={cn(
        "group relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-slate-900 via-slate-900/80 to-slate-900/60 p-6 text-white shadow-2xl transition-transform hover:-translate-y-1",
        className
      )}
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-0 transition duration-300 group-hover:opacity-100"
        style={{
          background: `radial-gradient(circle at ${spotlight.x}% ${spotlight.y}%, rgba(59,130,246,0.25), transparent 45%)`
        }}
      />
      <div className="relative flex flex-col space-y-4">
        <div className="flex items-center gap-3">
          {icon && <div className="rounded-full bg-white/10 p-2 text-xl">{icon}</div>}
          <div>
            <h3 className="text-lg font-semibold tracking-tight">{title}</h3>
            <p className="text-sm text-slate-300">{description}</p>
          </div>
        </div>
        <div className="text-slate-200">{children}</div>
      </div>
    </div>
  );
}

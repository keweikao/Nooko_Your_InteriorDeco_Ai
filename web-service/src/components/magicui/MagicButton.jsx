import { cn } from "@/lib/utils";

export function MagicButton({ children, className, ...props }) {
  return (
    <button
      className={cn(
        "relative inline-flex items-center justify-center rounded-full border border-white/20 bg-gradient-to-r from-indigo-500 via-sky-500 to-purple-500 px-6 py-2 text-sm font-semibold text-white shadow-[0_10px_40px_rgba(79,70,229,0.35)] transition-transform hover:-translate-y-0.5",
        "before:absolute before:inset-[2px] before:rounded-full before:bg-slate-900/60 before:content-['']",
        "after:absolute after:-inset-1 after:rounded-full after:border after:border-white/30 after:opacity-0 after:transition-all hover:after:opacity-100",
        className
      )}
      {...props}
    >
      <span className="relative flex items-center gap-2 text-[15px] uppercase tracking-wide">
        {children}
        <span className="h-1 w-1 animate-ping rounded-full bg-white/70" />
      </span>
    </button>
  );
}

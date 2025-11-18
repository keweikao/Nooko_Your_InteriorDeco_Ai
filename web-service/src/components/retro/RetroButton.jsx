import { cn } from "@/lib/utils";

export function RetroButton({ children, className, ...props }) {
  return (
    <button
      className={cn(
        "group relative inline-flex items-center justify-center rounded-[1.6rem] border-4 border-black bg-[#FEEA36] px-8 py-3 text-lg font-black uppercase tracking-[0.2em] text-black shadow-[6px_6px_0_0_#000]",
        "transition active:translate-y-1 active:shadow-[3px_3px_0_0_#000]",
        className
      )}
      {...props}
    >
      <span className="absolute -inset-1 translate-y-1 rounded-[1.9rem] border-4 border-black bg-[#FF7B54] opacity-0 transition group-hover:opacity-100" />
      <span className="relative flex items-center gap-2">
        {children}
        <span className="text-sm">★</span>
      </span>
    </button>
  );
}

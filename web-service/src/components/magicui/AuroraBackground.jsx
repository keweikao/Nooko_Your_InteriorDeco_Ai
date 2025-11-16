import { cn } from "@/lib/utils";

export function AuroraBackground({ children, className }) {
  return (
    <div className={cn("relative overflow-hidden rounded-3xl bg-slate-950 text-white", className)}>
      <div className="pointer-events-none absolute inset-0 opacity-80">
        <div className="absolute -left-20 top-10 h-72 w-72 rounded-full bg-fuchsia-500/40 blur-3xl" />
        <div className="absolute right-0 top-0 h-96 w-72 rounded-full bg-sky-500/40 blur-[120px]" />
        <div className="absolute bottom-0 left-1/3 h-48 w-96 rounded-full bg-emerald-400/30 blur-3xl" />
      </div>
      <div className="relative z-10 flex flex-col gap-4 p-8 text-base">{children}</div>
    </div>
  );
}

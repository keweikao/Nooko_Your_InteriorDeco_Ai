import { cn } from "@/lib/utils";

export function BentoGrid({ children, className }) {
  return (
    <div className={cn("grid gap-4 md:grid-cols-2 lg:grid-cols-3", className)}>
      {children}
    </div>
  );
}

export function BentoCard({ title, description, footer, className, children }) {
  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-2xl border border-white/10 bg-slate-900/70 p-5 text-white shadow-lg transition hover:-translate-y-1 hover:border-white/30",
        className
      )}
    >
      <div className="pointer-events-none absolute inset-px rounded-[1.1rem] border border-white/5 bg-gradient-to-br from-white/5 to-transparent opacity-0 transition group-hover:opacity-100" />
      <div className="relative z-10 flex flex-col space-y-3">
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">{footer}</p>
          <h4 className="text-lg font-semibold tracking-tight">{title}</h4>
          <p className="mt-1 text-sm text-slate-300">{description}</p>
        </div>
        {children}
      </div>
    </div>
  );
}

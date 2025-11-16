import { cn } from "@/lib/utils";

export function RetroCard({ title, description, children, className }) {
  return (
    <div
      className={cn(
        "relative rounded-3xl border-4 border-black bg-[#FDF5E6] p-6 text-black shadow-[8px_8px_0_0_#000]",
        className
      )}
    >
      <div className="absolute inset-x-6 top-4 h-3 rounded-full border-2 border-black bg-[#FF7B54]" />
      <div className="relative mt-6 flex flex-col gap-3">
        <h4 className="text-2xl font-black tracking-wide">{title}</h4>
        <p className="text-base font-medium text-slate-800">{description}</p>
        <div className="text-sm text-slate-700">{children}</div>
      </div>
    </div>
  );
}

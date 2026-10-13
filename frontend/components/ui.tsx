import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";

const VARIANTS: Record<Variant, string> = {
  primary:
    "bg-gradient-to-r from-sky-500 via-blue-500 to-violet-500 text-white shadow-[0_8px_30px_-8px_rgb(59_130_246/0.6)] hover:brightness-110 disabled:from-slate-700 disabled:via-slate-700 disabled:to-slate-700 disabled:text-slate-400 disabled:shadow-none",
  secondary:
    "bg-white/[0.04] text-slate-200 ring-1 ring-inset ring-white/10 hover:bg-white/[0.08] hover:ring-white/20 disabled:text-slate-500 disabled:hover:bg-white/[0.04]",
  ghost: "text-slate-400 hover:text-slate-100 hover:bg-white/[0.05] disabled:text-slate-600 disabled:hover:bg-transparent",
  danger: "bg-rose-500/10 text-rose-200 ring-1 ring-inset ring-rose-400/30 hover:bg-rose-500/20",
};

export function Button({
  variant = "secondary",
  size = "md",
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: "h-8 px-2.5 text-xs gap-1.5", md: "h-9 px-3.5 text-sm gap-2", lg: "h-12 px-6 text-[15px] gap-2.5" };
  return (
    <button
      type="button"
      className={`inline-flex shrink-0 items-center justify-center rounded-lg font-medium transition duration-150 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-sky-400 disabled:cursor-not-allowed ${sizes[size]} ${VARIANTS[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function Panel({
  eyebrow,
  title,
  actions,
  children,
  className = "",
  bodyClassName = "p-5",
}: {
  eyebrow?: string;
  title?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}) {
  return (
    <section className={`panel min-w-0 ${className}`}>
      {(eyebrow || title || actions) && (
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-5 py-3.5">
          <div className="min-w-0">
            {eyebrow && <div className="eyebrow">{eyebrow}</div>}
            {title && <h2 className="mt-0.5 truncate text-[15px] font-semibold text-slate-100">{title}</h2>}
          </div>
          {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
        </header>
      )}
      <div className={bodyClassName}>{children}</div>
    </section>
  );
}

export function Badge({ children, tone = "slate", className = "" }: { children: ReactNode; tone?: string; className?: string }) {
  const tones: Record<string, string> = {
    slate: "bg-white/[0.05] text-slate-300 ring-white/10",
    sky: "bg-sky-400/10 text-sky-200 ring-sky-400/25",
    violet: "bg-violet-400/10 text-violet-200 ring-violet-400/25",
    emerald: "bg-emerald-400/10 text-emerald-200 ring-emerald-400/25",
    amber: "bg-amber-400/10 text-amber-200 ring-amber-400/30",
    rose: "bg-rose-400/10 text-rose-200 ring-rose-400/30",
  };
  return (
    <span className={`inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-medium ring-1 ring-inset ${tones[tone]} ${className}`}>
      {children}
    </span>
  );
}

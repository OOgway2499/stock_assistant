import { clsx } from "clsx";

type Variant = "success" | "danger" | "warning" | "neutral" | "purple";

const variants: Record<Variant, string> = {
    success: "bg-green-500/15 text-green-400 border-green-500/30",
    danger: "bg-red-500/15 text-red-400 border-red-500/30",
    warning: "bg-yellow-500/15 text-yellow-400 border-yellow-500/30",
    neutral: "bg-gray-500/15 text-gray-400 border-gray-500/30",
    purple: "bg-purple-500/15 text-purple-400 border-purple-500/30",
};

export default function Badge({
    children,
    variant = "neutral",
}: {
    children: React.ReactNode;
    variant?: Variant;
}) {
    return (
        <span
            className={clsx(
                "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium",
                variants[variant]
            )}
        >
            {children}
        </span>
    );
}

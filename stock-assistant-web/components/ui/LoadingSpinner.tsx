export default function LoadingSpinner({ size = "md" }: { size?: "sm" | "md" | "lg" }) {
    const sizeClass = { sm: "h-4 w-4", md: "h-6 w-6", lg: "h-10 w-10" }[size];
    return (
        <div className={`${sizeClass} animate-spin rounded-full border-2 border-gray-600 border-t-blue-500`} />
    );
}

export function TypingIndicator() {
    return (
        <div className="flex items-center gap-3 px-4 py-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/20 text-sm">
                🤖
            </div>
            <div className="flex items-center gap-1.5">
                <div className="h-2 w-2 rounded-full bg-purple-400 dot-1" />
                <div className="h-2 w-2 rounded-full bg-purple-400 dot-2" />
                <div className="h-2 w-2 rounded-full bg-purple-400 dot-3" />
            </div>
            <span className="text-sm text-gray-400">Analyzing...</span>
        </div>
    );
}

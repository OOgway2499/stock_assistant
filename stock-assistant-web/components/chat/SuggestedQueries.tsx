"use client";

const QUERIES = [
    "How is Nifty 50 today?",
    "Analyse Reliance",
    "Top gainers today",
    "Compare TCS vs Infosys",
    "Latest market news",
    "IT sector performance",
];

interface Props {
    onSelect: (query: string) => void;
    visible: boolean;
}

export default function SuggestedQueries({ onSelect, visible }: Props) {
    if (!visible) return null;

    return (
        <div className="flex flex-wrap justify-center gap-2 px-4 py-2">
            {QUERIES.map((q) => (
                <button
                    key={q}
                    onClick={() => onSelect(q)}
                    className="rounded-full border border-gray-700 bg-gray-800/50 px-3 py-1.5 text-xs text-gray-300 transition-all hover:border-blue-500/50 hover:bg-blue-500/10 hover:text-blue-300"
                >
                    {q}
                </button>
            ))}
        </div>
    );
}

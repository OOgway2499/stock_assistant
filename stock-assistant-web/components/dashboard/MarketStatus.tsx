"use client";
import Badge from "@/components/ui/Badge";

export default function MarketStatus({ status }: { status: string }) {
    const isOpen = status?.toLowerCase() === "open";
    return (
        <Badge variant={isOpen ? "success" : "danger"}>
            <span className={`inline-block h-2 w-2 rounded-full ${isOpen ? "bg-green-400 live-pulse" : "bg-red-400"}`} />
            {isOpen ? "Market Open" : "Market Closed"}
        </Badge>
    );
}

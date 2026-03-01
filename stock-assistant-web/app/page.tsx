"use client";
import { useState } from "react";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";
import ChatWindow from "@/components/chat/ChatWindow";
import MarketOverview from "@/components/dashboard/MarketOverview";
import GainersLosers from "@/components/dashboard/GainersLosers";
import SectorPerformance from "@/components/dashboard/SectorPerformance";
import LoadingSpinner from "@/components/ui/LoadingSpinner";
import { useMarketData } from "@/hooks/useMarketData";
import { MessageSquare, BarChart3, Star } from "lucide-react";

export default function Home() {
  const { marketData, isLoading, lastUpdated, refetch } = useMarketData();
  const [externalQuery, setExternalQuery] = useState<string | null>(null);
  const [mobileTab, setMobileTab] = useState<"chat" | "market" | "watchlist">(
    "chat"
  );

  const handleQuery = (query: string) => {
    setExternalQuery(query);
    setMobileTab("chat");
  };

  return (
    <div className="flex h-screen flex-col overflow-hidden">
      {/* Header */}
      <Header
        marketStatus={marketData?.marketStatus || "closed"}
        onRefresh={refetch}
      />

      {/* Mobile Tab Bar */}
      <div className="flex border-b border-gray-800 lg:hidden">
        {[
          { key: "chat" as const, icon: MessageSquare, label: "Chat" },
          { key: "market" as const, icon: BarChart3, label: "Market" },
          { key: "watchlist" as const, icon: Star, label: "Watchlist" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setMobileTab(tab.key)}
            className={`flex flex-1 items-center justify-center gap-1.5 py-2.5 text-xs font-medium transition-all ${mobileTab === tab.key
                ? "border-b-2 border-blue-500 text-blue-400"
                : "text-gray-500"
              }`}
          >
            <tab.icon className="h-3.5 w-3.5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Main Content */}
      <main className="flex flex-1 overflow-hidden">
        {/* Left Sidebar — desktop only */}
        <div className="hidden lg:block">
          <Sidebar onQuery={handleQuery} />
        </div>

        {/* Center — Chat (main focus) */}
        <div
          className={`flex-1 ${mobileTab !== "chat" ? "hidden lg:flex" : "flex"
            } flex-col overflow-hidden`}
        >
          <ChatWindow
            externalQuery={externalQuery}
            onQueryConsumed={() => setExternalQuery(null)}
          />
        </div>

        {/* Right Panel — dashboard widgets */}
        <div
          className={`w-full lg:w-80 shrink-0 overflow-y-auto border-l border-gray-800 bg-[#0d1117] p-4 ${mobileTab === "market" ? "block" : "hidden lg:block"
            }`}
        >
          {isLoading && !marketData ? (
            <div className="flex h-full items-center justify-center">
              <LoadingSpinner size="lg" />
            </div>
          ) : (
            <div className="space-y-6">
              <MarketOverview indices={marketData?.indices || []} />

              <GainersLosers
                gainers={marketData?.gainers || []}
                losers={marketData?.losers || []}
                onStockClick={(sym) => handleQuery(`Analyse ${sym}`)}
              />

              <SectorPerformance indices={marketData?.indices || []} />

              {lastUpdated && (
                <p className="text-center text-[10px] text-gray-600">
                  Last updated:{" "}
                  {lastUpdated.toLocaleTimeString("en-IN", {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Mobile Watchlist Tab */}
        <div
          className={`w-full overflow-y-auto ${mobileTab === "watchlist" ? "block lg:hidden" : "hidden"
            }`}
        >
          <Sidebar onQuery={handleQuery} />
        </div>
      </main>
    </div>
  );
}

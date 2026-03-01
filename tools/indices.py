"""
Indices Tool — Market overview and sector performance from NSE India.
"""

from data_sources import nse_data


def get_market_overview() -> dict:
    """
    Get comprehensive market overview:
    Nifty 50, Bank Nifty, Nifty IT, top gainers, top losers, market status.

    Returns:
        dict with combined market data
    """
    try:
        overview = {}

        # Nifty 50
        nifty = nse_data.get_nifty50()
        overview["nifty_50"] = nifty

        # Bank Nifty & IT
        overview["nifty_bank"] = nse_data.get_index_data("NIFTY BANK")
        overview["nifty_it"] = nse_data.get_index_data("NIFTY IT")

        # Top gainers & losers (limit to 5 each)
        gainers = nse_data.get_top_gainers()
        losers = nse_data.get_top_losers()
        overview["top_gainers"] = gainers[:5] if isinstance(gainers, list) else gainers
        overview["top_losers"] = losers[:5] if isinstance(losers, list) else losers

        # Market status
        overview["market_status"] = nse_data.get_market_status()

        overview["data_source"] = "NSE India (real-time)"
        return overview

    except Exception as e:
        print(f"⚠️ [indices.get_market_overview] Error: {e}")
        return {"error": f"Market overview failed: {str(e)}"}


def get_nifty_sectors() -> dict:
    """
    Get performance of all major NSE sector indices.

    Returns:
        dict with sector-wise index data
    """
    try:
        sectors = [
            "NIFTY IT",
            "NIFTY BANK",
            "NIFTY PHARMA",
            "NIFTY FMCG",
            "NIFTY AUTO",
            "NIFTY METAL",
            "NIFTY REALTY",
            "NIFTY ENERGY",
        ]

        results = {}
        for sector in sectors:
            data = nse_data.get_index_data(sector)
            key = sector.lower().replace(" ", "_")
            results[key] = data

        results["data_source"] = "NSE India (real-time)"
        return results

    except Exception as e:
        print(f"⚠️ [indices.get_nifty_sectors] Error: {e}")
        return {"error": f"Sector data failed: {str(e)}"}

#!/usr/bin/env python3
"""
Enhanced zones_block.py with missing _send_retest_email function and improved error handling
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from robust_notifier import notifier

logger = logging.getLogger(__name__)

@dataclass
class Zone:
    """Trading zone data structure"""
    kind: str  # "supply" or "demand"
    entry: float
    stop: float
    target: float
    rr: float
    timestamp: str
    symbol: str

class ZoneManager:
    """Enhanced zone management with robust notifications"""

    def __init__(self):
        self.zones = {}  # symbol -> list of zones
        self.notifier = notifier

    def add_zone(self, symbol: str, zone: Zone):
        """Add a new trading zone"""
        if symbol not in self.zones:
            self.zones[symbol] = []

        self.zones[symbol].append(zone)
        logger.info(f"Added {zone.kind} zone for {symbol} at {zone.entry}")

    def check_zone_retest(self, symbol: str, current_price: float,
                         chart_path: Optional[Path] = None):
        """Check if price is retesting any zones"""
        if symbol not in self.zones:
            return

        for zone in self.zones[symbol]:
            if self._is_price_in_zone(current_price, zone):
                logger.info(f"Zone retest detected for {symbol} at {current_price}")
                self._send_retest_email(symbol, zone, chart_path)

    def _is_price_in_zone(self, price: float, zone: Zone) -> bool:
        """Check if price is within zone boundaries"""
        if zone.kind.lower() == "supply":
            # For supply zones, price should be below entry but above stop
            return zone.stop <= price <= zone.entry
        else:  # demand zone
            # For demand zones, price should be above entry but below stop
            return zone.entry <= price <= zone.stop

    def _send_retest_email(self, symbol: str, zone: Zone,
                          chart_path: Optional[Path] = None):
        """
        Send retest email notification

        This function was missing from the original zones_block.py and was causing crashes
        """
        try:
            # Format zone information
            zone_type = zone.kind.title()
            side_tag = "Long" if zone.kind.lower() == "demand" else "Short"

            # Calculate risk-reward ratio
            rr_value = getattr(zone, 'rr', 2.0)

            # Create email subject
            subject = f"ZoneSync RETEST · {symbol} · {side_tag} · {rr_value:.1f}R"

            # Create detailed email body
            body = self._format_retest_email_body(symbol, zone, side_tag)

            # Send notification with chart attachment if available
            chart_path_str = str(chart_path) if chart_path and chart_path.exists() else None

            success = self.notifier.send_alert(
                alert_type="RETEST",
                symbol=symbol,
                message=body,
                chart_path=chart_path_str
            )

            if success:
                logger.info(f"Retest email sent successfully for {symbol}")
            else:
                logger.error(f"Failed to send retest email for {symbol}")

        except Exception as e:
            logger.error(f"Error sending retest email for {symbol}: {e}")

    def _format_retest_email_body(self, symbol: str, zone: Zone, side_tag: str) -> str:
        """Format the email body for zone retest notifications"""

        current_time = logger.handlers[0].formatter.formatTime(
            logging.LogRecord("", 0, "", 0, "", (), None)
        ) if logger.handlers else "N/A"

        body = f"""
Zone Retest Alert

Pair: {symbol}
Strategy: ZoneSync
Zone Type: {zone.kind.title()}
Direction: {side_tag}
Retest Time: {current_time}

Trade Setup:
Entry: {zone.entry:.5f}
Stop Loss: {zone.stop:.5f}
Take Profit: {zone.target:.5f}
Risk/Reward: {zone.rr:.2f}R

Action Required:
Per trading plan, consider entry on FIRST retest with proper risk management.

Chart Analysis:
{f"Chart attached for detailed analysis." if hasattr(zone, 'chart_path') else "Chart analysis recommended before entry."}

Risk Management Reminder:
- Verify zone integrity before entry
- Confirm bias alignment with higher timeframes
- Use appropriate position sizing
- Monitor for signs of zone invalidation

This is an automated alert from ZoneSync FX Bot.
        """.strip()

        return body

    def send_zone_created_notification(self, symbol: str, zone: Zone,
                                     chart_path: Optional[Path] = None):
        """Send notification when a new zone is created"""
        try:
            side_tag = "Long Setup" if zone.kind.lower() == "demand" else "Short Setup"
            subject = f"ZoneSync NEW ZONE · {symbol} · {side_tag}"

            body = f"""
New Trading Zone Identified

Pair: {symbol}
Zone Type: {zone.kind.title()}
Entry Level: {zone.entry:.5f}
Stop Loss: {zone.stop:.5f}
Take Profit: {zone.target:.5f}
Risk/Reward: {zone.rr:.2f}R

Status: Waiting for retest entry signal

This zone will be monitored for retest opportunities.
            """.strip()

            chart_path_str = str(chart_path) if chart_path and chart_path.exists() else None

            self.notifier.send_alert(
                alert_type="NEW_ZONE",
                symbol=symbol,
                message=body,
                chart_path=chart_path_str
            )

        except Exception as e:
            logger.error(f"Error sending zone created notification for {symbol}: {e}")

    def cleanup_old_zones(self, max_age_hours: int = 24):
        """Remove zones older than specified hours"""
        # Implementation would depend on how timestamps are stored
        # This is a placeholder for zone cleanup logic
        pass

    def get_zone_summary(self) -> Dict[str, int]:
        """Get summary of current zones"""
        summary = {
            "total_zones": 0,
            "supply_zones": 0,
            "demand_zones": 0,
            "symbols_tracked": len(self.zones)
        }

        for symbol, zones in self.zones.items():
            summary["total_zones"] += len(zones)
            for zone in zones:
                if zone.kind.lower() == "supply":
                    summary["supply_zones"] += 1
                else:
                    summary["demand_zones"] += 1

        return summary

    def export_zones_to_csv(self, filepath: Path):
        """Export current zones to CSV file"""
        try:
            import pandas as pd

            zones_data = []
            for symbol, zones in self.zones.items():
                for zone in zones:
                    zones_data.append({
                        'symbol': symbol,
                        'kind': zone.kind,
                        'entry': zone.entry,
                        'stop': zone.stop,
                        'target': zone.target,
                        'rr': zone.rr,
                        'timestamp': zone.timestamp
                    })

            if zones_data:
                df = pd.DataFrame(zones_data)
                df.to_csv(filepath, index=False)
                logger.info(f"Exported {len(zones_data)} zones to {filepath}")
            else:
                logger.info("No zones to export")

        except Exception as e:
            logger.error(f"Error exporting zones to CSV: {e}")


# Global zone manager instance
zone_manager = ZoneManager()

# Convenience functions for backward compatibility
def _send_retest_email(symbol: str, zone: Zone, event_ts: str, chart_path: Path):
    """
    Backward compatibility function for the missing _send_retest_email

    This was the function that was missing and causing NameError crashes
    """
    zone_manager._send_retest_email(symbol, zone, chart_path)

def add_zone(symbol: str, kind: str, entry: float, stop: float, target: float,
             timestamp: str = None):
    """Add a new trading zone"""
    if timestamp is None:
        timestamp = logging.Formatter().formatTime(
            logging.LogRecord("", 0, "", 0, "", (), None)
        )

    rr = abs((target - entry) / (entry - stop)) if entry != stop else 1.0

    zone = Zone(
        kind=kind,
        entry=entry,
        stop=stop,
        target=target,
        rr=rr,
        timestamp=timestamp,
        symbol=symbol
    )

    zone_manager.add_zone(symbol, zone)
    return zone


if __name__ == "__main__":
    # Test the zone management system
    logging.basicConfig(level=logging.INFO)

    print("Testing Zone Management System...")

    # Test zone creation
    test_zone = add_zone("EUR/USD", "demand", 1.0500, 1.0480, 1.0540)
    print(f"Created test zone: {test_zone}")

    # Test retest detection
    zone_manager.check_zone_retest("EUR/USD", 1.0495)

    # Test zone summary
    summary = zone_manager.get_zone_summary()
    print(f"Zone summary: {summary}")

    print("Zone management system test completed.")
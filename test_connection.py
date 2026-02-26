"""
Quick test script to verify WebSocket connection and order book reconstruction
Run this first to make sure everything works!
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.orderbook.streamer import BinanceOrderBookStreamer
from src.orderbook.book import OrderBook


async def simple_test():
    """
    Simple test: Connect and display order book updates for 30 seconds
    """
    print("\n" + "="*70)
    print("TESTING BINANCE WEBSOCKET CONNECTION")
    print("="*70)
    print("This will stream BTC/USDT order book data for 30 seconds")
    print("You should see real-time price updates below")
    print("="*70 + "\n")
    
    update_counter = [0]  # Use list to avoid nonlocal issues
    
    async def display_callback(orderbook: OrderBook, message: dict):
        """Print order book state every 50 updates"""
        update_counter[0] += 1
        
        if update_counter[0] % 50 == 0:
            print(f"\n{'─'*70}")
            print(f"Update #{update_counter[0]} | {orderbook}")
            print(f"{'─'*70}")
            
            # Get top 5 levels
            bids, asks = orderbook.get_top_levels(5)
            
            # Calculate metrics
            mid_price = orderbook.get_mid_price()
            spread_abs, spread_pct = orderbook.get_spread()
            imbalance = orderbook.get_book_imbalance(5)
            
            # Display book state
            print(f"\n📊 Market Metrics:")
            print(f"   Mid Price:     ${mid_price:,.2f}")
            print(f"   Spread:        ${spread_abs:.2f} ({spread_pct*100:.4f}%)")
            print(f"   Imbalance:     {imbalance:+.4f} ({'BUY' if imbalance > 0 else 'SELL'} pressure)")
            
            # Display order book
            print(f"\n📕 Order Book (Top 5 Levels):")
            print(f"{'   BIDS (Buy Orders)':<35} | {'ASKS (Sell Orders)':>35}")
            print(f"   {'-'*33} | {'-'*35}")
            
            for i in range(5):
                bid_str = f"   ${bids[i][0]:,.2f}  |  {bids[i][1]:.4f} BTC" if i < len(bids) else "   " + " "*30
                ask_str = f"${asks[i][0]:,.2f}  |  {asks[i][1]:.4f} BTC" if i < len(asks) else " "*30
                print(f"{bid_str} | {ask_str:>35}")
            
            print(f"{'─'*70}\n")
    
    # Create streamer
    streamer = BinanceOrderBookStreamer(
        symbol="BTCUSDT",
        depth=20,
        update_speed="100ms"
    )
    
    print("⏳ Connecting to Binance WebSocket...\n")
    
    try:
        # Stream for 30 seconds
        await streamer.stream(callback=display_callback, duration=30)
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"Total updates received: {update_counter[0]}")
        print(f"Average update rate: {update_counter[0]/30:.1f} updates/second")
        print("="*70 + "\n")
        
        print("✓ Your WebSocket connection is working!")
        print("✓ Order book reconstruction is working!")
        print("\nYou're ready to start data collection! 🚀")
        print("\nNext steps:")
        print("  1. Run: python data/collector.py (to collect training data)")
        print("  2. Let it run for 24+ hours to get good data")
        print("  3. Then we'll build the feature engineering pipeline\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("  - Check your internet connection")
        print("  - Make sure Binance isn't blocked in your region")
        print("  - Try a different symbol (e.g., ETHUSDT)")


if __name__ == "__main__":
    print("\nStarting connection test...")
    print("Press Ctrl+C to stop early\n")
    
    try:
        asyncio.run(simple_test())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
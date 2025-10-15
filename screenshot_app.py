"""
Screenshot script for DimeDrop app using Playwright.
Captures screenshots of all app sections for UI review.
"""

import asyncio
import os
import time
from playwright.async_api import async_playwright
import subprocess
import signal
import sys


async def take_screenshots():
    """Take screenshots of all DimeDrop app sections."""

    # Create assets directory
    assets_dir = "/home/boonzy/Downloads/dimedrop/assets"
    os.makedirs(assets_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()

        try:
            # Navigate to the app
            print("🌐 Navigating to DimeDrop app...")
            await page.goto("http://localhost:3000", wait_until="domcontentloaded")
            await page.wait_for_load_state('networkidle', timeout=10000)
            await asyncio.sleep(3)  # Wait for Gradio to fully load

            # Take initial screenshot to see what we have
            await page.screenshot(path=f"{assets_dir}/00_initial_load.png", full_page=True)

            # Check what elements are on the page
            body_text = await page.inner_text('body')
            print(f"Page body contains: {body_text[:200]}...")

            # Try to find Gradio elements
            gradio_elements = await page.query_selector_all('.gradio-container, [class*="gradio"], button, .sidebar')
            print(f"Found {len(gradio_elements)} potential Gradio elements")

            # Wait for any interactive elements
            try:
                await page.wait_for_selector("button, input, .gradio-container", timeout=5000)
                print("✅ Found interactive elements")
            except:
                print("⚠️ No interactive elements found, taking basic screenshot")

            await asyncio.sleep(2)

            # Screenshot 1: Home page
            print("📸 Capturing Home page...")
            await page.screenshot(path=f"{assets_dir}/01_home_page.png", full_page=True)

            # Click Scan Card button
            print("🔍 Navigating to Scan Card...")
            scan_button = page.locator("button:has-text('📷 Scan Card')")
            await scan_button.click()
            await asyncio.sleep(1)
            await page.screenshot(path=f"{assets_dir}/02_scan_card.png", full_page=True)

            # Click Price Tracking button
            print("💰 Navigating to Price Tracking...")
            price_button = page.locator("button:has-text('💰 Price Tracking')")
            await price_button.click()
            await asyncio.sleep(1)
            await page.screenshot(path=f"{assets_dir}/03_price_tracking.png", full_page=True)

            # Click Sentiment Analysis button
            print("🧠 Navigating to Sentiment Analysis...")
            sentiment_button = page.locator("button:has-text('🧠 Sentiment Analysis')")
            await sentiment_button.click()
            await asyncio.sleep(1)
            await page.screenshot(path=f"{assets_dir}/04_sentiment_analysis.png", full_page=True)

            # Click Portfolio Management button
            print("📊 Navigating to Portfolio Management...")
            portfolio_button = page.locator("button:has-text('📊 Portfolio')")
            await portfolio_button.click()
            await asyncio.sleep(1)
            await page.screenshot(path=f"{assets_dir}/05_portfolio_management.png", full_page=True)

            # Test mobile view
            print("📱 Testing mobile responsiveness...")
            await page.set_viewport_size({"width": 375, "height": 667})
            await asyncio.sleep(1)
            await page.screenshot(path=f"{assets_dir}/06_mobile_view.png", full_page=True)

            # Test sidebar collapse (if toggle exists)
            print("🔄 Testing sidebar toggle...")
            try:
                toggle_button = page.locator("button:has-text('☰')")
                await toggle_button.click()
                await asyncio.sleep(1)
                await page.screenshot(path=f"{assets_dir}/07_sidebar_collapsed.png", full_page=True)
            except:
                print("Toggle button not found, skipping sidebar test")

            print("✅ All screenshots captured successfully!")
            print(f"📁 Screenshots saved to: {assets_dir}")

        except Exception as e:
            print(f"❌ Error during screenshot capture: {e}")
            # Take error screenshot
            await page.screenshot(path=f"{assets_dir}/error_screenshot.png", full_page=True)

        finally:
            await browser.close()


def start_app():
    """Start the DimeDrop app in background."""
    print("🚀 Starting DimeDrop app...")
    process = subprocess.Popen(
        ["python3", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/home/boonzy/Downloads/dimedrop"
    )
    return process


def stop_app(process):
    """Stop the DimeDrop app."""
    print("🛑 Stopping DimeDrop app...")
    try:
        process.terminate()
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


async def main():
    """Main function to run screenshot capture."""
    app_process = None

    try:
        # Start the app
        app_process = start_app()

        # Wait for app to start
        print("⏳ Waiting for app to start...")
        await asyncio.sleep(8)

        # Take screenshots
        await take_screenshots()

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # Stop the app
        if app_process:
            stop_app(app_process)

        print("🎉 Screenshot capture complete!")


if __name__ == "__main__":
    asyncio.run(main())

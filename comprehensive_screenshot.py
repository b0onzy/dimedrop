"""
Comprehensive screenshot script for DimeDrop app.
Captures screenshots of all sections using sidebar navigation.
"""

import asyncio
import os
import time
from playwright.async_api import async_playwright
import subprocess


assets_dir = "/home/boonzy/Downloads/dimedrop/assets"


async def take_comprehensive_screenshots():
    os.makedirs(assets_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()

        try:
            print("🌐 Connecting to DimeDrop app...")
            await page.goto("http://localhost:3000", timeout=60000)
            await page.wait_for_load_state('networkidle', timeout=20000)
            await asyncio.sleep(5)

            # Screenshot 1: Initial home page
            await page.screenshot(path=f"{assets_dir}/01_initial_home.png", full_page=True)
            print("✅ Initial home page captured")

            # Try to find sidebar navigation buttons
            nav_buttons = [
                ("🏠 Home", "02_home_section.png"),
                ("📷 Scan Card", "03_scan_card.png"),
                ("💰 Price Tracking", "04_price_tracking.png"),
                ("🧠 Sentiment Analysis", "05_sentiment_analysis.png"),
                ("📊 Portfolio", "06_portfolio.png")
            ]

            for button_text, filename in nav_buttons:
                try:
                    print(f"🔍 Looking for button: {button_text}")
                    # Try different selectors for the button
                    button = await page.query_selector(f'button:has-text("{button_text}")')
                    if button:
                        print(f"📸 Clicking {button_text}")
                        await button.click()
                        await asyncio.sleep(2)
                        await page.screenshot(path=f"{assets_dir}/{filename}", full_page=True)
                        print(f"✅ {filename} captured")
                    else:
                        print(f"❌ Button '{button_text}' not found")
                except Exception as e:
                    print(f"❌ Error with {button_text}: {e}")

            # Test mobile responsiveness
            print("📱 Testing mobile view...")
            await page.set_viewport_size({"width": 375, "height": 667})
            await asyncio.sleep(1)
            await page.screenshot(path=f"{assets_dir}/07_mobile_view.png", full_page=True)
            print("✅ Mobile view captured")

            # Test sidebar toggle if available
            print("🔄 Testing sidebar toggle...")
            try:
                toggle_button = await page.query_selector('button:has-text("☰")')
                if toggle_button:
                    await toggle_button.click()
                    await asyncio.sleep(1)
                    await page.screenshot(path=f"{assets_dir}/08_sidebar_collapsed.png", full_page=True)
                    print("✅ Collapsed sidebar captured")
                else:
                    print("ℹ️ No toggle button found")
            except Exception as e:
                print(f"❌ Error testing sidebar: {e}")

            print("🎉 All screenshots completed!")

        except Exception as e:
            print(f"❌ Error during screenshot capture: {e}")
            try:
                await page.screenshot(path=f"{assets_dir}/error_detailed.png", full_page=True)
            except:
                pass

        finally:
            await browser.close()


async def main():
    """Main function to run comprehensive screenshot capture."""
    app_process = None

    try:
        # Start the app
        print("🚀 Starting DimeDrop app...")
        app_process = subprocess.Popen(
            ["python3", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/home/boonzy/Downloads/dimedrop"
        )

        # Wait for app to start
        print("⏳ Waiting for app to start...")
        await asyncio.sleep(15)

        # Take comprehensive screenshots
        await take_comprehensive_screenshots()

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # Stop the app
        if app_process:
            print("🛑 Stopping DimeDrop app...")
            try:
                app_process.terminate()
                app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                app_process.kill()
                app_process.wait()

        print("🎉 Screenshot capture complete!")
        print(f"📁 Screenshots saved to: {assets_dir}")


if __name__ == "__main__":
    asyncio.run(main())

"""
Simple screenshot script for DimeDrop app.
"""

import asyncio
import os
import time
from playwright.async_api import async_playwright
import subprocess
import signal


async def take_screenshots():
    """Take basic screenshots."""

    assets_dir = "/home/boonzy/Downloads/dimedrop/assets"
    os.makedirs(assets_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            print("🌐 Connecting to app...")
            await page.goto("http://localhost:3000", timeout=30000)
            await asyncio.sleep(3)  # Wait for Gradio to load

            # Take screenshot of the main page
            await page.screenshot(path=f"{assets_dir}/app_main_page.png", full_page=True)
            print("✅ Main page screenshot saved!")

            # Try to find and click on different tabs
            tabs = await page.query_selector_all('button[data-testid*="tab"]')
            print(f"Found {len(tabs)} tabs")

            # Take screenshots of different sections if tabs are found
            for i, tab in enumerate(tabs[:5]):  # Limit to first 5 tabs
                try:
                    tab_text = await tab.inner_text()
                    print(f"📸 Clicking tab: {tab_text}")
                    await tab.click()
                    await asyncio.sleep(2)
                    await page.screenshot(path=f"{assets_dir}/tab_{i+1}_{tab_text.replace(' ', '_')}.png", full_page=True)
                except Exception as e:
                    print(f"❌ Error with tab {i}: {e}")

            print("✅ All screenshots captured!")

        except Exception as e:
            print(f"❌ Error: {e}")
            # Take error screenshot
            try:
                await page.screenshot(path=f"{assets_dir}/error_screenshot.png", full_page=True)
            except:
                pass

        finally:
            await browser.close()


async def main():
    """Main function."""
    # Start the app
    print("🚀 Starting DimeDrop app...")
    app_process = subprocess.Popen(
        ["python3", "app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd="/home/boonzy/Downloads/dimedrop"
    )

    try:
        # Wait for app to start
        print("⏳ Waiting for app to start...")
        await asyncio.sleep(8)

        # Take screenshots
        await take_screenshots()

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        # Stop the app
        print("🛑 Stopping app...")
        try:
            app_process.terminate()
            app_process.wait(timeout=5)
        except:
            app_process.kill()


if __name__ == "__main__":
    asyncio.run(main())

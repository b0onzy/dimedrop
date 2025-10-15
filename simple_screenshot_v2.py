"""
Simple screenshot script for DimeDrop app with better error handling.
"""

import asyncio
import os
import time
import subprocess
from playwright.async_api import async_playwright


async def check_app_ready(page, max_attempts=10):
    """Check if the app is ready by looking for Gradio elements."""
    for attempt in range(max_attempts):
        try:
            # Check for common Gradio elements
            gradio_elements = await page.query_selector('.gradio-container, .tabs, button')
            if gradio_elements:
                print(f"✅ App ready after {attempt + 1} attempts")
                return True
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2)
    return False


async def take_screenshots():
    """Take screenshots of the app."""

    assets_dir = "/home/boonzy/Downloads/dimedrop/assets"
    os.makedirs(assets_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()

        try:
            print("🌐 Connecting to DimeDrop app...")
            await page.goto("http://localhost:3000", timeout=60000, wait_until='domcontentloaded')

            # Check if app is ready
            if not await check_app_ready(page):
                print("❌ App not ready after maximum attempts")
                await page.screenshot(path=f"{assets_dir}/error_not_ready.png", full_page=True)
                return

            await asyncio.sleep(3)

            # Screenshot 1: Main page
            await page.screenshot(path=f"{assets_dir}/main_page.png", full_page=True)
            print("✅ Main page captured")

            # Try to find and click navigation buttons
            buttons_to_try = [
                "🏠 Home",
                "📷 Scan Card",
                "💰 Price Tracking",
                "🧠 Sentiment Analysis",
                "📊 Portfolio"
            ]

            for i, button_text in enumerate(buttons_to_try):
                try:
                    print(f"🔍 Looking for: {button_text}")
                    button = await page.query_selector(f'button:has-text("{button_text}")')
                    if button:
                        print(f"📸 Clicking {button_text}")
                        await button.click()
                        await asyncio.sleep(3)
                        filename = button_text.replace(" ", "_").replace("🏠", "home").replace("📷", "scan").replace("💰", "price").replace("🧠", "sentiment").replace("📊", "portfolio").lower()
                        await page.screenshot(path=f"{assets_dir}/section_{i+1}_{filename}.png", full_page=True)
                        print(f"✅ {button_text} section captured")
                    else:
                        print(f"❌ Button '{button_text}' not found")
                except Exception as e:
                    print(f"❌ Error with {button_text}: {e}")

            print("🎉 Screenshot capture completed!")

        except Exception as e:
            print(f"❌ Error during screenshot capture: {e}")
            try:
                await page.screenshot(path=f"{assets_dir}/error_final.png", full_page=True)
            except:
                pass

        finally:
            await browser.close()


async def main():
    """Main function."""
    app_process = None

    try:
        print("🚀 Starting DimeDrop app...")
        app_process = subprocess.Popen(
            ["python3", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/home/boonzy/Downloads/dimedrop"
        )

        print("⏳ Waiting for app to start (20 seconds)...")
        await asyncio.sleep(20)

        # Check if process is still running
        if app_process.poll() is not None:
            stdout, stderr = app_process.communicate()
            print("❌ App failed to start:")
            print("STDOUT:", stdout.decode())
            print("STDERR:", stderr.decode())
            return

        print("📸 Taking screenshots...")
        await take_screenshots()

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        if app_process and app_process.poll() is None:
            print("🛑 Stopping DimeDrop app...")
            try:
                app_process.terminate()
                app_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                app_process.kill()
                app_process.wait()

        print("🎉 Process complete!")


if __name__ == "__main__":
    asyncio.run(main())

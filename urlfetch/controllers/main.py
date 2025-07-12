from odoo import http
from odoo.http import Response
import json
from odoo.http import request
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, Error as PlaywrightError
import os


class UrlfetchController(http.Controller):
    @http.route(
        "/urlfetch/ping", type="http", auth="public", methods=["GET"], csrf=False
    )
    def urlfetch_ping(self, **kwargs):
        return Response("OK", status=200, mimetype="text/plain")

    @http.route(
        "/urlfetch/fetch", type="json", auth="public", methods=["POST"], csrf=False
    )
    def urlfetch_fetch(self, **kwargs):
        # Parse JSON body robustly
        try:
            # Try Odoo's jsonrequest first
            data = getattr(request, "jsonrequest", None)
            if data is None:
                # Fallback: parse from raw HTTP request
                raw = request.httprequest.get_data()
                data = json.loads(raw.decode("utf-8"))
        except Exception:
            return Response("Invalid JSON", status=400, mimetype="text/plain")

        url = data.get("url")
        if not url:
            return Response("Missing 'url' field", status=404, mimetype="text/plain")

        # Validate URL
        parsed = urlparse(url)
        if not (parsed.scheme in ("http", "https") and parsed.netloc):
            return Response("Invalid URL", status=403, mimetype="text/plain")

        try:
            os.environ["DEBUG"] = "pw:browser*"
            with sync_playwright() as p:
                print("Starting Playwright in headless mode...")
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                )

                print("Launching browser with Playwright...")
                page = browser.new_page()

                print("New page created, navigating to the URL...")
                page.goto(url, wait_until="load")

                print("Waiting for the page to load...")
                page.wait_for_load_state("networkidle", timeout=60000)

                print("Page loaded, retrieving HTML content...")
                html = page.content()

                print("HTML content retrieved successfully.")
                print(html)
                browser.close()
        except PlaywrightError as e:
            # Log the error message for debugging
            print(f"PlaywrightError: {e}")
            return Response("Error retrieving page", status=500, mimetype="text/plain")
        except Exception as e:
            print(f"Unknown error: {e}")
            return Response("Unknown error", status=500, mimetype="text/plain")

        return Response(html, status=200, mimetype="text/html")

from __future__ import annotations

from dataclasses import dataclass
import os
import random
import time

from playwright.sync_api import Page, sync_playwright

from .logger import logger

LBC_DEPOSIT_URL = "https://www.leboncoin.fr/deposer-une-annonce"


def _human_delay(delay_min: int, delay_max: int) -> None:
    """Add a random delay to simulate human behavior."""
    delay = random.uniform(delay_min, delay_max)
    logger.debug(f"⏸️  Human-like delay: {delay:.1f}s")
    time.sleep(delay)


@dataclass(frozen=True)
class AdPayload:
    title: str
    description: str
    price_eur: int
    category_label: str
    images: list[str]


def publish_ad(
    payload: AdPayload,
    storage_state_path: str,
    headless: bool,
    delay_min: int = 2,
    delay_max: int = 5,
) -> str:
    """
    Returns the published ad URL.
    Note: Leboncoin may trigger bot checks; keep headless=False initially.
    """
    logger.debug(f"🌐 Initializing browser (headless={headless})")
    os.makedirs(os.path.dirname(storage_state_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",  # Hide automation
            ],
        )
        logger.debug(f"🔐 Loading storage state: {os.path.exists(storage_state_path)}")
        context = browser.new_context(
            storage_state=(
                storage_state_path if os.path.exists(storage_state_path) else None
            ),
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        logger.info(f"🌐 Navigating to Leboncoin: {LBC_DEPOSIT_URL}")
        page.goto(LBC_DEPOSIT_URL, wait_until="domcontentloaded")
        _human_delay(delay_min, delay_max)

        # If you're not logged in, do it manually on first run:
        _ensure_logged_in(page)

        # Fill the deposit form
        logger.info("📝 Filling ad form...")
        _fill_form(page, payload, delay_min, delay_max)

        # Submit and extract URL
        logger.info("📤 Submitting ad...")
        published_url = _submit_and_get_url(page)

        logger.debug(f"💾 Saving session state to {storage_state_path}")
        context.storage_state(path=storage_state_path)
        context.close()
        browser.close()
        logger.debug("🔚 Browser closed")
        return published_url


def _ensure_logged_in(page: Page) -> None:
    """
    Manual-friendly login gate: if a login button or login form is detected,
    pause until the user completes login.
    """
    # This is intentionally generic because Leboncoin changes selectors often.
    # You will adapt it once you see the DOM in your session.
    if page.get_by_role("link", name="Se connecter").count() > 0:
        logger.warning("🔐 Not logged in! Please log in manually...")
        page.get_by_role("link", name="Se connecter").first.click()
        page.pause()  # user logs in, handles 2FA/captcha if any
        logger.info("✓ Login completed")
        page.goto(
            "https://www.leboncoin.fr/deposer-une-annonce",
            wait_until="domcontentloaded",
        )
    else:
        logger.debug("✓ Already logged in")


def _fill_form(page: Page, payload: AdPayload, delay_min: int, delay_max: int) -> None:
    """
    Fill fields using role/label-based selectors as much as possible.
    You will likely need to adjust these once you inspect the page.
    """
    # Category selection (generic flow; adjust according to actual UI)
    # Example approach: search/select category by visible text
    page.get_by_text("Catégorie", exact=False).first.click()
    _human_delay(delay_min, delay_max)
    page.get_by_text(payload.category_label, exact=False).first.click()
    _human_delay(delay_min, delay_max)

    # Title
    page.get_by_label("Titre", exact=False).fill(payload.title)
    _human_delay(delay_min, delay_max)

    # Description
    page.get_by_label("Description", exact=False).fill(payload.description)
    _human_delay(delay_min, delay_max)

    # Price
    page.get_by_label("Prix", exact=False).fill(str(payload.price_eur))
    _human_delay(delay_min, delay_max)

    # Images upload: usually an <input type="file">
    file_inputs = page.locator("input[type='file']")
    if file_inputs.count() == 0:
        raise RuntimeError(
            "No file input found for image upload (selector update needed)."
        )
    file_inputs.first.set_input_files(payload.images)
    _human_delay(delay_min, delay_max)


def _submit_and_get_url(page: Page) -> str:
    """
    Click publish button and return the resulting URL.
    """
    # Click publish
    btn = page.get_by_role("button", name="Valider", exact=False)
    if btn.count() == 0:
        btn = page.get_by_role("button", name="Publier", exact=False)
    if btn.count() == 0:
        page.pause()
        raise RuntimeError("Publish button not found (selector update needed).")

    btn.first.click()

    # Wait for navigation or confirmation page
    page.wait_for_load_state("networkidle")

    # Heuristic: published URL is current page URL if it contains /ad/ or similar
    url = page.url
    if "leboncoin.fr" not in url:
        raise RuntimeError("Unexpected URL after publish.")
    return url

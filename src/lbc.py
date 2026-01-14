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


def _human_type(
    page: Page, selector: str, text: str, delay_min: int, delay_max: int
) -> None:
    """Type text character by character with realistic delays to avoid bot detection."""
    element = page.locator(selector)
    element.click()
    _human_delay(delay_min * 0.3, delay_max * 0.3)

    # Type character by character with micro-delays
    for char in text:
        element.type(char, delay=random.uniform(50, 150))  # 50-150ms between chars

    logger.debug(f"⌨️  Typed {len(text)} characters with human-like timing")
    _human_delay(delay_min * 0.5, delay_max * 0.5)


def _move_mouse_randomly(page: Page) -> None:
    """Simulate random mouse movements to appear more human-like."""
    x = random.randint(100, 1800)
    y = random.randint(100, 1000)
    page.mouse.move(x, y, steps=random.randint(10, 30))
    logger.debug(f"🖱️  Moved mouse to ({x}, {y})")


def _random_scroll(page: Page, delay_min: int, delay_max: int) -> None:
    """Perform random scrolling behavior."""
    scroll_amount = random.randint(100, 500)
    page.evaluate(f"window.scrollBy(0, {scroll_amount})")
    logger.debug(f"📜 Scrolled {scroll_amount}px down")
    _human_delay(delay_min * 0.3, delay_max * 0.5)


def _verify_javascript(page: Page) -> None:
    """Verify JavaScript is working properly to avoid detection."""
    try:
        result = page.evaluate(
            "() => { return navigator.userAgent && typeof window !== 'undefined' }"
        )
        if not result:
            raise RuntimeError("JavaScript verification failed")
        logger.debug("✓ JavaScript verification passed")
    except Exception as e:
        logger.error(f"❌ JavaScript verification failed: {e}")
        raise RuntimeError("JavaScript is not working properly") from e


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
                "--disable-dev-shm-usage",  # Overcome limited resource problems
                "--no-sandbox",  # Useful for containerized environments
                "--disable-setuid-sandbox",
                "--disable-web-security",  # Prevent CORS issues
            ],
        )
        logger.debug(f"🔐 Loading storage state: {os.path.exists(storage_state_path)}")
        context = browser.new_context(
            storage_state=(
                storage_state_path if os.path.exists(storage_state_path) else None
            ),
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="fr-FR",  # French locale
            timezone_id="Europe/Paris",  # French timezone
            geolocation={"longitude": 2.3522, "latitude": 48.8566},  # Paris coordinates
            permissions=["geolocation"],
        )

        # Inject JavaScript to further hide automation
        context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            window.chrome = {
                runtime: {}
            };

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['fr-FR', 'fr', 'en-US', 'en']
            });
        """
        )

        page = context.new_page()

        logger.info(f"🌐 Navigating to Leboncoin: {LBC_DEPOSIT_URL}")
        page.goto(LBC_DEPOSIT_URL, wait_until="domcontentloaded")
        _human_delay(delay_min, delay_max)

        # Verify JavaScript is working
        _verify_javascript(page)

        # Random initial mouse movement and scroll
        _move_mouse_randomly(page)
        _random_scroll(page, delay_min, delay_max)

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
    # Random mouse movement before starting
    _move_mouse_randomly(page)
    _human_delay(delay_min * 0.5, delay_max * 0.5)

    # Category selection (generic flow; adjust according to actual UI)
    # Example approach: search/select category by visible text
    logger.debug("📂 Selecting category...")
    page.get_by_text("Catégorie", exact=False).first.click()
    _human_delay(delay_min, delay_max)
    page.get_by_text(payload.category_label, exact=False).first.click()
    _human_delay(delay_min, delay_max)

    # Random scroll between actions
    _random_scroll(page, delay_min, delay_max)
    _move_mouse_randomly(page)

    # Title - type character by character
    logger.debug("✏️  Typing title...")
    title_field = page.get_by_label("Titre", exact=False)
    title_field.click()
    _human_delay(delay_min * 0.3, delay_max * 0.5)
    # Type with realistic delays (100-200ms per character)
    for char in payload.title:
        title_field.type(char, delay=random.uniform(80, 180))
    _human_delay(delay_min, delay_max)

    # Random behavior
    _move_mouse_randomly(page)
    _human_delay(delay_min * 0.3, delay_max * 0.6)

    # Description - type character by character (but faster for long text)
    logger.debug("📄 Typing description...")
    desc_field = page.get_by_label("Description", exact=False)
    desc_field.click()
    _human_delay(delay_min * 0.3, delay_max * 0.5)
    # For long descriptions, type in chunks with delays
    chunk_size = 50
    for i in range(0, len(payload.description), chunk_size):
        chunk = payload.description[i : i + chunk_size]
        for char in chunk:
            desc_field.type(char, delay=random.uniform(30, 80))
        # Mini pause every chunk
        if i + chunk_size < len(payload.description):
            time.sleep(random.uniform(0.3, 0.8))
    _human_delay(delay_min, delay_max)

    # Random scroll
    _random_scroll(page, delay_min, delay_max)
    _move_mouse_randomly(page)

    # Price - type digit by digit
    logger.debug("💰 Typing price...")
    price_field = page.get_by_label("Prix", exact=False)
    price_field.click()
    _human_delay(delay_min * 0.3, delay_max * 0.5)
    price_str = str(payload.price_eur)
    for digit in price_str:
        price_field.type(digit, delay=random.uniform(100, 200))
    _human_delay(delay_min, delay_max)

    # Random behavior before image upload
    _move_mouse_randomly(page)
    _random_scroll(page, delay_min, delay_max)

    # Images upload: usually an <input type="file">
    logger.debug("🖼️  Uploading images...")
    file_inputs = page.locator("input[type='file']")
    if file_inputs.count() == 0:
        raise RuntimeError(
            "No file input found for image upload (selector update needed)."
        )
    file_inputs.first.set_input_files(payload.images)
    _human_delay(delay_min * 1.5, delay_max * 2)  # Longer delay after images


def _submit_and_get_url(page: Page) -> str:
    """
    Click publish button and return the resulting URL.
    """
    # Random mouse movement before clicking submit
    _move_mouse_randomly(page)
    time.sleep(random.uniform(0.5, 1.5))

    # Click publish
    btn = page.get_by_role("button", name="Valider", exact=False)
    if btn.count() == 0:
        btn = page.get_by_role("button", name="Publier", exact=False)
    if btn.count() == 0:
        page.pause()
        raise RuntimeError("Publish button not found (selector update needed).")

    # Move mouse to button area before clicking (more human-like)
    box = btn.first.bounding_box()
    if box:
        x = box["x"] + box["width"] / 2 + random.uniform(-10, 10)
        y = box["y"] + box["height"] / 2 + random.uniform(-5, 5)
        page.mouse.move(x, y, steps=random.randint(15, 30))
        time.sleep(random.uniform(0.3, 0.7))

    logger.debug("🖱️  Clicking publish button...")
    btn.first.click()

    # Wait for navigation or confirmation page
    page.wait_for_load_state("networkidle")

    # Heuristic: published URL is current page URL if it contains /ad/ or similar
    url = page.url
    if "leboncoin.fr" not in url:
        raise RuntimeError("Unexpected URL after publish.")
    return url

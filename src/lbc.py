from __future__ import annotations

from dataclasses import dataclass
import os
import random
import time

from playwright.sync_api import Page, sync_playwright
from playwright_stealth import stealth_sync
from python_ghost_cursor.playwright_sync import create_cursor

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
    proxy_server: str | None = None,
    proxy_username: str | None = None,
    proxy_password: str | None = None,
) -> str:
    """
    Returns the published ad URL.
    Note: Leboncoin may trigger bot checks; keep headless=False initially.
    """
    logger.debug(f"🌐 Initializing browser (headless={headless})")
    os.makedirs(os.path.dirname(storage_state_path), exist_ok=True)

    # Build proxy config if provided
    proxy_config = None
    if proxy_server:
        proxy_config = {"server": proxy_server}
        if proxy_username and proxy_password:
            proxy_config["username"] = proxy_username
            proxy_config["password"] = proxy_password
        logger.info(f"🔒 Using proxy: {proxy_server}")
    else:
        logger.warning("⚠️  No proxy configured - Datadome detection risk is HIGH")

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
            proxy=proxy_config,  # Add proxy configuration
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

        # Apply playwright-stealth to hide automation signals
        logger.debug("🛡️  Applying stealth mode...")
        stealth_sync(page)

        # Create ghost cursor for ultra-realistic mouse movements
        logger.debug("🖱️  Initializing ghost cursor...")
        cursor = create_cursor(page)

        logger.info(f"🌐 Navigating to Leboncoin: {LBC_DEPOSIT_URL}")
        page.goto(LBC_DEPOSIT_URL, wait_until="domcontentloaded")
        _human_delay(delay_min, delay_max)

        # Verify JavaScript is working
        _verify_javascript(page)

        # Random initial mouse movement with ghost cursor
        logger.debug("🖱️  Performing initial human-like mouse movements...")
        # Move to a random point with Bezier curves
        target_x = random.randint(300, 1600)
        target_y = random.randint(300, 900)
        cursor.move_to(target_x, target_y)
        _human_delay(delay_min * 0.5, delay_max * 0.8)

        # Random scroll
        _random_scroll(page, delay_min, delay_max)

        # If you're not logged in, do it manually on first run:
        _ensure_logged_in(page)

        # Fill the deposit form
        logger.info("📝 Filling ad form...")
        _fill_form(page, payload, delay_min, delay_max, cursor)

        # Submit and extract URL
        logger.info("📤 Submitting ad...")
        published_url = _submit_and_get_url(page, cursor)

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


def _fill_form(
    page: Page, payload: AdPayload, delay_min: int, delay_max: int, cursor
) -> None:
    """
    Fill fields using role/label-based selectors as much as possible.
    You will likely need to adjust these once you inspect the page.
    """
    # Random mouse movement with ghost cursor before starting
    logger.debug("🖱️  Random mouse movement with Bezier curves...")
    cursor.move_to(random.randint(300, 1700), random.randint(200, 800))
    _human_delay(delay_min * 0.5, delay_max * 0.5)

    # Category selection (generic flow; adjust according to actual UI)
    # Example approach: search/select category by visible text
    logger.debug("📂 Selecting category...")
    cat_elem = page.get_by_text("Catégorie", exact=False).first
    cursor.click(cat_elem)
    _human_delay(delay_min, delay_max)
    cat_option = page.get_by_text(payload.category_label, exact=False).first
    cursor.click(cat_option)
    _human_delay(delay_min, delay_max)

    # Random scroll between actions
    _random_scroll(page, delay_min, delay_max)
    cursor.move_to(random.randint(400, 1600), random.randint(300, 900))

    # Title - type character by character with cursor movement
    logger.debug("✏️  Typing title...")
    title_field = page.get_by_label("Titre", exact=False)
    cursor.click(title_field)
    _human_delay(delay_min * 0.3, delay_max * 0.5)
    # Type with realistic delays (100-200ms per character)
    for char in payload.title:
        title_field.type(char, delay=random.uniform(80, 180))
    _human_delay(delay_min, delay_max)

    # Random cursor movement
    cursor.move_to(random.randint(500, 1500), random.randint(400, 800))
    _human_delay(delay_min * 0.3, delay_max * 0.6)

    # Description - type character by character (but faster for long text)
    logger.debug("📄 Typing description...")
    desc_field = page.get_by_label("Description", exact=False)
    cursor.click(desc_field)
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

    # Random scroll and cursor movement
    _random_scroll(page, delay_min, delay_max)
    cursor.move_to(random.randint(600, 1400), random.randint(500, 900))

    # Price - type digit by digit
    logger.debug("💰 Typing price...")
    price_field = page.get_by_label("Prix", exact=False)
    cursor.click(price_field)
    _human_delay(delay_min * 0.3, delay_max * 0.5)
    price_str = str(payload.price_eur)
    for digit in price_str:
        price_field.type(digit, delay=random.uniform(100, 200))
    _human_delay(delay_min, delay_max)

    # Random cursor movement before image upload
    cursor.move_to(random.randint(700, 1300), random.randint(600, 1000))
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


def _submit_and_get_url(page: Page, cursor) -> str:
    """
    Click publish button and return the resulting URL.
    """
    # Random mouse movement with ghost cursor before clicking submit
    logger.debug("🖱️  Moving cursor before submission...")
    cursor.move_to(random.randint(800, 1200), random.randint(700, 900))
    time.sleep(random.uniform(0.5, 1.5))

    # Click publish
    btn = page.get_by_role("button", name="Valider", exact=False)
    if btn.count() == 0:
        btn = page.get_by_role("button", name="Publier", exact=False)
    if btn.count() == 0:
        page.pause()
        raise RuntimeError("Publish button not found (selector update needed).")

    # Use ghost cursor to move to button and click (ultra-realistic with Bezier curves)
    logger.debug("🖱️  Clicking publish button with realistic mouse movement...")
    cursor.click(btn.first)
    time.sleep(random.uniform(0.3, 0.7))

    # Wait for navigation or confirmation page
    page.wait_for_load_state("networkidle")

    # Heuristic: published URL is current page URL if it contains /ad/ or similar
    url = page.url
    if "leboncoin.fr" not in url:
        raise RuntimeError("Unexpected URL after publish.")
    return url

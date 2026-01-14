from __future__ import annotations

from dataclasses import dataclass
import os

from playwright.sync_api import Page, sync_playwright

LBC_DEPOSIT_URL = "https://www.leboncoin.fr/deposer-une-annonce"


@dataclass(frozen=True)
class AdPayload:
    title: str
    description: str
    price_eur: int
    category_label: str
    images: list[str]


def publish_ad(payload: AdPayload, storage_state_path: str, headless: bool) -> str:
    """
    Returns the published ad URL.
    Note: Leboncoin may trigger bot checks; keep headless=False initially.
    """
    os.makedirs(os.path.dirname(storage_state_path), exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            storage_state=(
                storage_state_path if os.path.exists(storage_state_path) else None
            )
        )
        page = context.new_page()

        page.goto(LBC_DEPOSIT_URL, wait_until="domcontentloaded")

        # If you're not logged in, do it manually on first run:
        _ensure_logged_in(page)

        # Fill the deposit form
        _fill_form(page, payload)

        # Submit and extract URL
        published_url = _submit_and_get_url(page)

        context.storage_state(path=storage_state_path)
        context.close()
        browser.close()
        return published_url


def _ensure_logged_in(page: Page) -> None:
    """
    Manual-friendly login gate: if a login button or login form is detected,
    pause until the user completes login.
    """
    # This is intentionally generic because Leboncoin changes selectors often.
    # You will adapt it once you see the DOM in your session.
    if page.get_by_role("link", name="Se connecter").count() > 0:
        page.get_by_role("link", name="Se connecter").first.click()
        page.pause()  # user logs in, handles 2FA/captcha if any
        page.goto(
            "https://www.leboncoin.fr/deposer-une-annonce",
            wait_until="domcontentloaded",
        )


def _fill_form(page: Page, payload: AdPayload) -> None:
    """
    Fill fields using role/label-based selectors as much as possible.
    You will likely need to adjust these once you inspect the page.
    """
    # Category selection (generic flow; adjust according to actual UI)
    # Example approach: search/select category by visible text
    page.get_by_text("Catégorie", exact=False).first.click()
    page.get_by_text(payload.category_label, exact=False).first.click()

    # Title
    page.get_by_label("Titre", exact=False).fill(payload.title)

    # Description
    page.get_by_label("Description", exact=False).fill(payload.description)

    # Price
    page.get_by_label("Prix", exact=False).fill(str(payload.price_eur))

    # Images upload: usually an <input type="file">
    file_inputs = page.locator("input[type='file']")
    if file_inputs.count() == 0:
        raise RuntimeError(
            "No file input found for image upload (selector update needed)."
        )
    file_inputs.first.set_input_files(payload.images)


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

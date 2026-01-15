#!/usr/bin/env python3
"""Test script to verify Bright Data proxy configuration."""

from __future__ import annotations

import sys

from playwright.sync_api import sync_playwright

from src.logger import logger
from src.settings import get_settings


def test_proxy() -> bool:
    """Test if proxy is configured and working."""
    settings = get_settings()

    if not settings.proxy_server:
        logger.error("❌ No proxy configured in .env")
        logger.info("Add these lines to your .env:")
        logger.info("PROXY_SERVER=http://brd.superproxy.io:22225")
        logger.info("PROXY_USERNAME=brd-customer-xxx-zone-xxx")
        logger.info("PROXY_PASSWORD=xxx")
        return False

    logger.info(f"🔍 Testing proxy: {settings.proxy_server}")
    logger.info(f"   Username: {settings.proxy_username}")
    logger.info(f"   Password: {'*' * len(settings.proxy_password or '')}")

    proxy_config = {
        "server": settings.proxy_server,
    }
    if settings.proxy_username and settings.proxy_password:
        proxy_config["username"] = settings.proxy_username
        proxy_config["password"] = settings.proxy_password

    try:
        with sync_playwright() as p:
            logger.info("🌐 Launching browser with proxy...")
            browser = p.chromium.launch(
                channel="chrome",
                headless=False,  # Visible pour voir ce qui se passe
            )

            context = browser.new_context(
                proxy=proxy_config,
                ignore_https_errors=True,  # Ignore SSL errors with proxy
            )
            page = context.new_page()

            # Test 1: Vérifier l'IP
            logger.info("📍 Test 1: Checking IP address...")
            page.goto("https://ipinfo.io/json", wait_until="domcontentloaded")
            ip_info = page.content()
            logger.info(f"✓ IP Info retrieved:\n{ip_info}")

            # Test 2: Accéder à Leboncoin
            logger.info("📍 Test 2: Accessing Leboncoin...")
            page.goto("https://www.leboncoin.fr", wait_until="domcontentloaded")
            title = page.title()
            logger.info(f"✓ Leboncoin title: {title}")

            # Vérifier si Datadome bloque
            content = page.content().lower()
            if "datadome" in content or "captcha" in content:
                logger.warning("⚠️  Datadome challenge detected!")
                logger.info("   This might still work for actual publishing")
            else:
                logger.success("✅ No Datadome challenge detected!")

            context.close()
            browser.close()

        logger.success("🎉 Proxy test completed successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Proxy test failed: {e}")
        logger.info("\nVerify:")
        logger.info("1. Credentials are correct in .env")
        logger.info("2. Bright Data zone is active")
        logger.info("3. You have traffic/credits available")
        return False


if __name__ == "__main__":
    success = test_proxy()
    sys.exit(0 if success else 1)

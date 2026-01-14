from __future__ import annotations

import os
import random
import tempfile
import time

from .drive import download_file, extract_drive_folder_id, list_images_in_folder
from .lbc import AdPayload, publish_ad
from .logger import logger
from .models import build_description, build_title, parse_eur_amount
from .settings import get_settings
from .sheet import get_rows, update_cells


def main() -> None:
    logger.info("🚀 Starting LBC Publisher")

    settings = get_settings()
    logger.info(
        f"📋 Configuration loaded: sheets_id={settings.sheets_id[:8]}..., sheet_name={settings.sheet_name}"
    )

    logger.info("📊 Fetching rows from Google Sheets...")
    rows = get_rows(settings.sheets_id, settings.sheet_name)
    logger.success(f"✓ Fetched {len(rows)} rows from spreadsheet")

    to_publish = [r for r in rows if r.should_publish()]
    logger.info(f"📝 Found {len(to_publish)} rows marked for publication")

    if not to_publish:
        logger.warning("⚠️  No rows to publish. Exiting.")
        return

    # Limit number of ads per run to avoid detection
    if len(to_publish) > settings.lbc_max_ads_per_run:
        logger.warning(
            f"⚠️  Limiting to {settings.lbc_max_ads_per_run} ads per run (found {len(to_publish)})"
        )
        to_publish = to_publish[: settings.lbc_max_ads_per_run]

    for idx, r in enumerate(to_publish, 1):
        logger.info(f"\n{'='*80}")
        logger.info(
            f"📦 Processing row {idx}/{len(to_publish)} (Sheet row #{r.row_index})"
        )

        try:
            # Parse price
            price = parse_eur_amount(r.prix_demande_unite)
            if price is None:
                raise RuntimeError("Missing price (Prix demandé à l'unité).")
            logger.debug(f"💰 Price parsed: {price}€")

            # Build title and description
            title = build_title(r)
            desc = build_description(r)
            logger.debug(f"📝 Title: {title}")
            logger.debug(f"📄 Description length: {len(desc)} characters")

            # Download images
            image_paths: list[str] = []
            with tempfile.TemporaryDirectory() as tmp:
                logger.info("📁 Downloading images from Google Drive...")
                folder_id = extract_drive_folder_id(r.dossier_photos)
                if folder_id:
                    imgs = list_images_in_folder(folder_id)
                    if not imgs:
                        raise RuntimeError("No images found in Drive folder.")
                    logger.info(f"🖼️  Found {len(imgs)} images, downloading up to 10...")

                    for i, f in enumerate(imgs[:10], start=1):
                        dst = os.path.join(tmp, f"{i:02d}_{f.name}")
                        download_file(f.file_id, dst)
                        image_paths.append(dst)
                        logger.debug(f"  ✓ Downloaded image {i}/10: {f.name}")

                    logger.success(f"✓ Downloaded {len(image_paths)} images")
                else:
                    raise RuntimeError(
                        "Missing/invalid Dossier photos (Drive folder URL)."
                    )

                # Create ad payload
                payload = AdPayload(
                    title=title,
                    description=desc,
                    price_eur=price,
                    category_label=r.categorie,
                    images=image_paths,
                )

                # Publish ad
                logger.info("🌐 Publishing ad on Leboncoin...")
                url = publish_ad(
                    payload,
                    settings.lbc_storage_state,
                    headless=settings.lbc_headless,
                    delay_min=settings.lbc_delay_min,
                    delay_max=settings.lbc_delay_max,
                    proxy_server=settings.proxy_server,
                    proxy_username=settings.proxy_username,
                    proxy_password=settings.proxy_password,
                )
                logger.success(f"✅ Ad published successfully: {url}")

            # Update spreadsheet
            logger.info("📝 Updating spreadsheet with published ad URL...")
            update_cells(
                settings.sheets_id,
                settings.sheet_name,
                r.row_index,
                {
                    "Lien de l'annonce": url,
                    "Status": "PUBLISHED",
                },
            )
            logger.success(f"✓ Row {r.row_index} marked as PUBLISHED")

            # Wait before next ad to avoid rate limiting
            if idx < len(to_publish):
                delay = random.randint(
                    settings.lbc_delay_min * 10, settings.lbc_delay_max * 10
                )
                logger.info(f"⏳ Waiting {delay}s before next ad to avoid detection...")
                time.sleep(delay)

        except Exception as e:
            logger.error(f"❌ Error processing row {r.row_index}: {str(e)}")

    logger.info(f"\n{'='*80}")
    logger.success(f"🎉 Finished processing {len(to_publish)} rows!")


if __name__ == "__main__":
    main()

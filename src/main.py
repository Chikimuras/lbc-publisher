from __future__ import annotations

import os
import tempfile

from .drive import download_file, extract_drive_folder_id, list_images_in_folder
from .lbc import AdPayload, publish_ad
from .models import build_description, build_title, parse_eur_amount
from .settings import get_settings
from .sheet import get_rows, update_cells


def main() -> None:
    settings = get_settings()

    rows = get_rows(settings.sheets_id, settings.sheet_name)
    to_publish = [r for r in rows if r.should_publish()]

    for r in to_publish:
        try:
            price = parse_eur_amount(r.prix_demande_unite)
            if price is None:
                raise RuntimeError("Missing price (Prix demandé à l'unité).")

            title = build_title(r)
            desc = build_description(r)

            image_paths: list[str] = []
            with tempfile.TemporaryDirectory() as tmp:
                folder_id = extract_drive_folder_id(r.dossier_photos)
                if folder_id:
                    imgs = list_images_in_folder(folder_id)
                    if not imgs:
                        raise RuntimeError("No images found in Drive folder.")
                    for i, f in enumerate(imgs[:10], start=1):
                        dst = os.path.join(tmp, f"{i:02d}_{f.name}")
                        download_file(f.file_id, dst)
                        image_paths.append(dst)
                else:
                    # If you later store direct photo URLs in "Photos", implement download here.
                    # For now, require a Drive folder.
                    raise RuntimeError(
                        "Missing/invalid Dossier photos (Drive folder URL)."
                    )

                payload = AdPayload(
                    title=title,
                    description=desc,
                    price_eur=price,
                    category_label=r.categorie,  # you may need a mapping later
                    images=image_paths,
                )

                url = publish_ad(
                    payload, settings.lbc_storage_state, headless=settings.lbc_headless
                )

            update_cells(
                settings.sheets_id,
                settings.sheet_name,
                r.row_index,
                {
                    "Lien de l'annonce": url,
                    "Status": "PUBLISHED",
                },
            )

        except Exception as e:
            update_cells(
                settings.sheets_id,
                settings.sheet_name,
                r.row_index,
                {
                    "Status": f"ERROR: {str(e)[:120]}",
                },
            )


if __name__ == "__main__":
    main()

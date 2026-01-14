from __future__ import annotations

from typing import Any

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from .logger import logger
from .models import SheetRow
from .settings import get_settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


HEADERS = [
    "Annonce LBC",
    "Lien de l'annonce",
    "Photos",
    "Dossier photos",
    "Catégorie",
    "Pièces",
    "Objet",
    "Marques",
    "Modèle",
    "Quantité",
    "État",
    "Prix neuf à l'unité",
    "Prix total",
    "Prix  demandé à l'unité",
    "Prix total demandé",
    "Status",
    "A publier",
]


def _creds() -> Credentials:
    settings = get_settings()
    return Credentials.from_service_account_file(
        settings.google_service_account_json, scopes=SCOPES
    )


def get_rows(sheets_id: str, sheet_name: str) -> list[SheetRow]:
    """
    Read the whole sheet (used range) and map rows by header names.
    """
    logger.debug("📊 Connecting to Google Sheets API...")
    service = build("sheets", "v4", credentials=_creds())
    rng = f"{sheet_name}!A:Z"
    logger.debug(f"📖 Reading range: {rng}")

    res = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheets_id, range=rng)
        .execute()
    )
    values: list[list[str]] = res.get("values", [])
    if not values:
        logger.warning("⚠️  Empty spreadsheet")
        return []

    header = values[0]
    logger.debug(f"📋 Found {len(header)} columns in header")
    col_index = {name: header.index(name) for name in HEADERS if name in header}
    logger.debug(f"✓ Mapped {len(col_index)} expected columns")

    def cell(row: list[str], name: str) -> str:
        i = col_index.get(name)
        if i is None:
            return ""
        return row[i] if i < len(row) else ""

    out: list[SheetRow] = []
    for i, r in enumerate(
        values[1:], start=2
    ):  # sheet rows are 1-based; header is row 1
        out.append(
            SheetRow(
                row_index=i,
                annonce_lbc=cell(r, "Annonce LBC"),
                lien_annonce=cell(r, "Lien de l'annonce"),
                photos=cell(r, "Photos"),
                dossier_photos=cell(r, "Dossier photos"),
                categorie=cell(r, "Catégorie"),
                pieces=cell(r, "Pièces"),
                objet=cell(r, "Objet"),
                marques=cell(r, "Marques"),
                modele=cell(r, "Modèle"),
                quantite=cell(r, "Quantité"),
                etat=cell(r, "État"),
                prix_neuf_unite=cell(r, "Prix neuf à l'unité"),
                prix_total=cell(r, "Prix total"),
                prix_demande_unite=cell(r, "Prix  demandé à l'unité"),
                prix_total_demande=cell(r, "Prix total demandé"),
                status=cell(r, "Status"),
                a_publier=cell(r, "A publier"),
            )
        )
    return out


def update_cells(
    sheets_id: str,
    sheet_name: str,
    row_index: int,
    updates: dict[str, str],
) -> None:
    """
    Update specific columns in a given row by header name.
    """
    logger.debug(f"📝 Updating row {row_index} with {len(updates)} cell(s)")
    service = build("sheets", "v4", credentials=_creds())

    # Read header to find column letters
    header_res = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=sheets_id, range=f"{sheet_name}!1:1")
        .execute()
    )
    header = header_res.get("values", [[]])[0]
    col_map = {name: idx for idx, name in enumerate(header)}  # 0-based

    data: list[dict[str, Any]] = []
    for name, val in updates.items():
        idx = col_map.get(name)
        if idx is None:
            logger.warning(f"⚠️  Column '{name}' not found in header, skipping")
            continue
        col_letter = _col_to_a1(idx)
        a1 = f"{sheet_name}!{col_letter}{row_index}"
        data.append({"range": a1, "values": [[val]]})
        logger.debug(f"  ✓ {name} = {val[:50]}...")  # Truncate long values

    if not data:
        logger.warning("⚠️  No valid cells to update")
        return

    body = {"valueInputOption": "USER_ENTERED", "data": data}
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=sheets_id, body=body
    ).execute()
    logger.debug(f"✓ Successfully updated {len(data)} cell(s)")


def _col_to_a1(idx: int) -> str:
    """
    Convert 0-based column index to A1 letters.
    """
    n = idx + 1
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

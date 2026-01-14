"""Tests for models module."""

from __future__ import annotations

from src.models import SheetRow, build_description, build_title, parse_eur_amount


class TestParseEurAmount:
    """Test parse_eur_amount function."""

    def test_parse_valid_french_format(self):
        """Test parsing valid French-formatted amounts."""
        assert parse_eur_amount("240,00 €") == 240
        assert parse_eur_amount("104,30 €") == 104
        assert parse_eur_amount("1 500,50 €") == 1500
        assert parse_eur_amount("99,99€") == 99

    def test_parse_with_non_breaking_space(self):
        """Test parsing with non-breaking space."""
        assert parse_eur_amount("240,00\u00a0€") == 240

    def test_parse_empty_or_dash(self):
        """Test parsing empty strings or dashes."""
        assert parse_eur_amount("") is None
        assert parse_eur_amount("-") is None
        assert parse_eur_amount("–") is None
        assert parse_eur_amount("   ") is None

    def test_parse_invalid_format(self):
        """Test parsing invalid formats."""
        assert parse_eur_amount("abc") is None
        assert parse_eur_amount("€€€") is None


class TestBuildTitle:
    """Test build_title function."""

    def test_uses_annonce_lbc_if_present(self):
        """Test that annonce_lbc is used when present."""
        row = SheetRow(
            row_index=1,
            annonce_lbc="Custom Title",
            lien_annonce="",
            photos="",
            dossier_photos="",
            categorie="",
            pieces="",
            objet="Object",
            marques="Brand",
            modele="Model",
            quantite="",
            etat="",
            prix_neuf_unite="",
            prix_total="",
            prix_demande_unite="",
            prix_total_demande="",
            status="",
            a_publier="",
        )
        assert build_title(row) == "Custom Title"

    def test_fallback_to_object_brand_model(self):
        """Test fallback to object + brand + model."""
        row = SheetRow(
            row_index=1,
            annonce_lbc="",
            lien_annonce="",
            photos="",
            dossier_photos="",
            categorie="",
            pieces="",
            objet="Laptop",
            marques="Apple",
            modele="MacBook Pro",
            quantite="",
            etat="",
            prix_neuf_unite="",
            prix_total="",
            prix_demande_unite="",
            prix_total_demande="",
            status="",
            a_publier="",
        )
        assert build_title(row) == "Laptop - Apple - MacBook Pro"

    def test_filters_empty_and_dash_values(self):
        """Test that empty values and dashes are filtered."""
        row = SheetRow(
            row_index=1,
            annonce_lbc="",
            lien_annonce="",
            photos="",
            dossier_photos="",
            categorie="",
            pieces="",
            objet="Laptop",
            marques="-",
            modele="",
            quantite="",
            etat="",
            prix_neuf_unite="",
            prix_total="",
            prix_demande_unite="",
            prix_total_demande="",
            status="",
            a_publier="",
        )
        assert build_title(row) == "Laptop"

    def test_truncates_to_70_chars(self):
        """Test that title is truncated to 70 characters."""
        long_text = "A" * 100
        row = SheetRow(
            row_index=1,
            annonce_lbc="",
            lien_annonce="",
            photos="",
            dossier_photos="",
            categorie="",
            pieces="",
            objet=long_text,
            marques="",
            modele="",
            quantite="",
            etat="",
            prix_neuf_unite="",
            prix_total="",
            prix_demande_unite="",
            prix_total_demande="",
            status="",
            a_publier="",
        )
        title = build_title(row)
        assert len(title) <= 70


class TestBuildDescription:
    """Test build_description function."""

    def test_includes_all_fields(self):
        """Test that description includes all relevant fields."""
        row = SheetRow(
            row_index=1,
            annonce_lbc="",
            lien_annonce="",
            photos="",
            dossier_photos="",
            categorie="Electronics",
            pieces="Living Room",
            objet="Laptop",
            marques="Apple",
            modele="MacBook Pro",
            quantite="1",
            etat="Excellent",
            prix_neuf_unite="2000,00 €",
            prix_total="2000,00 €",
            prix_demande_unite="1500,00 €",
            prix_total_demande="1500,00 €",
            status="",
            a_publier="",
        )
        desc = build_description(row)
        assert "Objet: Laptop" in desc
        assert "Marque: Apple" in desc
        assert "Modèle: MacBook Pro" in desc
        assert "État: Excellent" in desc
        assert "Quantité: 1" in desc
        assert "Pièce: Living Room" in desc
        assert "Catégorie (source): Electronics" in desc
        assert "Prix neuf (unité): 2000 €" in desc
        assert "Prix demandé (unité): 1500 €" in desc

    def test_filters_empty_values(self):
        """Test that empty values are filtered from description."""
        row = SheetRow(
            row_index=1,
            annonce_lbc="",
            lien_annonce="",
            photos="",
            dossier_photos="",
            categorie="",
            pieces="",
            objet="Laptop",
            marques="-",
            modele="",
            quantite="",
            etat="Good",
            prix_neuf_unite="",
            prix_total="",
            prix_demande_unite="",
            prix_total_demande="",
            status="",
            a_publier="",
        )
        desc = build_description(row)
        assert "Objet: Laptop" in desc
        assert "État: Good" in desc
        assert "Marque:" not in desc  # Filtered because it's a dash
        assert "Modèle:" not in desc  # Filtered because it's empty


class TestSheetRow:
    """Test SheetRow class."""

    def test_should_publish_when_all_conditions_met(self):
        """Test should_publish returns True when all conditions are met."""
        test_cases = ["oui", "true", "1", "x", "yes", "OUI", "True", "YES"]

        for a_publier_value in test_cases:
            row = SheetRow(
                row_index=1,
                annonce_lbc="",
                lien_annonce="",  # Empty
                photos="",
                dossier_photos="",
                categorie="",
                pieces="",
                objet="",
                marques="",
                modele="",
                quantite="",
                etat="",
                prix_neuf_unite="",
                prix_total="",
                prix_demande_unite="",
                prix_total_demande="",
                status="en vente",  # Valid status
                a_publier=a_publier_value,
            )
            assert row.should_publish() is True

    def test_should_publish_with_empty_status(self):
        """Test should_publish with empty status."""
        row = SheetRow(
            row_index=1,
            annonce_lbc="",
            lien_annonce="",
            photos="",
            dossier_photos="",
            categorie="",
            pieces="",
            objet="",
            marques="",
            modele="",
            quantite="",
            etat="",
            prix_neuf_unite="",
            prix_total="",
            prix_demande_unite="",
            prix_total_demande="",
            status="",  # Empty is valid
            a_publier="oui",
        )
        assert row.should_publish() is True

    def test_should_not_publish_when_lien_exists(self):
        """Test should_publish returns False when lien_annonce exists."""
        row = SheetRow(
            row_index=1,
            annonce_lbc="",
            lien_annonce="https://example.com",  # Not empty
            photos="",
            dossier_photos="",
            categorie="",
            pieces="",
            objet="",
            marques="",
            modele="",
            quantite="",
            etat="",
            prix_neuf_unite="",
            prix_total="",
            prix_demande_unite="",
            prix_total_demande="",
            status="en vente",
            a_publier="oui",
        )
        assert row.should_publish() is False

    def test_should_not_publish_when_a_publier_false(self):
        """Test should_publish returns False when a_publier is false."""
        row = SheetRow(
            row_index=1,
            annonce_lbc="",
            lien_annonce="",
            photos="",
            dossier_photos="",
            categorie="",
            pieces="",
            objet="",
            marques="",
            modele="",
            quantite="",
            etat="",
            prix_neuf_unite="",
            prix_total="",
            prix_demande_unite="",
            prix_total_demande="",
            status="en vente",
            a_publier="non",  # Not a valid "true" value
        )
        assert row.should_publish() is False

    def test_should_not_publish_with_invalid_status(self):
        """Test should_publish returns False with invalid status."""
        row = SheetRow(
            row_index=1,
            annonce_lbc="",
            lien_annonce="",
            photos="",
            dossier_photos="",
            categorie="",
            pieces="",
            objet="",
            marques="",
            modele="",
            quantite="",
            etat="",
            prix_neuf_unite="",
            prix_total="",
            prix_demande_unite="",
            prix_total_demande="",
            status="vendu",  # Invalid status
            a_publier="oui",
        )
        assert row.should_publish() is False

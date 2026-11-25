"""Fixtures : exports produits (tests `donnees`, sautés s'ils sont absents)."""

import pytest

from pc.cli import EXPORT, RAW


@pytest.fixture(scope="session")
def export():
    if not (EXPORT / "systeme_horaire.parquet").exists():
        pytest.skip(f"exports absents : {EXPORT} (lancer `pc download` puis `pc build`)")
    return EXPORT


@pytest.fixture(scope="session")
def raw():
    if not (RAW / "manifeste.json").exists():
        pytest.skip(f"sources absentes : {RAW} (lancer `pc download`)")
    return RAW

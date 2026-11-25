import pytest

from pc.cli import main


def test_cle_inconnue_refusee(tmp_path):
    with pytest.raises(SystemExit):
        main(["download", "--raw", str(tmp_path), "source_inexistante"])


def test_check_sans_export_echoue(tmp_path):
    assert main(["check", "--raw", str(tmp_path), "--export", str(tmp_path)]) == 1

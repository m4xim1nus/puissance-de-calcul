from pc.cli import main


def test_commandes_repondent():
    for commande in ("download", "build", "check"):
        assert main([commande]) == 0

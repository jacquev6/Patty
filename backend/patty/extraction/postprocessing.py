def cleanup_slashes(t: str, /) -> str:
    """
    Nettoyage chirurgical des erreurs de backslashs générées par le LLM
    AVANT de tenter de réparer la structure JSON.
    """
    assert not t.startswith("```"), "Le texte ne doit plus contenir de balises Markdown"
    assert not t.endswith("```"), "Le texte ne doit plus contenir de balises Markdown"
    assert t == t.strip(), "Le texte ne doit plus contenir d'espaces superflus aux extrémités"

    # -----------------------------------------------------------
    # RÉPARATIONS DES BACKSLASHS (Ordre important)
    # -----------------------------------------------------------

    # A. Sauts de ligne : \\n devient \n
    # Le LLM écrit souvent 2 chars (\ + n), on veut le caractère de contrôle.
    t = t.replace("\\\\n", "\\n")

    # B. Cas critique des guillemets avec 3 backslashs : \\\" devient \"
    # C'est ton erreur actuelle : \color{\\\" -> le parser voit 3 barres.
    # On remplace par \" (1 barre + guillemet) pour que ce soit un guillemet échappé valide.
    t = t.replace('\\\\\\"', '\\"')

    # C. Cas critique des guillemets avec 2 backslashs : \\" devient \"
    # Cela arrive quand le LLM essaie d'échapper le backslash devant le guillemet.
    # Dans une string JSON, \\" signifie "Backslash littéral + Fin de string".
    # Cela CASSE le json. On remplace par \" (Guillemet échappé).
    t = t.replace('\\\\"', '\\"')

    # D. LaTeX général : \\\\bf devient \\bf (4 barres -> 2 barres)
    # Pour avoir un seul backslash littéral en JSON, il en faut 2 dans le code source.
    # Si le LLM en met 4, on réduit à 2.
    t = t.replace("\\\\\\\\", "\\\\")

    # E. Nettoyage résiduel (3 barres -> 2 barres)
    # Au cas où il reste des \\\bf
    t = t.replace("\\\\\\", "\\\\")

    return t

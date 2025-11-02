#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier que tous les modules sont correctement gérés.
Ce script teste les imports et affiche les modules manquants.
"""


import sys
import importlib

def tester_import(nom_module, nom_package=None):
    """Teste l'import d'un module et retourne le résultat."""
    try:
        if nom_package:
            importlib.import_module(nom_package)
        else:
            importlib.import_module(nom_module)
        return True, None
    except ImportError as e:
        return False, str(e)

def main():
    """Fonction principale de test."""
    print("🔍 Test des imports des modules...")
    print("=" * 50)

    # Liste des modules à tester
    modules_a_tester = [
        ("docx", "docx"),
        ("sklearn", "sklearn"),
        ("fitz", "fitz"),
        ("spacy", "spacy"),
        ("customtkinter", "customtkinter"),
        ("fastapi", "fastapi"),
        ("uvicorn", "uvicorn"),
        ("pydantic", "pydantic"),
        ("yt_dlp", "yt_dlp"),
        
    ]

    modules_ok = []
    modules_manquants = []

    for nom_module, nom_package in modules_a_tester:
        print(f"Test de {nom_module}...", end=" ")
        success, error = tester_import(nom_module, nom_package)

        if success:
            print("✅ OK")
            modules_ok.append(nom_module)
        else:
            print("❌ MANQUANT")
            print(f"   Erreur: {error}")
            modules_manquants.append((nom_module, error))

    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ:")
    print(f"✅ Modules disponibles: {len(modules_ok)}")
    print(f"❌ Modules manquants: {len(modules_manquants)}")

    if modules_ok:
        print("\n✅ Modules OK:")
        for module in modules_ok:
            print(f"   - {module}")

    if modules_manquants:
        print("\n❌ Modules manquants:")
        for module, error in modules_manquants:
            print(f"   - {module}: {error}")

        print("\n💡 Pour installer les modules manquants:")
        print("   pip install -r 'installation guide/requirements.txt'")

    print("\n✨ Test terminé!")
    return len(modules_manquants) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
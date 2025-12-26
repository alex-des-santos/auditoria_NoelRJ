#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificação pré-deploy para Streamlit Cloud
Verifica se todos os arquivos necessários estão presentes e configurados corretamente
"""

import os
import sys
from pathlib import Path

# Force UTF-8 encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def check_file_exists(filename: str, required: bool = True) -> bool:
    """Verifica se um arquivo existe"""
    exists = Path(filename).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    print(f"{status} {filename}: {'Encontrado' if exists else 'NÃO encontrado'}")
    return exists


def check_gitignore() -> bool:
    """Verifica se o .gitignore está configurado corretamente"""
    if not Path(".gitignore").exists():
        print("❌ .gitignore não encontrado!")
        return False

    with open(".gitignore", "r") as f:
        content = f.read()

    checks = [
        ("*.csv", "Arquivos CSV (dados sensíveis)"),
        (".venv/", "Ambiente virtual"),
        ("__pycache__/", "Cache Python"),
    ]

    all_ok = True
    for pattern, desc in checks:
        if pattern in content:
            print(f"✅ .gitignore protege: {desc}")
        else:
            print(f"❌ .gitignore NÃO protege: {desc}")
            all_ok = False

    return all_ok


def check_requirements() -> bool:
    """Verifica se requirements.txt está presente e válido"""
    if not Path("requirements.txt").exists():
        print("❌ requirements.txt não encontrado!")
        return False

    with open("requirements.txt", "r") as f:
        content = f.read()

    required_packages = ["streamlit", "pandas", "plotly"]
    all_ok = True

    for package in required_packages:
        if package in content.lower():
            print(f"✅ Dependência encontrada: {package}")
        else:
            print(f"❌ Dependência faltando: {package}")
            all_ok = False

    return all_ok


def main():
    print("🔍 Verificando requisitos para deploy no Streamlit Cloud...\n")

    # Arquivos obrigatórios
    print("📁 Arquivos Obrigatórios:")
    required_files = {
        "app.py": True,
        "requirements.txt": True,
        ".gitignore": True,
    }

    files_ok = all(check_file_exists(f, req) for f, req in required_files.items())

    # Arquivos recomendados
    print("\n📄 Arquivos Recomendados:")
    recommended_files = {
        "README.md": False,
        "LICENSE": False,
        "context.md": False,
        "context_summary.md": False,
    }

    for f, req in recommended_files.items():
        check_file_exists(f, req)

    # Verificações específicas
    print("\n🔒 Verificação do .gitignore:")
    gitignore_ok = check_gitignore()

    print("\n📦 Verificação do requirements.txt:")
    requirements_ok = check_requirements()

    # Verificar se CSV não será commitado
    print("\n⚠️ Verificação de Dados Sensíveis:")
    csv_files = list(Path(".").glob("*.csv"))
    if csv_files:
        print(f"⚠️ Encontrados {len(csv_files)} arquivo(s) CSV:")
        for csv in csv_files:
            print(f"   - {csv}")
        print("   ⚠️ Certifique-se de que estão no .gitignore!")
    else:
        print("✅ Nenhum arquivo CSV encontrado no diretório raiz")

    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO:")
    print("="*60)

    if files_ok and gitignore_ok and requirements_ok:
        print("✅ Projeto pronto para deploy no Streamlit Cloud!")
        print("\n📝 Próximos passos:")
        print("1. git init")
        print("2. git add .")
        print("3. git commit -m 'Initial commit'")
        print("4. Criar repositório no GitHub")
        print("5. git remote add origin <URL>")
        print("6. git push -u origin main")
        print("7. Deploy em https://share.streamlit.io")
        return 0
    else:
        print("❌ Alguns requisitos não foram atendidos.")
        print("   Corrija os itens marcados com ❌ antes de fazer deploy.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

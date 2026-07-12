"""Telechargement automatique du dataset Kaggle Credit Card Fraud.

La source officielle du projet est Kaggle via:
    kagglehub.dataset_download("mlg-ulb/creditcardfraud")

Le fichier `data/raw/creditcard.csv` est uniquement un cache local non versionne.
"""

import shutil
import time
import subprocess
from pathlib import Path
from typing import Optional

import kagglehub
from loguru import logger

from config.settings import DATA_RAW


def download_real_dataset(retries: int = 3, delay: int = 5) -> Path:
    """Telecharge le dataset reel depuis Kaggle et le copie dans data/raw/.
    
    Args:
        retries: Nombre de tentatives en cas d'echec
        delay: Delai entre les tentatives (secondes)
    """
    for attempt in range(retries):
        try:
            logger.info(f"Tentative {attempt + 1}/{retries} - Telechargement du dataset depuis Kaggle...")
            
            # Telechargement avec timeout via kagglehub
            path = kagglehub.dataset_download("mlg-ulb/creditcardfraud")
            
            dataset_path = Path(path)
            csv_file = dataset_path / "creditcard.csv"

            if not csv_file.exists():
                # Chercher recursivement
                found = list(dataset_path.rglob("creditcard.csv"))
                if not found:
                    raise FileNotFoundError(
                        f"creditcard.csv non trouve dans: {dataset_path}"
                    )
                csv_file = found[0]

            destination = DATA_RAW / "creditcard.csv"
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(csv_file, destination)

            logger.info(f"Dataset copie vers: {destination}")
            return destination
            
        except Exception as e:
            logger.warning(f"Tentative {attempt + 1} echouee: {e}")
            if attempt < retries - 1:
                logger.info(f"Attente de {delay} secondes avant de reessayer...")
                time.sleep(delay)
            else:
                logger.error("Toutes les tentatives ont echoue")
                raise


def download_with_kaggle_cli() -> Path:
    """Alternative: Utiliser la CLI Kaggle pour le telechargement."""
    logger.info("Tentative de telechargement avec Kaggle CLI...")
    
    destination = DATA_RAW / "creditcard.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Verifier si kaggle est installe
        subprocess.run(["kaggle", "--version"], check=True, capture_output=True)
        
        # Telecharger avec kaggle CLI
        subprocess.run([
            "kaggle", "datasets", "download", 
            "mlg-ulb/creditcardfraud", 
            "-p", str(DATA_RAW),
            "--force"
        ], check=True, capture_output=True)
        
        # Decompresser
        zip_file = DATA_RAW / "creditcardfraud.zip"
        if zip_file.exists():
            subprocess.run([
                "unzip", "-o", str(zip_file), 
                "-d", str(DATA_RAW)
            ], check=True, capture_output=True)
            zip_file.unlink()  # Supprimer le zip apres extraction
            
        logger.info(f"Dataset telecharge avec Kaggle CLI vers: {destination}")
        return destination
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur avec Kaggle CLI: {e.stderr.decode() if e.stderr else str(e)}")
        raise
    except FileNotFoundError:
        logger.error("Kaggle CLI non installe. Installez avec: pip install kaggle")
        raise


def ensure_dataset(use_cli_fallback: bool = True) -> Path:
    """Verifie que le dataset existe, sinon le telecharge.
    
    Args:
        use_cli_fallback: Utiliser Kaggle CLI comme fallback si kagglehub echoue
    """
    dest = DATA_RAW / "creditcard.csv"
    if dest.exists():
        logger.info(f"Dataset deja present: {dest}")
        return dest
    
    # Essayer d'abord avec kagglehub
    try:
        return download_real_dataset()
    except Exception as e:
        logger.warning(f"Telechargement avec kagglehub echoue: {e}")
        
        if use_cli_fallback:
            logger.info("Tentative avec Kaggle CLI...")
            try:
                return download_with_kaggle_cli()
            except Exception as cli_error:
                logger.error(f"Kaggle CLI a aussi echoue: {cli_error}")
                logger.error("Veuillez telecharger manuellement le dataset depuis:")
                logger.error("https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud")
                raise
        else:
            raise
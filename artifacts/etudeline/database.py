from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os

# Configuration de la base de données avec diagnostic
EXTERNAL_DB_URL = os.getenv("EXTERNAL_DATABASE_URL") or os.getenv("RENDER_DATABASE_URL")
REPLIT_DB_URL = os.getenv("DATABASE_URL")

# PRIORITÉ : EXTERNAL_DATABASE_URL ou RENDER_DATABASE_URL (Render PostgreSQL) > DATABASE_URL (Replit)
if EXTERNAL_DB_URL:
    DATABASE_URL = EXTERNAL_DB_URL
    print("=" * 70)
    print("🔵 CONNEXION À LA BASE DE DONNÉES EXTERNE (RENDER POSTGRESQL)")
    print(f"   Host: {EXTERNAL_DB_URL.split('@')[1].split('/')[0] if '@' in EXTERNAL_DB_URL else 'unknown'}")
    print("   ⚠️  ATTENTION : Vos données sont sur cette base - NE PAS LA SUPPRIMER")
    print("=" * 70)
elif REPLIT_DB_URL:
    DATABASE_URL = REPLIT_DB_URL
    print("=" * 70)
    print("⚠️  CONNEXION À LA BASE DE DONNÉES REPLIT (LOCALE)")
    print("   PROBLÈME : Cette base n'est PAS persistante sur Render !")
    print("   SOLUTION : Configurez EXTERNAL_DATABASE_URL sur Render")
    print("=" * 70)
else:
    DATABASE_URL = "postgresql://user:password@localhost/dbname"
    print("=" * 70)
    print("❌ AUCUNE BASE DE DONNÉES CONFIGURÉE !")
    print("   Utilisation d'une base par défaut (NON FONCTIONNELLE)")
    print("=" * 70)

# Création de l'engine et de la session avec configuration SSL et connection pooling optimisé
engine = create_engine(
    DATABASE_URL,
    # Connection pooling pour production (100 profs + 12,000 étudiants)
    pool_size=10,              # Nombre de connexions maintenues dans le pool
    max_overflow=20,           # Connexions supplémentaires autorisées en pic de charge
    pool_timeout=30,           # Délai d'attente pour obtenir une connexion (secondes)
    pool_pre_ping=True,        # Vérifie que la connexion est vivante avant utilisation
    pool_recycle=300,          # Recycle les connexions après 5 minutes
    connect_args={"sslmode": "prefer"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Créer toutes les tables"""
    Base.metadata.create_all(bind=engine)

def reset_database():
    """Supprimer et recréer toutes les tables"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
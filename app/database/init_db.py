import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Define la ruta de la base de datos SQLite en la raíz del proyecto
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../leads.db"))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Crear el motor de la base de datos
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Crear el gestor de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para las clases/modelos
Base = declarative_base()

def init_db():
    """Crea las tablas en la base de datos si aún no existen."""
    # Importar los modelos aquí para asegurar que estén registrados antes de crear las tablas
    from app.database import models
    Base.metadata.create_all(bind=engine)

def get_db():
    """Generador de sesiones de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
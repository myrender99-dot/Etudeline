from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index, Table, LargeBinary, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Tables de liaison pour les relations many-to-many
professeur_ufrs = Table(
    'professeur_ufrs',
    Base.metadata,
    Column('professeur_id', Integer, ForeignKey('professeurs.id', ondelete='CASCADE'), primary_key=True),
    Column('ufr_id', String, ForeignKey('ufrs.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

professeur_filieres = Table(
    'professeur_filieres',
    Base.metadata,
    Column('professeur_id', Integer, ForeignKey('professeurs.id', ondelete='CASCADE'), primary_key=True),
    Column('filiere_id', String, ForeignKey('filieres.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow)
)

class Universite(Base):
    __tablename__ = "universites"
    
    id = Column(String, primary_key=True)
    nom = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    logo_url = Column(String(500), nullable=True)  # Deprecated - use logo_data instead
    logo_data = Column(LargeBinary, nullable=True)  # Image stockée en base de données
    logo_content_type = Column(String(50), nullable=True)  # e.g., 'image/jpeg', 'image/png'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    ufrs = relationship("UFR", back_populates="universite", cascade="all, delete-orphan")
    etudiants = relationship("Etudiant", back_populates="universite", cascade="all, delete-orphan")
    professeurs = relationship("Professeur", back_populates="universite")  # CASCADE via FK seulement
    administrateurs = relationship("Administrateur", back_populates="universite")  # CASCADE via FK seulement

class UFR(Base):
    __tablename__ = "ufrs"
    
    id = Column(String, primary_key=True)
    nom = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    universite_id = Column(String, ForeignKey("universites.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    universite = relationship("Universite", back_populates="ufrs")
    filieres = relationship("Filiere", back_populates="ufr", cascade="all, delete-orphan")
    etudiants = relationship("Etudiant", back_populates="ufr")
    professeurs = relationship("Professeur", back_populates="ufr")

class Filiere(Base):
    __tablename__ = "filieres"
    
    id = Column(String, primary_key=True)
    nom = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    ufr_id = Column(String, ForeignKey("ufrs.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    ufr = relationship("UFR", back_populates="filieres")
    matieres = relationship("Matiere", back_populates="filiere", cascade="all, delete-orphan")
    etudiants = relationship("Etudiant", back_populates="filiere")
    professeurs = relationship("Professeur", back_populates="filiere")
    chapitres = relationship("ChapitreComplet", back_populates="filiere")

class Matiere(Base):
    __tablename__ = "matieres"
    
    id = Column(String, primary_key=True)
    nom = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    filiere_id = Column(String, ForeignKey("filieres.id", ondelete="CASCADE"), nullable=False, index=True)
    niveau = Column(String(10), nullable=False, default="L1", index=True)
    semestre = Column(String(10), nullable=False, default="S1", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    filiere = relationship("Filiere", back_populates="matieres")
    professeurs = relationship("Professeur", back_populates="matiere_obj")
    chapitres = relationship("ChapitreComplet", back_populates="matiere")
    contents = relationship("Content", back_populates="matiere")

class Administrateur(Base):
    __tablename__ = "administrateurs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    is_main_admin = Column(Boolean, default=False)
    actif = Column(Boolean, default=True)
    universite_id = Column(String, ForeignKey("universites.id", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    universite = relationship("Universite", back_populates="administrateurs")

class Professeur(Base):
    __tablename__ = "professeurs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    specialite = Column(String(200), nullable=False)
    actif = Column(Boolean, default=True)
    universite_id = Column(String, ForeignKey("universites.id", ondelete="CASCADE"), nullable=True, index=True)
    # ANCIENNES COLONNES - Gardées pour rétrocompatibilité
    ufr_id = Column(String, ForeignKey("ufrs.id", ondelete="SET NULL"), nullable=True, index=True)
    filiere_id = Column(String, ForeignKey("filieres.id", ondelete="SET NULL"), nullable=True, index=True)
    matiere_id = Column(String, ForeignKey("matieres.id", ondelete="SET NULL"), nullable=True, index=True)
    matiere = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations - Anciennes (one-to-many) pour rétrocompatibilité
    universite = relationship("Universite", back_populates="professeurs")
    ufr = relationship("UFR", back_populates="professeurs", foreign_keys=[ufr_id])
    filiere = relationship("Filiere", back_populates="professeurs", foreign_keys=[filiere_id])
    matiere_obj = relationship("Matiere", back_populates="professeurs")
    chapitres = relationship("ChapitreComplet", back_populates="professeur", cascade="all, delete-orphan")
    contents = relationship("Content", back_populates="professeur", cascade="all, delete-orphan")
    
    # NOUVELLES RELATIONS Many-to-Many
    ufrs_multiples = relationship("UFR", secondary=professeur_ufrs, backref="professeurs_multiples")
    filieres_multiples = relationship("Filiere", secondary=professeur_filieres, backref="professeurs_multiples")

class Etudiant(Base):
    __tablename__ = "etudiants"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    niveau = Column(String(10), nullable=False)
    universite_id = Column(String, ForeignKey("universites.id", ondelete="CASCADE"), nullable=False, index=True)
    ufr_id = Column(String, ForeignKey("ufrs.id", ondelete="CASCADE"), nullable=False, index=True)
    filiere_id = Column(String, ForeignKey("filieres.id", ondelete="CASCADE"), nullable=False, index=True)
    statut_passage = Column(String(20), nullable=True)  # null, 'en_attente', 'validé', 'redoublant'
    subscription_active = Column(Boolean, default=False, nullable=False)
    subscription_start = Column(DateTime, nullable=True)
    subscription_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    universite = relationship("Universite", back_populates="etudiants")
    ufr = relationship("UFR", back_populates="etudiants")
    filiere = relationship("Filiere", back_populates="etudiants")
    passages = relationship("StudentPassage", back_populates="etudiant", cascade="all, delete-orphan")
    payment_requests = relationship("PaymentRequest", back_populates="etudiant", cascade="all, delete-orphan")
    documents = relationship("DocumentEtudiant", back_populates="etudiant", cascade="all, delete-orphan")

class Content(Base):
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    niveau = Column(String(10), nullable=False)
    semestre = Column(String(10), nullable=False)
    chapitre = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)
    texte = Column(Text, nullable=True)
    fichier_nom = Column(String(500), nullable=True)
    fichier_path = Column(String(1000), nullable=True)
    matiere_id = Column(String, ForeignKey("matieres.id"), nullable=True, index=True)
    created_by = Column(String(100), ForeignKey("professeurs.username", ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    matiere = relationship("Matiere", back_populates="contents")
    professeur = relationship("Professeur", back_populates="contents")

class ChapitreComplet(Base):
    __tablename__ = "chapitres_complets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    universite_id = Column(String, ForeignKey("universites.id", ondelete="CASCADE"), nullable=False, index=True)
    ufr_id = Column(String, ForeignKey("ufrs.id", ondelete="CASCADE"), nullable=False, index=True)
    filiere_id = Column(String, ForeignKey("filieres.id", ondelete="CASCADE"), nullable=False, index=True)
    matiere_id = Column(String, ForeignKey("matieres.id", ondelete="CASCADE"), nullable=False, index=True)
    niveau = Column(String(10), nullable=False)
    semestre = Column(String(10), nullable=False)
    chapitre = Column(String(200), nullable=False)
    titre = Column(String(500), nullable=False)
    
    # Cours
    cours_texte = Column(Text, nullable=True)
    cours_fichier_nom = Column(String(500), nullable=True)
    cours_fichier_path = Column(String(1000), nullable=True)
    
    # Exercices
    exercice_texte = Column(Text, nullable=True)
    exercice_fichier_nom = Column(String(500), nullable=True)
    exercice_fichier_path = Column(String(1000), nullable=True)
    
    # Solutions
    solution_texte = Column(Text, nullable=True)
    solution_fichier_nom = Column(String(500), nullable=True)
    solution_fichier_path = Column(String(1000), nullable=True)
    
    created_by = Column(String(100), ForeignKey("professeurs.username", ondelete='CASCADE'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    universite = relationship("Universite", foreign_keys=[universite_id])
    ufr = relationship("UFR", foreign_keys=[ufr_id])
    filiere = relationship("Filiere", back_populates="chapitres")
    matiere = relationship("Matiere", back_populates="chapitres")
    professeur = relationship("Professeur", back_populates="chapitres")
    commentaires = relationship("Commentaire", back_populates="chapitre", cascade="all, delete-orphan")

class Commentaire(Base):
    __tablename__ = "commentaires"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    texte = Column(Text, nullable=False)
    chapitre_id = Column(Integer, ForeignKey("chapitres_complets.id", ondelete='CASCADE'), nullable=False)
    auteur_type = Column(String(20), nullable=False)  # 'professeur' ou 'etudiant'
    auteur_id = Column(Integer, nullable=False)
    auteur_nom = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    chapitre = relationship("ChapitreComplet", back_populates="commentaires")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False)  # 'nouveau_chapitre', 'nouveau_commentaire'
    message = Column(String(500), nullable=False)
    destinataire_type = Column(String(20), nullable=False)  # 'prof' ou 'etudiant'
    destinataire_id = Column(Integer, nullable=False)
    lien = Column(String(500), nullable=True)  # URL ou chemin vers la ressource
    lue = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Métadonnées optionnelles pour faciliter les requêtes
    chapitre_id = Column(Integer, ForeignKey("chapitres_complets.id", ondelete='SET NULL'), nullable=True)
    universite_id = Column(String(36), ForeignKey("universites.id", ondelete='SET NULL'), nullable=True)

class PushSubscription(Base):
    """Abonnements aux notifications push Web Push API"""
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_type = Column(String(20), nullable=False)   # 'etudiant' ou 'prof'
    user_id = Column(Integer, nullable=False, index=True)
    endpoint = Column(Text, nullable=False, unique=True)
    p256dh = Column(Text, nullable=False)
    auth = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_push_user', 'user_type', 'user_id'),
    )


class ParametreSysteme(Base):
    __tablename__ = "parametres_systeme"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cle = Column(String(100), unique=True, nullable=False)
    valeur = Column(String(500), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ParametreUniversite(Base):
    """Paramètres configurables par université (téléchargements, passage de classe, etc.)"""
    __tablename__ = "parametres_universite"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    universite_id = Column(String, ForeignKey("universites.id", ondelete='CASCADE'), unique=True, nullable=False, index=True)
    telechargements_actifs = Column(Boolean, default=True, nullable=False)
    passage_classe_actif = Column(Boolean, default=True, nullable=False)
    messages_actifs = Column(Boolean, default=True, nullable=False)
    cours_en_ligne_actifs = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    universite = relationship("Universite", foreign_keys=[universite_id])

class PassageHierarchy(Base):
    """Règles de passage académique définies par l'administrateur"""
    __tablename__ = "passage_hierarchy"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    universite_id = Column(String, ForeignKey("universites.id", ondelete='CASCADE'), nullable=False, index=True)
    filiere_depart_id = Column(String, ForeignKey("filieres.id", ondelete='CASCADE'), nullable=False, index=True)
    niveau_depart = Column(String(10), nullable=False)
    filiere_arrivee_id = Column(String, ForeignKey("filieres.id", ondelete='CASCADE'), nullable=False, index=True)
    niveau_arrivee = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    universite = relationship("Universite", foreign_keys=[universite_id])
    filiere_depart = relationship("Filiere", foreign_keys=[filiere_depart_id])
    filiere_arrivee = relationship("Filiere", foreign_keys=[filiere_arrivee_id])
    
    # Index composite pour optimiser les recherches
    __table_args__ = (
        Index('idx_passage_depart', 'universite_id', 'filiere_depart_id', 'niveau_depart'),
        Index('idx_passage_arrivee', 'universite_id', 'filiere_arrivee_id', 'niveau_arrivee'),
    )

class StudentPassage(Base):
    """Historique des passages académiques des étudiants"""
    __tablename__ = "student_passage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("etudiants.id", ondelete='CASCADE'), nullable=False, index=True)
    old_filiere_id = Column(String, ForeignKey("filieres.id", ondelete='SET NULL'), nullable=True)
    old_niveau = Column(String(10), nullable=False)
    new_filiere_id = Column(String, ForeignKey("filieres.id", ondelete='SET NULL'), nullable=True)
    new_niveau = Column(String(10), nullable=True)
    statut = Column(String(20), nullable=False)  # 'passé' ou 'redoublant'
    date_validation = Column(DateTime, default=datetime.utcnow)
    annee_universitaire = Column(String(20), nullable=True)  # Ex: "2024-2025"
    
    # Relations
    etudiant = relationship("Etudiant", back_populates="passages")
    old_filiere = relationship("Filiere", foreign_keys=[old_filiere_id])
    new_filiere = relationship("Filiere", foreign_keys=[new_filiere_id])
    
    # Index pour optimiser les requêtes
    __table_args__ = (
        Index('idx_student_passage_student', 'student_id', 'date_validation'),
        Index('idx_student_passage_statut', 'statut', 'annee_universitaire'),
    )

class MessageProf(Base):
    """Messages envoyés par les professeurs aux étudiants avec ciblage hiérarchique"""
    __tablename__ = "messages_prof"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prof_id = Column(Integer, ForeignKey("professeurs.id", ondelete='CASCADE'), nullable=False, index=True)
    contenu = Column(Text, nullable=False)
    audio_file = Column(String(500), nullable=True)  # Chemin du fichier audio (optionnel)
    date_creation = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Ciblage hiérarchique (null = tous)
    universite_id = Column(String, ForeignKey("universites.id", ondelete='CASCADE'), nullable=False, index=True)
    ufr_id = Column(String, ForeignKey("ufrs.id", ondelete='CASCADE'), nullable=True, index=True)
    filiere_id = Column(String, ForeignKey("filieres.id", ondelete='CASCADE'), nullable=True, index=True)
    niveau = Column(String(10), nullable=True, index=True)  # L1, L2, L3, M1, M2
    semestre = Column(String(10), nullable=True)  # S1, S2
    matiere_id = Column(String, ForeignKey("matieres.id", ondelete='CASCADE'), nullable=True, index=True)
    
    # Relations
    professeur = relationship("Professeur", foreign_keys=[prof_id])
    universite = relationship("Universite", foreign_keys=[universite_id])
    ufr = relationship("UFR", foreign_keys=[ufr_id])
    filiere = relationship("Filiere", foreign_keys=[filiere_id])
    matiere = relationship("Matiere", foreign_keys=[matiere_id])
    statuts = relationship("MessageEtudiantStatut", back_populates="message", cascade="all, delete-orphan")
    
    # Index composite pour optimiser les recherches
    __table_args__ = (
        Index('idx_message_date', 'date_creation'),
        Index('idx_message_ciblage', 'universite_id', 'ufr_id', 'filiere_id', 'niveau'),
    )

class MessageEtudiantStatut(Base):
    """Statut de lecture/suppression des messages pour chaque étudiant"""
    __tablename__ = "messages_etudiant_statut"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages_prof.id", ondelete='CASCADE'), nullable=False, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id", ondelete='CASCADE'), nullable=False, index=True)
    lu = Column(Boolean, default=False, nullable=False)
    supprime = Column(Boolean, default=False, nullable=False)
    date_lecture = Column(DateTime, nullable=True)
    date_suppression = Column(DateTime, nullable=True)
    
    # Relations
    message = relationship("MessageProf", back_populates="statuts")
    etudiant = relationship("Etudiant", foreign_keys=[etudiant_id])
    
    # Index composite pour optimiser les recherches
    __table_args__ = (
        Index('idx_statut_etudiant_message', 'etudiant_id', 'message_id'),
        Index('idx_statut_non_supprime', 'etudiant_id', 'supprime'),
    )

class ScheduledCourse(Base):
    """Cours en ligne programmés avec Jitsi"""
    __tablename__ = "scheduled_courses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    prof_id = Column(Integer, ForeignKey("professeurs.id", ondelete='CASCADE'), nullable=False, index=True)
    universite_id = Column(String, ForeignKey("universites.id", ondelete='CASCADE'), nullable=False, index=True)
    ufr_id = Column(String, ForeignKey("ufrs.id", ondelete='CASCADE'), nullable=True, index=True)
    filiere_id = Column(String, ForeignKey("filieres.id", ondelete='CASCADE'), nullable=True, index=True)
    matiere_id = Column(String, ForeignKey("matieres.id", ondelete='CASCADE'), nullable=True, index=True)
    
    filiere = Column(String(100), nullable=False)
    niveau = Column(String(10), nullable=False)
    semestre = Column(String(10), nullable=False)
    matiere = Column(String(200), nullable=False)
    
    cours_date = Column(String(10), nullable=False)
    cours_heure = Column(String(5), nullable=False)
    duree_minutes = Column(Integer, nullable=False, default=60)
    
    jitsi_link = Column(String(500), nullable=False)
    
    notification_24h_sent = Column(Boolean, default=False, nullable=False)
    notification_1h_sent = Column(Boolean, default=False, nullable=False)
    notification_debut_sent = Column(Boolean, default=False, nullable=False)
    
    statut = Column(String(20), default='programme', nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    professeur = relationship("Professeur", foreign_keys=[prof_id])
    universite = relationship("Universite", foreign_keys=[universite_id])
    ufr_rel = relationship("UFR", foreign_keys=[ufr_id])
    filiere_rel = relationship("Filiere", foreign_keys=[filiere_id])
    matiere_rel = relationship("Matiere", foreign_keys=[matiere_id])
    
    __table_args__ = (
        Index('idx_scheduled_course_date', 'cours_date', 'cours_heure'),
        Index('idx_scheduled_course_prof', 'prof_id', 'cours_date'),
        Index('idx_scheduled_course_filiere', 'filiere_id', 'niveau', 'semestre'),
    )


class PaymentRequest(Base):
    __tablename__ = "payment_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("etudiants.id", ondelete="CASCADE"), nullable=False, index=True)
    payment_method = Column(String(20), nullable=False)  # orange / wave
    amount = Column(Integer, default=490, nullable=False)
    proof_image_path = Column(String(500), nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending / approved / rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    etudiant = relationship("Etudiant", back_populates="payment_requests")


class StudentDailySession(Base):
    """Enregistre les connexions uniques des étudiants par jour"""
    __tablename__ = "student_daily_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    etudiant = relationship("Etudiant", foreign_keys=[etudiant_id])

    __table_args__ = (
        Index('idx_daily_session_unique', 'etudiant_id', 'date', unique=True),
    )


class DocumentEtudiant(Base):
    """Documents personnels uploadés par les étudiants (étagère numérique)"""
    __tablename__ = "documents_etudiants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id", ondelete="CASCADE"), nullable=False, index=True)
    universite_id = Column(String, ForeignKey("universites.id", ondelete="CASCADE"), nullable=False, index=True)
    ufr_id = Column(String, ForeignKey("ufrs.id", ondelete="CASCADE"), nullable=True, index=True)
    filiere_id = Column(String, ForeignKey("filieres.id", ondelete="CASCADE"), nullable=True, index=True)
    matiere_id = Column(String, ForeignKey("matieres.id", ondelete="SET NULL"), nullable=True, index=True)

    niveau = Column(String(10), nullable=True)              # L1, L2, L3, M1, M2...
    semestre = Column(String(10), nullable=True)           # S1, S2, S3...

    nom_affichage = Column(String(255), nullable=False)    # Nom éditable par l'étudiant
    fichier_nom = Column(String(500), nullable=False)      # Nom original du fichier
    fichier_path = Column(String(1000), nullable=False)    # Chemin de stockage
    type_document = Column(String(100), nullable=True)     # cours, exercice, solution, examen...
    description = Column(Text, nullable=True)
    taille = Column(Integer, nullable=True)                # Taille en octets

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    etudiant = relationship("Etudiant", back_populates="documents")
    universite = relationship("Universite", foreign_keys=[universite_id])
    ufr = relationship("UFR", foreign_keys=[ufr_id])
    filiere = relationship("Filiere", foreign_keys=[filiere_id])
    matiere = relationship("Matiere", foreign_keys=[matiere_id])

    __table_args__ = (
        Index('idx_doc_etudiant', 'etudiant_id', 'created_at'),
        Index('idx_doc_filiere', 'filiere_id', 'matiere_id'),
    )
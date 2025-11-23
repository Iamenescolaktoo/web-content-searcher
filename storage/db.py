import os
import json
import datetime
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, sessionmaker

# ------------------------------
# DATABASE CONFIG
# ------------------------------

DB_URL = os.getenv("DB_URL", "sqlite:///news.db")

# For AWS RDS use something like:
# DB_URL="postgresql+psycopg2://admin:PASSWORD@your-rds-host:5432/newsdb"

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,       # detects stale AWS connections
    pool_size=5,              # safe defaults
    max_overflow=10,
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# ------------------------------
# MODELS
# ------------------------------

class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True)
    title = Column(Text)
    source = Column(Text)
    datetime = Column(Text)
    category = Column(String(50))
    sentiment = Column(String(50))
    toxicity = Column(Float)
    keywords = Column(Text)     # stored as JSON string
    entities = Column(Text)     # stored as JSON string
    risk_point = Column(Integer)
    created_at = Column(Text)


class UserEmail(Base):
    __tablename__ = "user_emails"

    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, nullable=False)


class UserStar(Base):
    __tablename__ = "user_stars"

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey("user_emails.id"))
    news_id = Column(Integer, ForeignKey("news_items.id"))
    starred_at = Column(Text)


# ------------------------------
# INITIALIZATION
# ------------------------------

def init_db():
    """Create tables if missing (AWS-friendly)."""
    Base.metadata.create_all(engine)


# ------------------------------
# WRITE OPERATIONS
# ------------------------------

def save_news_item(rec: dict):
    """Stores one processed news record in the DB."""
    with SessionLocal() as s:
        item = NewsItem(
            title=rec.get("title"),
            source=rec.get("source"),
            datetime=rec.get("datetime"),
            category=rec.get("category"),
            sentiment=rec.get("sentiment"),
            toxicity=float(rec.get("toxicity") or 0),
            keywords=json.dumps(rec.get("keywords", []), ensure_ascii=False),
            entities=json.dumps(rec.get("entities", []), ensure_ascii=False),
            risk_point=int(rec.get("risk_point", 0)),
            created_at=datetime.datetime.utcnow().isoformat()
        )
        s.add(item)
        s.commit()


def save_user_email(email: str):
    """Store email if unique."""
    with SessionLocal() as s:
        exists = s.query(UserEmail).filter_by(email=email).first()
        if exists:
            return False
        s.add(UserEmail(email=email))
        s.commit()
        return True


def save_star(email: str, news_id: int):
    """Record that a user starred a news item."""
    with SessionLocal() as s:

        user = s.query(UserEmail).filter_by(email=email).first()
        if not user:
            # auto-create user email if not stored yet
            user = UserEmail(email=email)
            s.add(user)
            s.commit()
            s.refresh(user)

        star = UserStar(
            email_id=user.id,
            news_id=news_id,
            starred_at=datetime.datetime.utcnow().isoformat()
        )
        s.add(star)
        s.commit()
        return True


# ------------------------------
# READ OPERATIONS
# ------------------------------

def fetch_news_for_date(date_str: str):
    """Return all news from a specific date, sorted by risk."""
    start = f"{date_str}T00:00:00"
    end = f"{date_str}T23:59:59"

    with SessionLocal() as s:
        rows = (
            s.query(NewsItem)
            .filter(NewsItem.created_at >= start, NewsItem.created_at <= end)
            .order_by(NewsItem.risk_point.desc(), NewsItem.created_at.desc())
            .all()
        )

        out = []
        for r in rows:
            out.append({
                "title": r.title,
                "source": r.source,
                "datetime": r.datetime,
                "category": r.category,
                "sentiment": r.sentiment,
                "toxicity": r.toxicity,
                "keywords": json.loads(r.keywords or "[]"),
                "entities": json.loads(r.entities or "[]"),
                "risk_point": r.risk_point,
                "created_at": r.created_at,
            })
        return out

import os, json, datetime
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DB_URL", "sqlite:///news.db")
engine = create_engine(DB_URL, future=True)

def init_db():
    with engine.begin() as conn:
        conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS news_items (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT,
          source TEXT,
          datetime TEXT,
          category TEXT,
          sentiment TEXT,
          toxicity REAL,
          keywords TEXT,
          entities TEXT,
          risk_point INTEGER,
          created_at TEXT
        )
        """)
        conn.commit()

def save_news_item(rec: dict):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO news_items (title, source, datetime, category, sentiment, toxicity, keywords, entities, risk_point, created_at)
            VALUES (:title, :source, :datetime, :category, :sentiment, :toxicity, :keywords, :entities, :risk_point, :created_at)
        """), {
            "title": rec.get("title"),
            "source": rec.get("source"),
            "datetime": rec.get("datetime"),
            "category": rec.get("category"),
            "sentiment": rec.get("sentiment"),
            "toxicity": rec.get("toxicity"),
            "keywords": json.dumps(rec.get("keywords", []), ensure_ascii=False),
            "entities": json.dumps(rec.get("entities", []), ensure_ascii=False),
            "risk_point": int(rec.get("risk_point", 0)),
            "created_at": datetime.datetime.utcnow().isoformat()
        })

def fetch_news_for_date(date_str: str):
    start = f"{date_str}T00:00:00"; end = f"{date_str}T23:59:59"
    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT title, source, datetime, category, sentiment, toxicity, keywords, entities, risk_point, created_at
            FROM news_items
            WHERE created_at BETWEEN :start AND :end
            ORDER BY risk_point DESC, created_at DESC
        """), {"start": start, "end": end}).mappings().all()
        return [dict(r) for r in rows]

def save_user_email(email):
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.orm import declarative_base, sessionmaker

    Base = declarative_base()
    engine = create_engine("sqlite:///news.db")
    Session = sessionmaker(bind=engine)

    class UserEmail(Base):
        __tablename__ = "user_emails"
        id = Column(Integer, primary_key=True)
        email = Column(String, unique=True, nullable=False)

    Base.metadata.create_all(engine)

    with Session() as s:
        existing = s.query(UserEmail).filter_by(email=email).first()
        if existing:
            return False
        s.add(UserEmail(email=email))
        s.commit()
        return True

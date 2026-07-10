import hashlib
import re
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. DATABASE SETUP
DATABASE_URL = "sqlite:///./urls.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class URLMap(Base):
    __tablename__ = "url_maps"
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String, nullable=False)
    short_hash = Column(String, unique=True, index=True, nullable=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 2. FASTAPI CONFIGURATION & TEMPLATES
app = FastAPI(title="Secure URL Shortener API")

# Mount directories to securely serve CSS static files and HTML templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Helper utility functions
def generate_short_hash(url: str) -> str:
    hash_object = hashlib.md5(url.encode())
    return hash_object.hexdigest()[:6]

def is_valid_url(url: str) -> bool:
    regex = re.compile(
        r'^(?:http|ftp)s?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' 
        r'localhost|' 
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' 
        r'(?::\d+)?' 
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

# 3. ENDPOINTS
@app.get("/", response_class=HTMLResponse)
def serve_ui(request: Request):
    """Serves the decoupled HTML template file to the browser user."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/shorten", status_code=status.HTTP_201_CREATED)
def shorten_url(long_url: str, db: Session = Depends(get_db)):
    if not is_valid_url(long_url):
        raise HTTPException(status_code=400, detail="Invalid URL format. Please include http:// or https://")

    existing_url = db.query(URLMap).filter(URLMap.long_url == long_url).first()
    if existing_url:
        return {"short_url": f"http://localhost:8000/{existing_url.short_hash}", "status": "Fetched existing mapping"}

    short_hash = generate_short_hash(long_url)
    collision_check = db.query(URLMap).filter(URLMap.short_hash == short_hash).first()
    if collision_check:
        short_hash = generate_short_hash(long_url + "-salt")

    new_mapping = URLMap(long_url=long_url, short_hash=short_hash)
    db.add(new_mapping)
    db.commit()
    db.refresh(new_mapping)

    return {"short_url": f"http://localhost:8000/{short_hash}", "status": "Successfully shortened"}

@app.get("/{short_hash}")
def redirect_to_long_url(short_hash: str, db: Session = Depends(get_db)):
    mapping = db.query(URLMap).filter(URLMap.short_hash == short_hash).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=mapping.long_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
from database.db import SessionLocal
from database.models import Download
from datetime import datetime


def add_download(user_id: int, link: str, quality: str):
    db = SessionLocal()
    download = Download(user_id=user_id, link=link, quality=quality,timestamp=datetime.utcnow())
    db.add(download)
    db.commit()
    db.close()





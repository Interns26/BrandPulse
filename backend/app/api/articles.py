from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.models import Article
from app.schemas.article import ArticleResponse

router = APIRouter(
    prefix="/api/articles",
    tags=["Articles"],
)


@router.get("", response_model=list[ArticleResponse])
def get_articles(
    db: Session = Depends(get_db),
):
    articles = (
        db.query(Article)
        .order_by(Article.published_at.desc())
        .all()
    )

    return articles
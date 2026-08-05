import datetime
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from atlas.database.models import Base, get_utc_now


# ============================================================
#  ATLAS TV — Video Content & Watch Tracking Models
# ============================================================


class TvVideo(Base):
    """Represents a curated YouTube video available on Atlas TV."""

    __tablename__ = "tv_videos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(nullable=False)
    youtube_id: Mapped[str] = mapped_column(nullable=False)
    thumbnail: Mapped[Optional[str]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    channel: Mapped[str] = mapped_column(nullable=False)  # tech, ai, careers, etc.
    tags: Mapped[Optional[str]] = mapped_column(nullable=True)  # comma-separated
    company: Mapped[Optional[str]] = mapped_column(nullable=True)
    is_sponsored: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_live: Mapped[bool] = mapped_column(default=False, nullable=False)
    viewer_count: Mapped[int] = mapped_column(default=0, nullable=False)
    duration_sec: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )


class TvWatchHistory(Base):
    """Tracks which users have watched which videos and whether XP was awarded."""

    __tablename__ = "tv_watch_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    video_id: Mapped[int] = mapped_column(
        ForeignKey("tv_videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    watched_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )
    xp_awarded: Mapped[bool] = mapped_column(default=False, nullable=False)


class TvBookmark(Base):
    """Records user-saved bookmarks for Atlas TV videos."""

    __tablename__ = "tv_bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    video_id: Mapped[int] = mapped_column(
        ForeignKey("tv_videos.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=get_utc_now, nullable=False
    )

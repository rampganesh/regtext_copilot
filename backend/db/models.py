from datetime import date

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class Source(Base):
    __tablename__ = 'sources'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(64), nullable=False)
    subject_area: Mapped[str] = mapped_column(String(128), nullable=False)
    approval_state: Mapped[str] = mapped_column(String(32), nullable=False, default='pending')
    content_owner: Mapped[str] = mapped_column(String(128), nullable=False, default='')
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)

    versions: Mapped[list['SourceVersion']] = relationship(back_populates='source')


class SourceVersion(Base):
    __tablename__ = 'source_versions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey('sources.id'), nullable=False)
    version_label: Mapped[str] = mapped_column(String(128), nullable=False)
    published_date: Mapped[date] = mapped_column(Date, nullable=False)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    pdf_path: Mapped[str] = mapped_column(String(1024), nullable=False, default='')

    source: Mapped['Source'] = relationship(back_populates='versions')
    chunks: Mapped[list['Chunk']] = relationship(back_populates='version')


class Chunk(Base):
    __tablename__ = 'chunks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int] = mapped_column(ForeignKey('source_versions.id'), nullable=False)
    chunk_type: Mapped[str] = mapped_column(String(32), nullable=False, default='paragraph')
    location_id: Mapped[str] = mapped_column(String(255), nullable=False)
    page_ref: Mapped[int | None] = mapped_column(Integer, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)

    version: Mapped['SourceVersion'] = relationship(back_populates='chunks')

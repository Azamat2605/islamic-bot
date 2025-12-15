import enum
from sqlalchemy import Enum, String, Float, Boolean, Text, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base


class PlaceType(enum.Enum):
    MOSQUE = "mosque"          # Мечеть
    RESTAURANT = "restaurant"  # Ресторан
    SHOP = "shop"              # Магазин (продукты)
    CLOTHES = "clothes"        # Магазин одежды
    OTHER = "other"            # Другое


class HalalPlace(Base):
    __tablename__ = "halal_places"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    place_type: Mapped[PlaceType] = mapped_column(Enum(PlaceType, native_enum=False), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    working_hours: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    photo_id: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships (HalalFavorite будет добавлен позже)
    # favorites: Mapped[list["HalalFavorite"]] = relationship(
    #     "HalalFavorite", back_populates="place", cascade="all, delete-orphan"
    # )

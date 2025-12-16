from __future__ import annotations
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from aiogram.utils.i18n import gettext as _


class UIAssets(BaseSettings):
    """
    Конфигурация UI-ассетов для главного меню и других визуальных элементов.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="UI_",
        extra="ignore"
    )

    # Изображение главного меню
    MAIN_MENU_IMAGE_URL: str = Field(
        default="https://i.postimg.cc/wTxRBQNK/Bez-nazvania-(10).jpg",
        description="URL изображения для главного меню (внешний хост)"
    )
    MAIN_MENU_IMAGE_FILE_ID: Optional[str] = Field(
        default=None,
        description="FileID изображения, если оно уже загружено в Telegram"
    )
    
    # Подпись и форматирование
    MAIN_MENU_CAPTION: str = Field(
        default="<b>🕌 Добро пожаловать в Исламский Помощник!</b>\n\n"
                "<i>Ваш персональный гид в мире исламских знаний и практик</i>\n\n"
                "Выберите раздел ниже:",
        description="Подпись к изображению главного меню с поддержкой HTML-форматирования"
    )
    MAIN_MENU_PARSE_MODE: str = Field(
        default="HTML",
        description="Режим парсинга для подписи (HTML или Markdown)"
    )

    def get_main_menu_image(self) -> tuple[Optional[str], Optional[str]]:
        """
        Возвращает (file_id, url) для изображения главного меню.
        Приоритет: FileID > URL.
        """
        if self.MAIN_MENU_IMAGE_FILE_ID:
            return self.MAIN_MENU_IMAGE_FILE_ID, None
        return None, self.MAIN_MENU_IMAGE_URL

    def get_localized_caption(self, username: str = "", language: str = "ru") -> str:
        """
        Возвращает локализованную подпись для главного меню.
        В реальной реализации здесь должна быть логика i18n.
        """
        # Временная реализация - возвращаем дефолтную подпись
        # В будущем можно интегрировать с i18n
        return self.MAIN_MENU_CAPTION


# Глобальный экземпляр конфигурации
ui_assets = UIAssets()

"""Модели данных бота для чтения."""

from dataclasses import dataclass


@dataclass
class Book:
    """Модель книги для отслеживания прогресса чтения."""

    title: str
    author: str
    total_pages: int
    current_page: int = 0

    def get_progress(self) -> float:
        """Возвращает процент прочитанного."""
        if self.total_pages == 0:
            return 0.0
        return round((self.current_page / self.total_pages) * 100, 2)

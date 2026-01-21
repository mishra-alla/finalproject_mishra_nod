# valutatrade_hub/parser_service/scheduler.py

"""
Планировщик для периодического обновления курсов.
"""

import time
import threading
import logging
from typing import Optional

from .updater import RatesUpdater


class RatesScheduler:
    """Планировщик обновления курсов"""

    def __init__(self, interval_minutes: int = 5):
        self.interval = interval_minutes * 60  # в секундах
        self.updater = RatesUpdater()
        self.logger = logging.getLogger(__name__)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Запускает планировщик в отдельном потоке"""
        if self._thread and self._thread.is_alive():
            self.logger.warning("Scheduler already running")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.logger.info(f"Scheduler started (interval: {self.interval // 60} min)")

    def stop(self) -> None:
        """Останавливает планировщик"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info("Scheduler stopped")

    def _run(self) -> None:
        """Основной цикл планировщика"""
        self.logger.info("Scheduler running...")
        while not self._stop_event.is_set():
            try:
                self.logger.info("Scheduled update started")
                self.updater.run_update()
                self.logger.info("Scheduled update completed")
            except Exception as e:
                self.logger.error(f"Scheduled update failed: {e}")
            # Ждем указанный интервал или прерывание
            for _ in range(self.interval):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

    def run_once(self) -> None:
        """Запускает одно обновление."""
        self.logger.info("Manual scheduled update")
        self.updater.run_update()

"""
Text typing manager with lock to prevent double-typing bugs.
"""
import keyboard
import threading
import time
from config import TYPING_DELAY_INITIAL, TYPING_DELAY_PER_CHAR, TYPING_DELAY_BEFORE_ENTER


class TypingManager:
    """Manages text typing with thread safety."""
    
    def __init__(self, auto_enter_callback, per_char_delay_callback=None):
        self.auto_enter_callback = auto_enter_callback
        # Callback untuk mengambil delay per karakter secara dinamis (dari UI)
        # Jika tidak diberikan, pakai default dari config.
        self.per_char_delay_callback = per_char_delay_callback or (lambda: TYPING_DELAY_PER_CHAR)
        self.typing_lock = threading.Lock()
        self.is_paused = False
    
    def send_text(self, text):
        """Send text with thread safety."""
        if self.is_paused:
            return
        if not text:
            return
        # Prevent multiple simultaneous calls (mencegah double-typing bug).
        if not self.typing_lock.acquire(blocking=False):
            return
        # Jalankan di thread terpisah supaya tidak nge-freeze GUI.
        threading.Thread(target=self._type_text_with_lock, args=(text,), daemon=True).start()
    
    def _type_text_with_lock(self, text):
        """Wrapper untuk _type_text yang handle lock release."""
        try:
            self._type_text(text)
        finally:
            # Pastikan lock selalu di-release meskipun ada error.
            self.typing_lock.release()
    
    def _type_text(self, text):
        """Type text character by character with delays."""
        # Delay sebelum mengetik supaya aplikasi tujuan siap menangkap input.
        time.sleep(TYPING_DELAY_INITIAL)
        
        # Pakai metode per karakter dengan delay yang bisa diatur user (manual)
        # supaya bisa disesuaikan antara kecepatan dan keakuratan.
        try:
            for char in text:
                keyboard.write(char)
                # Delay per karakter: diambil dari callback (bisa diubah dari UI)
                try:
                    delay = float(self.per_char_delay_callback() or 0)
                except Exception:
                    delay = TYPING_DELAY_PER_CHAR
                if delay < 0:
                    delay = 0
                time.sleep(delay)
        except Exception as e:
            # Fallback: kalau ada error, coba pakai keyboard.write() langsung
            try:
                keyboard.write(text)
            except Exception:
                pass
        
        # Tambah delay kecil setelah selesai mengetik sebelum tekan Enter (kalau perlu).
        if self.auto_enter_callback():
            time.sleep(TYPING_DELAY_BEFORE_ENTER)
            try:
                keyboard.press_and_release('enter')
            except Exception:
                pass


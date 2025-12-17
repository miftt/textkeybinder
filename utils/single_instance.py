"""
Single instance lock to prevent multiple instances of the application.
"""
import socket
import sys


_single_instance_socket = None


def acquire_single_instance_lock():
    """
    Cegah aplikasi dibuka dua kali.

    Kita pakai TCP port lokal sebagai "lock".
    Instance pertama berhasil bind ke port → lanjut jalan.
    Instance kedua gagal bind → artinya sudah ada yang jalan.
    """
    global _single_instance_socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Port arbitrer, kecil kemungkinan dipakai app lain.
        s.bind(("127.0.0.1", 49327))
        s.listen(1)
        _single_instance_socket = s
        return True
    except OSError:
        return False


def check_and_exit_if_running():
    """Check if another instance is running, show message and exit if so."""
    if not acquire_single_instance_lock():
        # Tampilkan pesan sederhana lalu keluar.
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                "TEXT MACRO KEYBINDER BY MIFUZI is already running.\n\n"
                "Please close the existing window before starting a new one.",
                "Already Running",
                0x10,  # MB_ICONERROR
            )
        except Exception:
            print("TEXT MACRO KEYBINDER BY MIFUZI is already running.")
        sys.exit(0)


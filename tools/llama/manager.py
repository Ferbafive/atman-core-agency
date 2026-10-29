from __future__ import annotations

import argparse
import gc
import logging
import os
import shutil
import subprocess
import sys
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from urllib.error import URLError
from urllib.request import urlopen
from uuid import uuid4

import psutil


LLAMA_ROOT = Path(os.environ.get("LLAMA_ROOT", r"C:\Llama"))
MEMORY_WARNING_PERCENT = 85.0
DEFAULT_GPU_LAYERS = "10"
CONTEXT_SIZE = "8192"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8080
QUARANTINE_NAME = "_quarantine"
PREFERRED_MODEL_FILENAME = "Qwen_Qwen3.5-4B-Q4_K_M.gguf"


def has_valid_pe_header(path: Path) -> bool:
    with path.open("rb") as binary:
        if binary.read(2) != b"MZ":
            return False
        binary.seek(0x3C)
        offset_data = binary.read(4)
        if len(offset_data) != 4:
            return False
        pe_offset = int.from_bytes(offset_data, byteorder="little")
        if pe_offset < 0x40 or pe_offset + 4 > path.stat().st_size:
            return False
        binary.seek(pe_offset)
        return binary.read(4) == b"PE\0\0"


def quarantine_invalid_ggml_dlls(root: Path) -> list[Path]:
    quarantine_folder = (
        datetime.now().strftime("%Y%m%d-%H%M%S") + f"-{uuid4().hex[:8]}"
    )
    quarantine_root = root / QUARANTINE_NAME / quarantine_folder
    moved: list[Path] = []

    for candidate in root.rglob("ggml*.dll"):
        if QUARANTINE_NAME in candidate.parts or candidate.is_symlink():
            continue
        if not candidate.is_file() or has_valid_pe_header(candidate):
            continue

        destination = quarantine_root / candidate.relative_to(root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(candidate), str(destination))
        moved.append(candidate)

    return moved


def find_server_executable(root: Path) -> Path:
    direct_path = root / "llama-server.exe"
    if direct_path.is_file():
        return direct_path

    matches = sorted(
        path
        for path in root.rglob("llama-server.exe")
        if QUARANTINE_NAME not in path.parts
    )
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(
            f"No se encontro llama-server.exe en {root}. "
            "Coloca el ejecutable ahi o deja solo una copia dentro de la carpeta."
        )
    raise RuntimeError(
        f"Se encontraron varias copias de llama-server.exe bajo {root}. "
        "Deja la version que quieras usar en la raiz C:\\Llama."
    )


def find_models(root: Path) -> list[Path]:
    return sorted(
        (
            path
            for path in root.rglob("*.gguf")
            if QUARANTINE_NAME not in path.parts and path.is_file()
        ),
        key=lambda path: str(path).casefold(),
    )


class LlamaManager:
    def __init__(self, window: tk.Tk, auto_start: bool = False) -> None:
        self.window = window
        self.server_process: subprocess.Popen[bytes] | None = None
        self.watchdog_process: subprocess.Popen[bytes] | None = None
        self.watchdog_error: str | None = None
        self.last_warning_active = False
        self.log_path = LLAMA_ROOT / "logs" / "llama-server.log"
        self.server_path: Path | None = None
        self.model_paths: list[Path] = []

        self._configure_logging()
        self._build_interface()
        self._load_installation()
        self._start_watchdog()
        self.window.protocol("WM_DELETE_WINDOW", self._close)
        self.window.after(1000, self._refresh_status)
        if auto_start and self.server_path is not None and self.model_var.get():
            self.window.after(250, self._start_server)

    def _configure_logging(self) -> None:
        log_directory = LLAMA_ROOT / "logs"
        log_directory.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=log_directory / "manager.log",
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
            encoding="utf-8",
        )

    def _build_interface(self) -> None:
        self.window.title("Llama.cpp - Panel local")
        self.window.geometry("620x310")
        self.window.minsize(560, 280)

        frame = ttk.Frame(self.window, padding=16)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Instalacion:").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text=str(LLAMA_ROOT)).grid(
            row=0, column=1, columnspan=2, sticky="w", padx=(10, 0)
        )

        ttk.Label(frame, text="Modelo GGUF:").grid(
            row=1, column=0, sticky="w", pady=(14, 0)
        )
        self.model_var = tk.StringVar()
        self.model_picker = ttk.Combobox(
            frame, textvariable=self.model_var, state="readonly", width=56
        )
        self.model_picker.grid(
            row=1, column=1, columnspan=2, sticky="ew", padx=(10, 0), pady=(14, 0)
        )

        ttk.Label(frame, text="Capas GPU:").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )
        self.gpu_layers_var = tk.StringVar(value=DEFAULT_GPU_LAYERS)
        ttk.Entry(frame, textvariable=self.gpu_layers_var, width=8).grid(
            row=2, column=1, sticky="w", padx=(10, 0), pady=(10, 0)
        )
        ttk.Label(
            frame,
            text=f"Contexto: {CONTEXT_SIZE} | Puerto local: {SERVER_PORT}",
        ).grid(row=2, column=2, sticky="e", pady=(10, 0))

        self.server_status_var = tk.StringVar(value="Servidor: comprobando...")
        self.memory_status_var = tk.StringVar(value="Memoria: comprobando...")
        ttk.Label(frame, textvariable=self.server_status_var).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(18, 0)
        )
        ttk.Label(frame, textvariable=self.memory_status_var).grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(6, 0)
        )

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(20, 0))
        self.start_button = ttk.Button(
            buttons, text="Iniciar servidor", command=self._start_server
        )
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(
            buttons, text="Detener servidor", command=self._stop_server, state="disabled"
        )
        self.stop_button.pack(side="left", padx=(8, 0))

        ttk.Label(
            frame,
            text="El umbral de RAM solo genera un aviso; detén el servidor desde este panel si es necesario.",
            wraplength=580,
        ).grid(row=6, column=0, columnspan=3, sticky="w", pady=(16, 0))

    def _load_installation(self) -> None:
        if not LLAMA_ROOT.is_dir():
            self._show_startup_error(f"No existe la carpeta {LLAMA_ROOT}.")
            return

        try:
            self.server_path = find_server_executable(LLAMA_ROOT)
            self.model_paths = find_models(LLAMA_ROOT)
        except (OSError, RuntimeError) as error:
            logging.exception("No se pudo validar la instalacion de llama.cpp")
            self.server_status_var.set(f"Servidor: error de configuracion ({error})")
            self.start_button.configure(state="disabled")
            return

        self.model_picker["values"] = [str(path) for path in self.model_paths]
        preferred_model = next(
            (
                path
                for path in self.model_paths
                if path.name.casefold() == PREFERRED_MODEL_FILENAME.casefold()
            ),
            None,
        )
        if preferred_model is not None:
            self.model_var.set(str(preferred_model))
        elif len(self.model_paths) == 1:
            self.model_var.set(str(self.model_paths[0]))
        elif not self.model_paths:
            self.server_status_var.set("Servidor: no se encontraron modelos .gguf")
            self.start_button.configure(state="disabled")
            return

        self.server_status_var.set(f"Servidor: listo ({self.server_path})")

    def _start_watchdog(self) -> None:
        watchdog_path = Path(__file__).with_name("ram_watchdog.py")
        command = [
            sys.executable,
            str(watchdog_path),
            "--parent-pid",
            str(os.getpid()),
        ]
        try:
            self.watchdog_process = subprocess.Popen(
                command,
                cwd=LLAMA_ROOT,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError as error:
            logging.exception("No se pudo iniciar el monitor de memoria")
            self.watchdog_error = str(error)

    def _show_startup_error(self, message: str) -> None:
        self.server_status_var.set(f"Servidor: {message}")
        self.start_button.configure(state="disabled")
        messagebox.showerror("Configuracion de Llama.cpp", message, parent=self.window)

    def _start_server(self) -> None:
        if self.server_process is not None and self.server_process.poll() is None:
            return
        if self.server_path is None:
            messagebox.showerror(
                "No se puede iniciar", "No se encontro llama-server.exe.", parent=self.window
            )
            return

        selected_model = self.model_var.get()
        model_path = Path(selected_model)
        if not selected_model or not model_path.is_file() or model_path.suffix.lower() != ".gguf":
            messagebox.showerror(
                "Selecciona un modelo",
                "Selecciona un archivo .gguf valido antes de iniciar.",
                parent=self.window,
            )
            return

        gpu_layers_text = self.gpu_layers_var.get().strip()
        if not gpu_layers_text.isdecimal():
            messagebox.showerror(
                "Capas GPU no validas",
                "Indica un numero entero de capas GPU (por ejemplo, 10).",
                parent=self.window,
            )
            return

        try:
            moved = quarantine_invalid_ggml_dlls(LLAMA_ROOT)
        except OSError as error:
            logging.exception("Fallo al apartar una DLL ggml con cabecera invalida")
            messagebox.showerror(
                "Error validando DLL",
                f"No se pudo apartar una DLL ggml invalida:\n{error}",
                parent=self.window,
            )
            return

        if moved:
            logging.warning("DLL ggml apartadas por cabecera PE invalida: %s", moved)
            messagebox.showwarning(
                "DLL invalidas apartadas",
                f"Se movieron {len(moved)} DLL ggml con cabecera PE invalida a "
                f"{LLAMA_ROOT / QUARANTINE_NAME}. No se borraron modelos ni DLL validas.",
                parent=self.window,
            )

        command = [
            str(self.server_path),
            "--model",
            str(model_path),
            "--ctx-size",
            CONTEXT_SIZE,
            "--n-gpu-layers",
            gpu_layers_text,
            "--host",
            SERVER_HOST,
            "--port",
            str(SERVER_PORT),
        ]
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self.log_path.open("ab") as server_log:
                self.server_process = subprocess.Popen(
                    command,
                    cwd=self.server_path.parent,
                    stdout=server_log,
                    stderr=subprocess.STDOUT,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
        except OSError as error:
            logging.exception("No se pudo iniciar llama-server.exe")
            messagebox.showerror(
                "Error al iniciar el servidor",
                f"No se pudo iniciar llama-server.exe:\n{error}\n\n"
                f"Consulta el registro: {self.log_path}",
                parent=self.window,
            )
            return

        logging.info("Servidor iniciado: %s", command)
        self.server_status_var.set(
            f"Servidor: iniciando (PID {self.server_process.pid}); registro: {self.log_path}"
        )
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def _stop_server(self) -> None:
        process = self.server_process
        if process is None or process.poll() is not None:
            self.server_process = None
            self.server_status_var.set("Servidor: detenido")
            self.stop_button.configure(state="disabled")
            self.start_button.configure(state="normal")
            return

        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

        logging.info("Servidor detenido por el usuario")
        self.server_process = None
        self.server_status_var.set("Servidor: detenido")
        self.stop_button.configure(state="disabled")
        self.start_button.configure(state="normal")

    def _refresh_status(self) -> None:
        memory = psutil.virtual_memory()
        used_gb = (memory.total - memory.available) / (1024**3)
        total_gb = memory.total / (1024**3)
        over_threshold = memory.percent >= MEMORY_WARNING_PERCENT
        if over_threshold and not self.last_warning_active:
            collected = gc.collect()
            logging.warning(
                "RAM del sistema sobre %.0f%% (%.1f%%); GC local libero %d objetos",
                MEMORY_WARNING_PERCENT,
                memory.percent,
                collected,
            )
        if self.watchdog_error is not None:
            self.memory_status_var.set(
                f"Monitor RAM no disponible: {self.watchdog_error} | "
                f"Uso de RAM: {memory.percent:.1f}%"
            )
        elif over_threshold:
            self.memory_status_var.set(
                f"AVISO: RAM {memory.percent:.1f}% ({used_gb:.1f}/{total_gb:.1f} GB) - "
                "GC del monitor; no libera RAM del servidor."
            )
        else:
            self.memory_status_var.set(
                f"RAM del sistema: {memory.percent:.1f}% ({used_gb:.1f}/{total_gb:.1f} GB)"
            )
        self.last_warning_active = over_threshold

        process = self.server_process
        if process is not None:
            return_code = process.poll()
            if return_code is None:
                self.server_status_var.set(
                    f"Servidor: activo (PID {process.pid}) | "
                    f"http://{SERVER_HOST}:{SERVER_PORT}"
                )
            else:
                self.server_status_var.set(
                    f"Servidor: finalizado (codigo {return_code}); "
                    f"registro: {self.log_path}"
                )
                self.server_process = None
                self.start_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
        elif self.server_path is not None:
            self.server_status_var.set(f"Servidor: detenido | {self.server_path}")

        if process is not None and process.poll() is None and int(time.time()) % 5 == 0:
            try:
                with urlopen(
                    f"http://{SERVER_HOST}:{SERVER_PORT}/health", timeout=0.5
                ) as response:
                    if response.status == 200:
                        self.server_status_var.set(
                            f"Servidor: saludable | http://{SERVER_HOST}:{SERVER_PORT}"
                        )
            except (OSError, URLError, TimeoutError):
                pass

        self.window.after(1000, self._refresh_status)

    def _close(self) -> None:
        process = self.server_process
        if process is not None and process.poll() is None:
            should_stop = messagebox.askyesno(
                "Servidor activo",
                "El servidor sigue activo. Quieres detenerlo y cerrar el panel?",
                parent=self.window,
            )
            if not should_stop:
                return
            self._stop_server()
        watchdog = self.watchdog_process
        if watchdog is not None and watchdog.poll() is None:
            watchdog.terminate()
            try:
                watchdog.wait(timeout=5)
            except subprocess.TimeoutExpired:
                watchdog.kill()
                watchdog.wait(timeout=5)
        self.window.destroy()


def main() -> None:
    parser = argparse.ArgumentParser(description="Panel de control local de llama.cpp.")
    parser.add_argument(
        "--auto-start",
        action="store_true",
        help="Inicia el servidor automaticamente al abrir el panel.",
    )
    arguments = parser.parse_args()
    window = tk.Tk()
    LlamaManager(window, auto_start=arguments.auto_start)
    window.mainloop()


if __name__ == "__main__":
    main()

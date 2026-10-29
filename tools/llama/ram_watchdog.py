from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

import psutil


LLAMA_ROOT = Path(r"C:\Llama")
THRESHOLD_PERCENT = 85.0
CHECK_INTERVAL_SECONDS = 30


def parent_is_running(parent_pid: int) -> bool:
    try:
        return psutil.Process(parent_pid).is_running()
    except psutil.NoSuchProcess:
        return False


def monitor_ram(parent_pid: int) -> None:
    log_directory = LLAMA_ROOT / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_directory / "ram-watchdog.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )
    logging.info("Monitor iniciado; umbral %.0f%%", THRESHOLD_PERCENT)
    was_over_threshold = False

    while parent_is_running(parent_pid):
        memory = psutil.virtual_memory()
        over_threshold = memory.percent >= THRESHOLD_PERCENT
        if over_threshold and not was_over_threshold:
            logging.warning(
                "Uso de RAM %.1f%%; el monitor no limpia la cache ni libera memoria de otros procesos",
                memory.percent,
            )
        elif was_over_threshold and not over_threshold:
            logging.info("Uso de RAM normalizado: %.1f%%", memory.percent)
        was_over_threshold = over_threshold
        time.sleep(CHECK_INTERVAL_SECONDS)

    logging.info("Monitor detenido: el panel principal ya no esta activo")


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor ligero de memoria RAM.")
    parser.add_argument("--parent-pid", required=True, type=int)
    arguments = parser.parse_args()
    monitor_ram(arguments.parent_pid)


if __name__ == "__main__":
    main()

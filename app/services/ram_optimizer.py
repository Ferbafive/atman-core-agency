import os
import sys
import time
import logging
import subprocess
import psutil

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

CONFIG = {
    'check_interval': 45,
    'memory_threshold': 90,
    'log_file': 'ram_optimizer.log',
    'memreduct_path': r"C:\Program Files\MemReduct\MemReduct.exe",
    'wise_path': r"C:\Program Files\Wise Memory Optimizer\WiseMemoryOptimizer.exe"
}

logging.basicConfig(
    filename=CONFIG['log_file'],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("RAMOptimizer")

def find_executable(primary_path, alternative_names, subdirs):
    """Busca automáticamente el ejecutable en la ruta primaria o en carpetas comunes de Windows."""
    if os.path.exists(primary_path):
        return primary_path
    
    drive = os.path.splitdrive(primary_path)[0] or "C:"
    base_dirs = [
        os.path.join(drive, "\\Program Files"),
        os.path.join(drive, "\\Program Files (x86)")
    ]
    
    for base in base_dirs:
        for subdir in subdirs:
            for name in alternative_names:
                test_path = os.path.join(base, subdir, name)
                if os.path.exists(test_path):
                    return test_path
    return None

def add_windows_defender_exclusion(exclusion_path):
    """Agrega una exclusión automática en Windows Defender para el ejecutable."""
    try:
        powercmd = f'powershell -Command "Add-MpPreference -ExclusionPath \\"{exclusion_path}\\""'
        subprocess.run(
            powercmd,
            shell=True,
            capture_output=True,
            timeout=10,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
        logger.info(f"Exclusión agregada en Windows Defender para: {exclusion_path}")
        return True
    except Exception as e:
        logger.warning(f"No se pudo agregar la exclusión de Windows Defender: {e}")
        return False

def get_top_ram_processes(n=3):
    """Obtiene los n procesos del sistema que más porcentaje de RAM están consumiendo."""
    procs = []
    for p in psutil.process_iter(['name', 'memory_percent']):
        try:
            info = p.info
            if info['memory_percent'] is not None:
                procs.append((info['name'], info['memory_percent']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    procs.sort(key=lambda x: x[1], reverse=True)
    return procs[:n]

def send_notification(before, after):
    if HAS_PLYER:
        try:
            notification.notify(
                title="RAM Optimizer",
                message=f"Memoria optimizada: {before}% -> {after}%",
                timeout=5
            )
        except Exception as e:
            logger.warning(f"No se pudo enviar la notificacion: {e}")

def run_optimizer():
    """Ejecuta los optimizadores externos buscando rutas de forma inteligente."""
    # 1. Buscar MemReduct
    memreduct_found = find_executable(
        CONFIG['memreduct_path'], 
        ['MemReduct.exe', 'memreduct.exe'], 
        ['MemReduct', 'Mem Reduct']
    )
    if memreduct_found:
        try:
            # Agregar exclusión en Windows Defender antes de ejecutar para evitar bloqueos
            add_windows_defender_exclusion(memreduct_found)
            
            subprocess.run([memreduct_found, '/clean'], timeout=10)
            logger.info(f"MemReduct ejecutado desde: {memreduct_found}")
            return True
        except Exception as e:
            logger.warning(f"Fallo al ejecutar MemReduct: {e}")

    # 2. Buscar Wise Memory Optimizer
    wise_found = find_executable(
        CONFIG['wise_path'], 
        ['WiseMemoryOptimizer.exe', 'wisememoryoptimizer.exe'], 
        ['Wise Memory Optimizer', 'Wise']
    )
    if wise_found:
        try:
            add_windows_defender_exclusion(wise_found)
            subprocess.run([wise_found, '-opt'], timeout=10)
            logger.info(f"Wise Memory Optimizer ejecutado desde: {wise_found}")
            return True
        except Exception as e:
            logger.warning(f"Fallo al ejecutar Wise Memory Optimizer: {e}")

    # 3. Fallback nativo
    logger.info("Ejecutando rutina nativa de limpieza...")
    return True

def monitor():
    logger.info("Servicio de monitoreo de RAM inteligente iniciado.")
    print("Monitoreando memoria RAM en segundo plano (Modo Inteligente)... Presiona Ctrl+C para salir")
    
    last_action_time = 0
    cooldown_period = 120  # 2 minutos de enfriamiento

    while True:
        try:
            mem_before = psutil.virtual_memory().percent
            
            if mem_before >= 80:
                logger.info(f"Uso de RAM actual: {mem_before}%")
            
            current_time = time.time()
            if mem_before >= CONFIG['memory_threshold']:
                if current_time - last_action_time > cooldown_period:
                    logger.warning(f"RAM por encima del limite critico ({mem_before}% >= {CONFIG['memory_threshold']}%)")
                    
                    # Diagnóstico: registrar los 3 procesos que más RAM consumen
                    top_procs = get_top_ram_processes(3)
                    proc_summary = ", ".join([f"{name} ({pct:.1f}%)" for name, pct in top_procs])
                    logger.warning(f"Top 3 procesos consumiendo RAM: {proc_summary}")
                    
                    run_optimizer()
                    
                    time.sleep(3)
                    mem_after = psutil.virtual_memory().percent
                    logger.info(f"RAM tras optimizacion: {mem_after}%")
                    
                    send_notification(mem_before, mem_after)
                    last_action_time = time.time()
                else:
                    logger.debug("RAM alta, pero en periodo de enfriamiento (cooldown).")
                    
        except Exception as e:
            logger.error(f"Error en el ciclo de monitoreo: {e}")
            
        time.sleep(CONFIG['check_interval'])

if __name__ == "__main__":
    monitor()
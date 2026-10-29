import time
import logging
import ctypes
import psutil

# Configurar el sistema de registros (Logs)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ram_optimizer.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

CRITICAL_THRESHOLD = 90.0  # Límite crítico de RAM en porcentaje
CHECK_INTERVAL = 45        # Segundos entre cada comprobación

def clean_memory_native():
    """Ejecuta la rutina nativa de limpieza de memoria en Windows."""
    try:
        logging.info("Ejecutando rutina nativa de limpieza de memoria...")
        
        # Limpiar el conjunto de trabajo de todos los procesos accesibles (Windows)
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Omitir procesos críticos del sistema si es necesario
                p = psutil.Process(proc.info['pid'])
                # Llamada nativa de Windows para liberar memoria en caché del proceso
                ctypes.windll.psapi.EmptyWorkingSet(p._handle)
            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
                pass
                
        logging.info("Rutina nativa de limpieza finalizada con éxito.")
    except Exception as e:
        logging.error(f"Error durante la limpieza nativa: {e}")

def monitor_ram():
    logging.info("Servicio de monitoreo de RAM inteligente iniciado.")
    
    while True:
        try:
            # Obtener el uso actual de la memoria RAM
            mem = psutil.virtual_memory()
            current_usage = mem.percent
            
            logging.info(f"Uso de RAM actual: {current_usage}%")
            
            # Comprobar si supera el límite crítico
            if current_usage >= CRITICAL_THRESHOLD:
                logging.warning(f"RAM por encima del limite critico! ({current_usage}% >= {CRITICAL_THRESHOLD}%)")
                
                # Obtener el Top 3 de procesos que más consumen
                processes = []
                for p in psutil.process_iter(['name', 'memory_percent']):
                    try:
                        processes.append((p.info['name'], p.info['memory_percent'] or 0.0))
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                processes.sort(key=lambda x: x[1], reverse=True)
                top_3 = processes[:3]
                top_3_str = ", ".join([f"{name} ({pct:.1f}%)" for name, pct in top_3])
                logging.warning(f"Top 3 procesos consumiendo RAM: {top_3_str}")
                
                # Ejecutar limpieza nativa directamente
                clean_memory_native()
                
                # Esperar a que la memoria se estabilice tras la limpieza
                time.sleep(3)
                new_usage = psutil.virtual_memory().percent
                logging.info(f"RAM tras optimizacion: {new_usage}%")
                
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            logging.error(f"Error en el ciclo de monitoreo: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor_ram()
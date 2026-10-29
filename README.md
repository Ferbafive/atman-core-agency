# RAM Optimizer para Windows

Script automático que monitorea el consumo de memoria RAM y ejecuta herramientas de optimización como **MemReduct** o **Wise Memory Optimizer** en segundo plano cuando se supera un umbral de uso.

## Requisitos

Instala las dependencias necesarias ejecutando en la terminal:

```bash
pip install psutil plyer
```

## Lanzador local de llama.cpp

En Windows, ejecuta `setup_total.bat` desde la raiz del proyecto. El script
reutiliza `.venv` si funciona; si no, crea `.llama-venv`. Si no hay Python
disponible, intenta instalar Python 3.12 para el usuario con `winget`; despues
instala `psutil` sin modificar la instalacion global. Necesita conexion a
Internet para instalar Python o `psutil` cuando falten.

El lanzador comprueba `C:\Llama`, busca el archivo exacto
`Qwen_Qwen3.5-4B-Q4_K_M.gguf` en Descargas y lo mueve a `C:\Llama` si aun no
esta alli. Si encuentra varias copias, mueve la mas reciente. Tambien requiere
`llama-server.exe` bajo `C:\Llama`; el script no descarga ni instala llama.cpp.
Se necesita permiso de escritura en `C:\Llama`. No solicita elevacion UAC ni
sobrescribe un modelo que ya exista.

Al completar las comprobaciones, abre el panel, inicia en segundo plano un
monitor de RAM ligado a la vida del panel y arranca el servidor automaticamente
con el modelo indicado, 10 capas GPU, contexto 2048 y escucha en
`127.0.0.1:8080`. El panel permite detener el servidor. La compilacion de
`llama-server.exe` debe tener CUDA para usar la GPU; el argumento de capas no
añade soporte CUDA a una compilacion que no lo incluya.

El panel requiere Python con Tkinter y `psutil`. Para instalar manualmente la
dependencia en `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Al iniciar, solo aparta a `C:\Llama\_quarantine` las DLL `ggml*.dll` que no
tengan cabeceras PE validas; no borra archivos y no modifica modelos. Esta
comprobacion no detecta DLL validas pero incompatibles con la version del
ejecutable, por lo que conviene instalar juntos el servidor y sus DLL de la
misma compilacion.

El monitor registra avisos al superar el 85% de RAM en
`C:\Llama\logs\ram-watchdog.log`. No vacia la cache de Windows ni puede liberar
RAM del servidor; si el uso sigue alto, usa el boton para detener el servidor.
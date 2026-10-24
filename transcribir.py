import os
import subprocess
import whisper

ruta_original = r"C:\Users\Fernando\Desktop\agencia.mp3"
ruta_corte = r"C:\Users\Fernando\Desktop\agencia_corte.mp3"
ruta_salida = r"C:\Users\Fernando\Desktop\transcripcion.txt"

# 1 hora y 36 minutos en segundos (3600 + 2160 = 5760)
duracion_segundos = 5760

if not os.path.exists(ruta_original):
    print(f"❌ No se encuentra el archivo: {ruta_original}")
else:
    try:
        print("Recortando la primera hora y 36 minutos del audio...")
        # Usamos ffmpeg para cortar el audio rápidamente sin perder calidad
        comando = [
            "ffmpeg",
            "-y",
            "-i",
            ruta_original,
            "-t",
            str(duracion_segundos),
            "-c",
            "copy",
            ruta_corte,
        ]
        subprocess.run(comando, check=True)

        print("Cargando el modelo de Whisper...")
        model = whisper.load_model("base")

        print(
            "Transcribiendo el fragmento recortado... (esto tardará unos minutos)"
        )
        result = model.transcribe(ruta_corte, language="es")

        print(f"Guardando el archivo de texto en: {ruta_salida}")
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(result["text"])

        print(
            "¡Transcripción completada con éxito! Ya tienes el .txt en el escritorio."
        )

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
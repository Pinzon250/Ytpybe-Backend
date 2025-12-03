from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp
import os
import uvicorn
import uuid

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/descargar/")
def descargar(url: str = Query(...), formato: str = Query("video")):
    unique_id = str(uuid.uuid4())  

    filename_template = f"{DOWNLOAD_DIR}/{unique_id}.%(ext)s"
    opciones = {
        'outtmpl': filename_template,
        'quiet': True,
    }

    if formato == "audio":
        opciones.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        opciones.update({'format': 'bestvideo+bestaudio/best'})

    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url)
            title = ydl.prepare_filename(info)
        
        # Buscar el archivo generado
        base = os.path.splitext(title)[0]
        for ext in ['mp4', 'webm', 'mkv', 'mp3']:
            filepath = f"{base}.{ext}"
            if os.path.exists(filepath):
                return FileResponse(filepath, filename=os.path.basename(filepath), media_type='application/octet-stream')
        
        return {"error": "Archivo no encontrado"}
    except Exception as e:
        return {"error": str(e)}
    
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

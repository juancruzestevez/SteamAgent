import logging
import tempfile
import asyncio
import numpy as np
import sounddevice as sd
import whisper
import edge_tts
import pygame
from pynput import keyboard
from src.agent.brain import SteamAgent
import os

logger = logging.getLogger(__name__)

class SteamVoiceBot:
    def __init__(self):
        self.agent = SteamAgent()
        print("⏳ Cargando el modelo de reconocimiento de voz (Whisper Base)... esto tomará unos segundos.")
        # Usamos el modelo "base" que es súper rápido y pesa muy poco.
        self.whisper_model = whisper.load_model("base")
        self.samplerate = 16000
        self.is_recording = False
        self.audio_data = []
        pygame.mixer.init()
        
    def _audio_callback(self, indata, frames, time, status):
        """Función que recibe el audio del micrófono de forma continua."""
        if status:
            logger.warning(status)
        if self.is_recording:
            self.audio_data.append(indata.copy())
            
    def on_press(self, key):
        """Se activa al presionar una tecla."""
        if key == keyboard.Key.f9 and not self.is_recording:
            print("\n🔴 Grabando... (Habla ahora y suelta F9 cuando termines)")
            self.is_recording = True
            self.audio_data = []
            
    def on_release(self, key):
        """Se activa al soltar una tecla."""
        if key == keyboard.Key.f9 and self.is_recording:
            print("⏹️ Grabación terminada. Procesando voz...")
            self.is_recording = False
            # Ejecutar el procesamiento asíncrono
            asyncio.run(self.process_audio())
            
    async def process_audio(self):
        if not self.audio_data:
            return
            
        # Unimos los fragmentos de audio grabados y los preparamos para Whisper
        audio_np = np.concatenate(self.audio_data, axis=0)
        audio_np = audio_np.flatten()
        
        print("🧠 Entendiendo lo que dijiste...")
        # fp16=False es necesario para evitar warnings en CPU o GPUs sin soporte nativo FP16
        result = self.whisper_model.transcribe(audio_np, fp16=False, language="es")
        text = result["text"].strip()
        print(f"🗣️ Tú: {text}")
        
        if not text:
            print("🤔 No te escuché bien. Intenta apretar F9 de nuevo.")
            return
            
        print("🤖 Agente pensando...")
        # El cerebro de SteamAgent procesa tu texto (puede usar RAG, buscar en Steam, etc)
        response = self.agent.chat(text)
        print(f"🤖 Agente: {response}")
        
        print("🔊 Generando voz de respuesta...")
        # Generar audio usando la voz de Edge (es-MX-JorgeNeural o es-ES-AlvaroNeural)
        communicate = edge_tts.Communicate(response, "es-MX-JorgeNeural")
        
        temp_audio_name = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio_name = temp_audio.name
                
            await communicate.save(temp_audio_name)
            
            # Reproducir el audio resultante por los auriculares
            pygame.mixer.music.load(temp_audio_name)
            pygame.mixer.music.play()
            
            # Esperar a que el audio termine de reproducirse
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
                
        finally:
            # Limpiar archivo temporal
            if temp_audio_name and os.path.exists(temp_audio_name):
                # Pequeño retardo para que PyGame suelte el archivo
                pygame.mixer.music.unload()
                os.remove(temp_audio_name)
                
        print("\n✅ Listo. Mantén [F9] presionado cuando quieras hablar de nuevo.")
        
    def start(self):
        print("🎙️ Iniciando Asistente de Voz Local...")
        
        # Abrimos el micrófono de manera continua
        with sd.InputStream(samplerate=self.samplerate, channels=1, dtype='float32', callback=self._audio_callback):
            print("✅ ¡Sistema encendido! Minimiza esta ventana.")
            print("   👉 Mantén presionada la tecla [F9] para hablarle al Agente.")
            
            # Ponemos a escuchar el teclado globalmente
            with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
                listener.join()

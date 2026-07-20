<div align="center">
  <h1>🎮 SteamAgent</h1>
  <p>Tu asistente personal de videojuegos. Juega sin interrupciones, descubre nuevas joyas en tu biblioteca y nunca más te quedes trabado.</p>
</div>

---

## 🚀 ¿Por qué SteamAgent?

Todos hemos estado ahí: estás inmerso en una partida increíble, la tensión está al máximo y de repente... te trabas. Tienes que pausar el juego, minimizar, abrir el navegador, esquivar spoilers en foros y buscar una guía para saber cómo avanzar. O tal vez miras tu biblioteca de 300 juegos y sientes que "no tienes nada para jugar".

**SteamAgent nació para eliminar esas fricciones.**

Es mucho más que un simple chatbot; es tu compañero de aventuras. SteamAgent se conecta directamente a tu cuenta y entiende tu contexto. Ya sea que necesites ayuda táctica en tiempo real, descubrir qué juego de tu inmensa biblioteca encaja con tu humor actual, o simplemente quieras saber qué logros te faltan para platinar tu juego favorito, SteamAgent está ahí para ti.

---

## ✨ Lo que SteamAgent puede hacer por ti

* 🎯 **Asistencia Contextual (¡Próximamente!)**: SteamAgent sabe a qué estás jugando. Pídele ayuda y te dará consejos específicos sin que tengas que explicarle dónde estás ni hacer tab-out.
* 📚 **Curador de Biblioteca Personal**: ¿No sabes qué jugar? SteamAgent analiza tus gustos y el tiempo que le has dedicado a tus juegos para recomendarte joyas ocultas que ya posees.
* 🏆 **Cazador de Logros**: Pregúntale qué te falta para completar tu juego y te armará una guía rápida con tus próximos objetivos.
* 🌐 **Buscador en Tiempo Real**: Si necesitas guías, lore de una saga o la última actualización de un parche, el agente navega por internet y te resume lo más importante en segundos.

---

## 🚀 Cómo empezar a usarlo

Para llevar a SteamAgent a tu computadora, solo necesitas seguir estos sencillos pasos:

1. **Descarga la app:**
   ```bash
   git clone git@github.com:juancruzestevez/SteamAgent.git
   cd SteamAgent
   ```

2. **Prepara el entorno:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Conecta tus cuentas:**
   Copia el archivo base y agrega tus claves:
   ```bash
   cp .env.example .env
   ```
   Abre el archivo `.env` y pon tu `STEAM_API_KEY` (tu pase a los servidores de Steam), tu `STEAM_USER_ID` y elige qué "cerebro" quieres que use el agente añadiendo una API Key de OpenAI (ChatGPT), Anthropic (Claude), Groq o Google Gemini.

4. **¡Arranca!**
   ```bash
   python -m src.main
   ```

---

## 🤓 Para Desarrolladores y Entusiastas

Debajo de esta interfaz amigable, SteamAgent es un proyecto robusto diseñado con las mejores prácticas de la Ingeniería de IA actual:

* **Arquitectura de Agente ReAct**: Construido sobre LangChain, el modelo razona antes de actuar, eligiendo dinámicamente qué herramientas ejecutar.
* **Agnóstico al LLM**: Soporta de forma nativa OpenAI, Anthropic, Gemini y Groq/Llama3 mediante un patrón Factory.
* **Optimización Extrema**: Utiliza caché en SQLite con un patrón *Decorator* para minimizar las llamadas a la API de Steam y acelerar respuestas.
* **Memoria Persistente**: Ventana de contexto gestionada automáticamente para mantener conversaciones fluidas sin romper los límites de tokens.
* **Seguridad y Tipado**: Configuración centralizada validada en tiempo real mediante Pydantic.

---

<div align="center">
  <p>Construido con pasión por los videojuegos y la IA por <b>Juan Cruz Estevez</b>.</p>
</div>

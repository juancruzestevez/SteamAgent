<div align="center">
  <h1>🎮 SteamAgent AI</h1>
  <p>Un Asistente Inteligente Conversacional para tu Biblioteca de Steam, potenciado por LangChain y Arquitectura ReAct.</p>
</div>

---

## 📖 Sobre el Proyecto

**SteamAgent** es una aplicación de Inteligencia Artificial diseñada para actuar como un compañero y asistente personal mientras juegas o exploras tu biblioteca de Steam. 

A diferencia de un chatbot tradicional, SteamAgent es un **Agente ReAct (Reasoning + Acting)**. Esto significa que puede "pensar" sobre tu pregunta, decidir qué herramienta usar (consultar la API de Steam, buscar guías en internet), ejecutar la acción, analizar los resultados, y finalmente entregarte una respuesta útil y contextualizada.

Este proyecto fue concebido como un entorno de aprendizaje práctico para la Ingeniería de IA, explorando conceptos de orquestación de LLMs, gestión de memoria conversacional y desarrollo modular en Python.

---

## ✨ Características Principales

* 🧠 **Arquitectura ReAct**: Razonamiento y ejecución dinámica de herramientas mediante LangChain.
* 🔄 **Soporte Multi-Modelo (LLM)**: Arquitectura flexible que permite intercambiar motores de IA (Groq/Llama3, Google Gemini, OpenAI, Anthropic Claude) simplemente cambiando una variable de entorno.
* 🚀 **Caché Local Inteligente**: Integración de una base de datos SQLite con un patrón *Decorator* para almacenar temporalmente respuestas de la API de Steam, optimizando tiempos de respuesta y reduciendo el consumo de cuota.
* 🌐 **Búsqueda Web Integrada**: Capacidad de buscar guías, lore y noticias de juegos en tiempo real utilizando DuckDuckGo.
* 💾 **Memoria Conversacional**: Implementación de una memoria de ventana deslizante que permite al agente recordar el contexto de la charla sin desbordar el límite de tokens.
* 🛠️ **Configuración Centralizada (Pydantic)**: Validación estricta y tipado fuerte para todas las variables de entorno, implementando una filosofía de "falla rápida" (fail-fast).
* 📝 **Logging Profesional**: Trazabilidad completa de las acciones del agente para facilitar el debugging y monitoreo.

---

## 🛠️ Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Orquestación IA:** LangChain
* **Modelos IA:** Groq (Llama-3), Google Generative AI (Gemini), OpenAI, Anthropic
* **Validación de Datos:** Pydantic & Pydantic-Settings
* **Caché / Base de Datos:** SQLite3 (Nativo)
* **Búsqueda Web:** DuckDuckGo Search (DDGS)
* **Peticiones HTTP:** Requests

---

## 🚀 Instalación y Configuración

Sigue estos pasos para ejecutar el agente en tu entorno local.

### 1. Clonar el repositorio
```bash
git clone git@github.com:juancruzestevez/SteamAgent.git
cd SteamAgent
```

### 2. Crear y activar un entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate
```

### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar las Variables de Entorno
Copia el archivo de ejemplo y configúralo con tus claves API:
```bash
cp .env.example .env
```

Abre el archivo `.env` y completa al menos las siguientes variables obligatorias:
* `STEAM_API_KEY`: Tu clave de la API de Steam ([Obtener aquí](https://steamcommunity.com/dev/apikey))
* `STEAM_USER_ID`: Tu ID público de Steam (Formato de 17 dígitos)
* Y al menos **una** clave para un proveedor LLM (ej: `GROQ_API_KEY`, `OPENAI_API_KEY`, etc.)

*Nota: Por defecto, la aplicación intentará usar los proveedores en el orden: Groq -> Gemini -> OpenAI -> Anthropic. Puedes forzar uno específico cambiando `LLM_PROVIDER=openai`.*

---

## 🕹️ Uso

Para iniciar el agente conversacional en tu terminal, simplemente ejecuta:

```bash
python -m src.main
```

**Ejemplos de preguntas que puedes hacerle:**
* *"¿Cuáles son mis 3 juegos más jugados?"*
* *"¿Cuántas horas tengo en el Counter-Strike 2?"*
* *"Busca en internet una guía para desbloquear el logro 'Short Fuse' en mi último juego"*

---

## 🗺️ Roadmap de Desarrollo

- [x] **Fase 0:** Refactorización, Arquitectura Modular, Soporte Multi-LLM y Caché.
- [ ] **Fase 1:** Asistente Contextual (Detección de juego activo, resúmenes de YouTube).
- [ ] **Fase 2:** Curador de Biblioteca (Recomendaciones inteligentes y ofertas).
- [ ] **Fase 3:** Sistema RAG (Generación Aumentada por Recuperación) con base de datos vectorial para Wikis.
- [ ] **Fase 4:** Interfaz de Voz en Discord (STT/TTS).
- [ ] **Fase 5:** Integración de Visión por Computadora (análisis de capturas de pantalla de la partida).

---

## 👨‍💻 Autor

**Juan Cruz Estevez** 
* Proyecto de investigación y aprendizaje en Ingeniería de Inteligencia Artificial.

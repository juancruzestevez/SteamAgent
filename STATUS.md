# 🎮 Steam Agent - Status & Roadmap de Aprendizaje

Este archivo sirve como bitácora de progreso y guía de estudio para el desarrollo del Agente de Steam con IA.

## 🎯 Objetivo Educativo
Aprender a desarrollar aplicaciones de IA utilizando LangChain, Gemini y APIs externas, siguiendo una arquitectura modular y escalable.

## 👨‍🏫 Metodología de Tutoría
1. **Agente/Mentor:** Explica conceptos y guía el diseño.
2. **Usuario/Desarrollador:** Implementa la lógica basada en las explicaciones.
3. **Feedback:** El mentor revisa el código y sugiere mejoras.

---

## 🗺️ Roadmap del Proyecto

### Fase 1: Expansión de Conocimiento (RAG & Web) 🛠️ [EN PROGRESO]
*   [ ] **Card 1.1: Herramienta de Búsqueda Web**
    *   *Concepto:* Agentic Search con DuckDuckGo.
    *   *Estado:* En diseño. Tarea: Crear `src/tools/search.py`.
*   [ ] **Card 1.2: Herramienta de YouTube**
    *   *Concepto:* Transcripciones para resúmenes de guías.
*   [ ] **Card 1.3: Refinamiento de Prompts**
    *   *Concepto:* System Prompt Engineering para priorizar búsquedas.

### Fase 2: Análisis Avanzado de Steam 📊 [PENDIENTE]
*   [ ] **Card 2.1: Análisis de Logros ("Platinador")**
*   [ ] **Card 2.2: Integración de Storefront API (Ofertas)**
*   [ ] **Card 2.3: Motor de Recomendaciones**

### Fase 3: Interfaz In-Game (Discord) 🤖 [PENDIENTE]
*   [ ] **Card 3.1: Setup del Bot de Discord**
*   [ ] **Card 3.2: Integración Agente <-> Discord**
*   [ ] **Card 3.3: (Plus) Integración de Voz**

---

## 📂 Arquitectura Actual
- `src/api/`: Clientes de APIs externas (Steam).
- `src/tools/`: Herramientas que el LLM puede ejecutar.
- `src/agent/`: Cerebro y configuración del LLM.
- `src/main.py`: Punto de entrada del programa.

---

## 📝 Próximos Pasos (Tarea Actual)
1. Instalar `duckduckgo-search`.
2. Crear `src/tools/search.py`.
3. Definir la función de búsqueda y su `Tool` de LangChain.
4. Integrar la nueva herramienta en `src/agent/brain.py`.

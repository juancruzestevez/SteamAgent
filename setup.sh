#!/bin/bash

# ========================================
# SCRIPT DE INSTALACIÓN AUTOMÁTICA
# Steam Agent - Chatbot de IA
# ========================================

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║        🎮  STEAM AGENT - Instalación Automática  🤖      ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar Python
echo "🔍 Verificando instalación de Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION encontrado"
else
    print_error "Python 3 no está instalado"
    echo "Por favor instala Python 3.8 o superior desde: https://python.org"
    exit 1
fi

# Verificar pip
echo ""
echo "🔍 Verificando pip..."
if command -v pip3 &> /dev/null; then
    print_success "pip encontrado"
else
    print_error "pip no está instalado"
    echo "Instalando pip..."
    python3 -m ensurepip --default-pip
fi

# Crear entorno virtual
echo ""
echo "📦 Creando entorno virtual..."
if [ -d "venv" ]; then
    print_warning "El entorno virtual ya existe. ¿Deseas recrearlo? (s/n)"
    read -r response
    if [[ "$response" =~ ^([sS])$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Entorno virtual recreado"
    else
        print_success "Usando entorno virtual existente"
    fi
else
    python3 -m venv venv
    print_success "Entorno virtual creado"
fi

# Activar entorno virtual
echo ""
echo "🚀 Activando entorno virtual..."
source venv/bin/activate
print_success "Entorno virtual activado"

# Instalar dependencias
echo ""
echo "📥 Instalando dependencias..."
echo "   (Esto puede tomar unos minutos)"
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Dependencias instaladas correctamente"
else
    print_error "Error al instalar dependencias"
    exit 1
fi

# Configurar archivo .env
echo ""
echo "🔐 Configurando archivo .env..."
if [ -f ".env" ]; then
    print_warning "El archivo .env ya existe"
    echo "¿Deseas mantenerlo? (s/n)"
    read -r response
    if [[ "$response" =~ ^([nN])$ ]]; then
        cp .env.example .env
        print_success "Archivo .env recreado desde .env.example"
    else
        print_success "Manteniendo archivo .env existente"
    fi
else
    cp .env.example .env
    print_success "Archivo .env creado desde .env.example"
fi

# Instrucciones para configurar API Keys
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🎯 SIGUIENTE PASO: Configurar tus API Keys"
echo ""
echo "Edita el archivo .env y completa:"
echo ""
echo "1. ANTHROPIC_API_KEY"
echo "   → Obtener en: https://console.anthropic.com/"
echo ""
echo "2. STEAM_API_KEY"
echo "   → Obtener en: https://steamcommunity.com/dev/apikey"
echo ""
echo "3. STEAM_USER_ID"
echo "   → Encontrar en: https://steamid.io/"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Después de configurar .env, ejecuta:"
echo ""
echo "  source venv/bin/activate  # Activar entorno (si no está activo)"
echo "  python main.py            # Iniciar el chatbot"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
print_success "¡Instalación completada!"
echo ""

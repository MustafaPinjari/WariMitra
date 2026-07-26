$ErrorActionPreference = "Stop"

function Write-Step { param([string]$Message) Write-Host "`n==> $Message" -ForegroundColor Cyan }
function Write-Success { param([string]$Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Warning { param([string]$Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Write-ErrorMsg { param([string]$Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-ProgressMsg { param([string]$Message) Write-Host " -> $Message" -ForegroundColor DarkGray }

function Check-Command {
    param([string]$Cmd, [string]$Name)
    if (-not (Get-Command $Cmd -ErrorAction SilentlyContinue)) {
        Write-ErrorMsg "$Name ($Cmd) is not installed or not in PATH."
        exit 1
    }
}

Write-Step "Performing System Checks..."
@("python", "git", "flutter", "node", "npm", "npx") | ForEach-Object { Check-Command $_ $_ }

Write-Step "Checking Git Configuration..."
$gitName = git config --global user.name
$gitEmail = git config --global user.email

if ([string]::IsNullOrWhiteSpace($gitName)) {
    Write-ProgressMsg "Git user.name not found. Setting default."
    git config --global user.name "WariMitra Developer"
}
if ([string]::IsNullOrWhiteSpace($gitEmail)) {
    Write-ProgressMsg "Git user.email not found. Setting default."
    git config --global user.email "developer@warimitra.com"
}

$ProjectName = "WariMitra"
Write-Step "Creating Enterprise Directory Structure..."
$Directories = @(
    "backend", "frontend", "mobile", "docs", "database", "shared", 
    "tests", "infrastructure", "scripts", "postman", ".vscode", 
    ".github/workflows", "backend/requirements"
)
foreach ($dir in $Directories) {
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
}

Write-Step "Setting up Backend (Django Enterprise)..."
Push-Location backend

if (-not (Test-Path "venv")) {
    Write-ProgressMsg "Creating Python virtual environment..."
    python -m venv venv
}
$PythonExec = ".\venv\Scripts\python.exe"
$PipExec = ".\venv\Scripts\pip.exe"

# If Python virtual env creation failed or python executable is missing, fail early
if (-not (Test-Path $PythonExec)) {
    Write-ErrorMsg "Failed to create Python virtual environment. Please ensure Python is correctly installed."
    exit 1
}

& $PythonExec -m pip install --upgrade pip | Out-Null

$BaseDeps = @("Django>=4.2", "djangorestframework", "django-cors-headers", "drf-spectacular", "django-filter", "Pillow", "python-decouple", "psycopg2-binary")
$DevDeps = @("django-extensions", "black", "isort", "flake8", "mypy", "pytest", "pytest-django", "coverage", "pre-commit")
$ProdDeps = @("gunicorn")

$BaseDeps -join "`n" | Out-File "requirements/base.txt" -Encoding utf8
"-r base.txt`n" + ($DevDeps -join "`n") | Out-File "requirements/development.txt" -Encoding utf8
"-r base.txt`n" + ($ProdDeps -join "`n") | Out-File "requirements/production.txt" -Encoding utf8

& $PipExec install -r requirements/development.txt | Out-Null

if (-not (Test-Path "manage.py")) {
    & $PythonExec -m django startproject config . | Out-Null
} else {
    Write-ProgressMsg "Django project already exists. Skipping startproject."
}

$AppsDir = "apps"
if (-not (Test-Path $AppsDir)) { New-Item -ItemType Directory -Force -Path $AppsDir | Out-Null }
if (-not (Test-Path "$AppsDir\__init__.py")) { New-Item -ItemType File -Force -Path "$AppsDir\__init__.py" | Out-Null }

$DjangoApps = @(
    "authentication", "users", "pilgrims", "dindi", "volunteers",
    "ngo", "medical", "police", "temple", "government",
    "community", "sos", "missing_person", "navigation", "maps",
    "notifications", "analytics", "reports", "weather", "media", "audit"
)

foreach ($app in $DjangoApps) {
    $AppPath = "$AppsDir/$app"
    if (-not (Test-Path $AppPath)) {
        New-Item -ItemType Directory -Force -Path $AppPath | Out-Null
        & $PythonExec manage.py startapp $app $AppPath
    }
    
    $AppsPyPath = "$AppPath/apps.py"
    if (Test-Path $AppsPyPath) {
        (Get-Content $AppsPyPath) -replace "name = '$app'", "name = 'apps.$app'" | Set-Content $AppsPyPath
    }
}

$DjangoArchDirs = @("core", "common", "api", "services", "utils", "permissions", "serializers", "tests", "management", "management/commands")
foreach ($d in $DjangoArchDirs) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
    if (-not (Test-Path "$d\__init__.py")) { New-Item -ItemType File -Force -Path "$d\__init__.py" | Out-Null }
}

$CoreAppsPyContent = @"
from django.apps import AppConfig
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
"@
if (-not (Test-Path "core/apps.py")) { Out-File -FilePath "core/apps.py" -InputObject $CoreAppsPyContent -Encoding utf8 }

$BaseModelContent = @"
from django.db import models
class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
"@
if (-not (Test-Path "core/models.py")) { Out-File -FilePath "core/models.py" -InputObject $BaseModelContent -Encoding utf8 }

$CustomUserContent = @"
from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    pass
"@
Out-File -FilePath "apps/users/models.py" -InputObject $CustomUserContent -Encoding utf8

if (-not (Test-Path ".env")) {
    $DbName = "warimitra"
    $DbUser = "postgres"
    $DbPass = "postgres"
    $DbHost = "127.0.0.1"
    $DbPort = "5432"

    $EnvContent = @"
DEBUG=True
SECRET_KEY=django-insecure-replace-me-in-production
DB_NAME=$DbName
DB_USER=$DbUser
DB_PASSWORD=$DbPass
DB_HOST=$DbHost
DB_PORT=$DbPort
"@
    Out-File -FilePath ".env" -InputObject $EnvContent -Encoding utf8
}
Out-File -FilePath ".env.example" -InputObject "DEBUG=True`nSECRET_KEY=`nDB_NAME=`nDB_USER=`nDB_PASSWORD=`nDB_HOST=`nDB_PORT=" -Encoding utf8

if (-not (Test-Path "config/settings")) { New-Item -ItemType Directory -Force -Path "config/settings" | Out-Null }
if (-not (Test-Path "config/settings/__init__.py")) { New-Item -ItemType File -Force -Path "config/settings/__init__.py" | Out-Null }

$SettingsBaseContent = @"
import os
from pathlib import Path
from decouple import config
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    'django_extensions',
    'core',
] + [f'apps.{app}' for app in [
    'authentication', 'users', 'pilgrims', 'dindi', 'volunteers',
    'ngo', 'medical', 'police', 'temple', 'government',
    'community', 'sos', 'missing_person', 'navigation', 'maps',
    'notifications', 'analytics', 'reports', 'weather', 'media', 'audit'
]]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages',],},},]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='warimitra'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='127.0.0.1'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
AUTH_USER_MODEL = 'users.User'
AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},]
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
}
SPECTACULAR_SETTINGS = {
    'TITLE': 'WariMitra API',
    'DESCRIPTION': 'Enterprise API for WariMitra',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler',},},
    'root': {'handlers': ['console'], 'level': 'INFO',},
}
CORS_ALLOW_ALL_ORIGINS = True
"@
Out-File -FilePath "config/settings/base.py" -InputObject $SettingsBaseContent -Encoding utf8
Out-File -FilePath "config/settings/development.py" -InputObject "from .base import *`nDEBUG = True" -Encoding utf8
Out-File -FilePath "config/settings/production.py" -InputObject "from .base import *`nDEBUG = False" -Encoding utf8

if (Test-Path "config/settings/base.py") {
    Remove-Item "config/settings.py" -Force -ErrorAction SilentlyContinue
}

$ManagePyContent = (Get-Content "manage.py") -replace "'config.settings'", "'config.settings.development'"
Out-File -FilePath "manage.py" -InputObject $ManagePyContent -Encoding utf8

$AsgiPyContent = (Get-Content "config/asgi.py") -replace "'config.settings'", "'config.settings.development'"
Out-File -FilePath "config/asgi.py" -InputObject $AsgiPyContent -Encoding utf8

$WsgiPyContent = (Get-Content "config/wsgi.py") -replace "'config.settings'", "'config.settings.development'"
Out-File -FilePath "config/wsgi.py" -InputObject $WsgiPyContent -Encoding utf8

$UrlsContent = @"
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
"@
Out-File -FilePath "config/urls.py" -InputObject $UrlsContent -Encoding utf8

Write-Step "Running Django Migrations..."
try {
    & $PythonExec manage.py makemigrations users
    & $PythonExec manage.py makemigrations
    & $PythonExec manage.py migrate
} catch {
    Write-Warning "Migrations failed. Please ensure PostgreSQL is running and credentials are correct, then run them manually."
}

Pop-Location

Write-Step "Setting up Frontend (Next.js Enterprise)..."
if (-not (Test-Path "frontend/package.json")) {
    npx -y create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-npm | Out-Null
} else {
    Write-ProgressMsg "Next.js frontend already exists. Skipping create-next-app."
}

Push-Location frontend
Write-ProgressMsg "Installing frontend dependencies..."
npm install axios @tanstack/react-query react-hook-form zod zustand next-themes @heroicons/react | Out-Null
npm install -D prettier eslint-config-prettier | Out-Null

$FrontendDirs = @("app", "components", "features", "hooks", "lib", "services", "store", "types", "utils", "constants", "styles")
foreach ($d in $FrontendDirs) {
    if (-not (Test-Path "src/$d")) { New-Item -ItemType Directory -Force -Path "src/$d" | Out-Null }
}

if (-not (Test-Path "src/services/api.ts")) { Out-File -FilePath "src/services/api.ts" -InputObject "export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';" -Encoding utf8 }
if (-not (Test-Path "src/lib/axios.ts")) { Out-File -FilePath "src/lib/axios.ts" -InputObject "import axios from 'axios';`nimport { API_BASE } from '../services/api';`nexport const api = axios.create({ baseURL: API_BASE });" -Encoding utf8 }
if (-not (Test-Path "src/lib/queryClient.ts")) { Out-File -FilePath "src/lib/queryClient.ts" -InputObject "import { QueryClient } from '@tanstack/react-query';`nexport const queryClient = new QueryClient();" -Encoding utf8 }
if (-not (Test-Path "src/styles/theme.ts")) { Out-File -FilePath "src/styles/theme.ts" -InputObject "export const theme = {};" -Encoding utf8 }
if (-not (Test-Path "src/env.d.ts")) { Out-File -FilePath "src/env.d.ts" -InputObject "/// <reference types=`"next`" />`n/// <reference types=`"next/types/global`" />" -Encoding utf8 }
if (-not (Test-Path ".prettierrc")) { Out-File -FilePath ".prettierrc" -InputObject "{ `"semi`": true, `"trailingComma`": `"all`", `"singleQuote`": true, `"printWidth`": 100, `"tabWidth`": 2 }" -Encoding utf8 }
if (-not (Test-Path ".eslintrc.json")) { Out-File -FilePath ".eslintrc.json" -InputObject '{ "extends": ["next/core-web-vitals", "prettier"] }' -Encoding utf8 }

Pop-Location

Write-Step "Setting up Mobile (Flutter Enterprise)..."
if (-not (Test-Path "mobile/pubspec.yaml")) {
    flutter create --org com.warimitra --project-name warimitra mobile | Out-Null
} else {
    Write-ProgressMsg "Flutter mobile project already exists. Skipping flutter create."
}

Push-Location mobile
Write-ProgressMsg "Installing flutter dependencies..."
$FlutterDeps = @("flutter_riverpod", "go_router", "dio", "flutter_secure_storage", "geolocator", "google_maps_flutter", "intl", "flutter_local_notifications", "freezed_annotation", "json_annotation")
$FlutterDevDeps = @("build_runner", "freezed", "json_serializable")
foreach ($dep in $FlutterDeps) { flutter pub add $dep | Out-Null }
foreach ($dep in $FlutterDevDeps) { flutter pub add --dev $dep | Out-Null }

$FlutterDirs = @("core", "config", "constants", "routes", "theme", "widgets", "services", "repository", "features", "models", "providers", "utils")
foreach ($d in $FlutterDirs) {
    if (-not (Test-Path "lib/$d")) { New-Item -ItemType Directory -Force -Path "lib/$d" | Out-Null }
}
Pop-Location

Write-Step "Generating Configuration & Documentation..."
$ReadmeContent = @"
# WariMitra
Government-scale Smart Pilgrimage Management Platform

## Architecture
Backend: Django REST Framework
Frontend: Next.js (App Router, Tailwind)
Mobile: Flutter (Riverpod, GoRouter)

## Development Guide
1. Start PostgreSQL
2. Backend: `cd backend && .\venv\Scripts\activate && python manage.py runserver`
3. Frontend: `cd frontend && npm run dev`
4. Mobile: `cd mobile && flutter run`
"@
if (-not (Test-Path "README.md")) { Out-File -FilePath "README.md" -InputObject $ReadmeContent -Encoding utf8 }
if (-not (Test-Path "CHANGELOG.md")) { Out-File -FilePath "CHANGELOG.md" -InputObject "# Changelog`n`n## [Unreleased] - Initial Setup" -Encoding utf8 }
if (-not (Test-Path "CONTRIBUTING.md")) { Out-File -FilePath "CONTRIBUTING.md" -InputObject "# Contributing`n`nPlease read the code of conduct before contributing." -Encoding utf8 }
if (-not (Test-Path "CODE_OF_CONDUCT.md")) { Out-File -FilePath "CODE_OF_CONDUCT.md" -InputObject "# Code of Conduct`n`nBe respectful." -Encoding utf8 }
if (-not (Test-Path ".editorconfig")) { Out-File -FilePath ".editorconfig" -InputObject "root = true`n`n[*]`ncharset = utf-8`nindent_style = space`nindent_size = 4`ninsert_final_newline = true`ntrim_trailing_whitespace = true`n`n[*.{js,jsx,ts,tsx,json,yml}]`nindent_size = 2" -Encoding utf8 }

$VsCodeSettings = @"
{
    "python.defaultInterpreterPath": "`${workspaceFolder}/backend/venv/Scripts/python.exe",
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "esbenp.prettier-vscode",
    "[python]": { "editor.defaultFormatter": "ms-python.black-formatter" },
    "[dart]": { "editor.defaultFormatter": "Dart-Code.dart-code", "editor.formatOnSave": true }
}
"@
if (-not (Test-Path ".vscode/settings.json")) { Out-File -FilePath ".vscode/settings.json" -InputObject $VsCodeSettings -Encoding utf8 }
if (-not (Test-Path ".vscode/extensions.json")) { Out-File -FilePath ".vscode/extensions.json" -InputObject '{ "recommendations": ["ms-python.python", "ms-python.black-formatter", "Dart-Code.flutter", "dbaeumer.vscode-eslint", "esbenp.prettier-vscode", "bradlc.vscode-tailwindcss"] }' -Encoding utf8 }
if (-not (Test-Path ".vscode/launch.json")) { Out-File -FilePath ".vscode/launch.json" -InputObject '{ "version": "0.2.0", "configurations": [] }' -Encoding utf8 }
if (-not (Test-Path ".vscode/tasks.json")) { Out-File -FilePath ".vscode/tasks.json" -InputObject '{ "version": "2.0.0", "tasks": [] }' -Encoding utf8 }

$GitIgnoreContent = @"
venv/
__pycache__/
*.pyc
.env
db.sqlite3
node_modules/
.next/
out/
build/
.dart_tool/
.packages
.vscode/
.idea/
.DS_Store
"@
if (-not (Test-Path ".gitignore")) { Out-File -FilePath ".gitignore" -InputObject $GitIgnoreContent -Encoding utf8 }

Write-Step "Initializing Git Repository..."
if (-not (Test-Path ".git")) {
    git init | Out-Null
    git add . | Out-Null
    git commit -m "chore: enterprise bootstrap of WariMitra" | Out-Null
}

Write-Success "WariMitra Enterprise setup complete! You are ready to develop."

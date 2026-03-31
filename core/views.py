"""
Módulo de vistas y controladores para PsicoSystem SI2.
Contiene tanto las vistas web MVC como los endpoints de la API REST.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .forms import ClinicaForm, RegistroUsuarioForm, PacienteForm
from .models import Paciente, Cita
from .serializers import (
    PacienteSerializer,
    ClinicaSerializer,
    UsuarioSerializer,
)  # NUEVO: Importación necesaria para T014


# ==============================================================================
# MÓDULO: GESTIÓN ORGANIZACIONAL (TENANT)
# SPRINT 0 | T001 (Arquitectura) | T005 (Modelado)
# ==============================================================================
@login_required  # RNF-03: Seguridad de Acceso (Autenticación Obligatoria)
def registrar_clinica_view(request):
    """
    CU-25: Registrar Clínica | RF-29: Soporte Multi-tenancy
    Propósito: Crear la entidad raíz que aislará todos los datos posteriores.
    """
    if request.method == "POST":
        form = ClinicaForm(request.POST)  # T005: Interacción con formularios Django
        if form.is_valid():
            form.save()  # T004: Persistencia en PostgreSQL
            return redirect("dashboard")  # T007: Navegabilidad del Prototipo UI
    else:
        form = ClinicaForm()

    return render(request, "core/registrar_clinica.html", {"form": form})


# ==============================================================================
# MÓDULO: SEGURIDAD Y ACCESO (IDENTIDAD)
# SPRINT 0 | T001 (Seguridad) | T003 (Estructura Base)
# ==============================================================================
@login_required  # RNF-03: Restricción de acceso para usuarios anónimos
def registrar_usuario_view(request):
    """
    CU-02: Registrar Usuario | RF-28: Gestión de Roles y Permisos
    Propósito: Alta de psicólogos vinculados a una clínica específica.
    """
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()  # T005: Registro basado en AbstractUser personalizado
            return redirect("dashboard")
    else:
        form = RegistroUsuarioForm()

    return render(request, "core/registrar_usuario.html", {"form": form})


# ==============================================================================
# MÓDULO: GESTIÓN DE PACIENTES (LOGICA DE NEGOCIO)
# SPRINT 1 | T014 (Desarrollo Funcional) | RF-02 (Gestión Pacientes)
# ==============================================================================
@login_required
def registrar_paciente_view(request):
    """
    CU-06: Registrar Paciente | RF-29: Aislamiento Lógico de Datos
    Propósito: Garantizar que la data sea privada para cada clínica.
    """
    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            paciente = form.save(
                commit=False
            )  # T014: Preparación de objeto antes de persistir

            # --- PUNTO CRÍTICO DE AUDITORÍA (RF-29) ---
            # Se asigna la clínica del usuario actual sin intervención manual.
            paciente.clinica = request.user.clinica

            paciente.save()  # T004: Persistencia final en BD
            return redirect("dashboard")
    else:
        form = PacienteForm()
    return render(request, "core/registrar_paciente.html", {"form": form})


# ==============================================================================
# MÓDULO: DASHBOARD DE CONTROL (VISUALIZACIÓN)
# SPRINT 0 | T007 (Prototipo UI) | RNF-08 (Eficiencia Operativa)
# ==============================================================================
@login_required
def dashboard_view(request):
    """
    T007: Punto central de control para el usuario final.
    Muestra métricas clave (KPIs) filtradas por pertenencia organizacional.
    """
    clinica = request.user.clinica  # RF-29: Captura del Tenant ID desde la sesión

    # RNF-08: Consultas optimizadas vía ORM para KPIs en tiempo real
    total_pacientes = (
        Paciente.objects.filter(clinica=clinica).count() if clinica else 0  # type: ignore
    )
    citas_pendientes = (
        Cita.objects.filter(
            paciente__clinica=clinica, estado="PENDIENTE"
        ).count()  # type: ignore
        if clinica
        else 0
    )

    contexto = {
        "total_pacientes": total_pacientes,  # KPI: Cantidad de pacientes (RF-02)
        "citas_pendientes": citas_pendientes,  # KPI: Gestión de Agenda
        "clinica_nombre": clinica.nombre if clinica else "S/C",
    }
    return render(request, "core/dashboard.html", contexto)


# ==============================================================================
# CAPA API: SERVICIOS REST (DESACOPLAMIENTO)
# SPRINT 1 | T008 (Arquitectura REST) | T011 (Autenticación JWT) | T014 (Validación)
# ==============================================================================


class DashboardAPIView(APIView):
    """
    RNF-01: Interoperabilidad (Servicio para React/Flutter)
    T008: Implementación de arquitectura orientada a servicios.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna las métricas del dashboard filtradas por la clínica del usuario.
        """
        clinica = request.user.clinica  # RF-29: Multi-tenancy
        total_pacientes = (
            Paciente.objects.filter(clinica=clinica).count() if clinica else 0  # type: ignore
        )
        citas_pendientes = (
            Cita.objects.filter(
                paciente__clinica=clinica, estado="PENDIENTE"
            ).count()  # type: ignore
            if clinica
            else 0
        )

        data = {
            "clinica": clinica.nombre if clinica else "Sin Clínica",
            "metricas": {
                "total_pacientes": total_pacientes,
                "citas_pendientes": citas_pendientes,
            },
        }
        return Response(data, status=status.HTTP_200_OK)


class PacienteCreateAPIView(APIView):
    """
    T014: Desarrollo de funcionalidades de interoperabilidad.
    CU-02: Registro de Paciente vía API (Móvil/React).
    CORRECCIÓN DE AUDITORÍA: Implementación de Serializers para validación robusta.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Crea un nuevo paciente registrado por el móvil u otros clientes.
        """
        # T014: Instanciamos el Serializer con los datos del JSON (Payload)
        serializer = PacienteSerializer(data=request.data)

        # RNF-08: Validación automática (CI único, formatos de fecha, campos requeridos)
        if serializer.is_valid():
            # RF-29: Inyectamos la clínica del usuario autenticado (Seguridad Multi-tenant)
            # Esto evita que un usuario de la Clínica A registre pacientes en la Clínica B.
            serializer.save(clinica=request.user.clinica)

            return Response(
                {
                    "message": "Paciente registrado exitosamente vía REST API",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        # Si los datos son inválidos (ej: CI ya existe), DRF devuelve el error exacto
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# RESOLUCIÓN INCUMPLIMIENTO #3: ENDPOINTS DE ESCRITURA API (INTEROPERABILIDAD)
# ==============================================================================


class ClinicaCreateAPIView(APIView):
    """
    T001 / RF-29: Registro de Clínica vía API.
    Permite que sistemas externos registren organizaciones en la plataforma.
    """

    # En este caso, el registro de clínica suele ser público o de admin
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Crea una nueva clínica mediante JSON."""
        serializer = ClinicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Clínica registrada vía API", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioCreateAPIView(APIView):
    """
    T001 / RF-28: Registro de Psicólogo/Usuario vía API.
    Cumple con la arquitectura híbrida al permitir registros JSON.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Registra un nuevo usuario mediante JSON."""
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            # Aquí podrías añadir lógica extra para roles si fuera necesario
            serializer.save()
            return Response(
                {
                    "message": "Usuario/Psicólogo registrado vía API",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

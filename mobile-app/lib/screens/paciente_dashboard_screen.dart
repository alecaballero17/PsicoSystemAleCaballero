import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/auth_service.dart';
import 'login_screen.dart';
import 'agendar_cita_stepper_screen.dart';
import '../models/user_model.dart';

import 'paciente_profile_screen.dart';
import 'paciente_password_screen.dart';
import 'paciente_pagos_screen.dart';

class PacienteDashboard extends StatefulWidget {
  final String token;
  final String role;
  final String username;

  const PacienteDashboard({
    Key? key,
    required this.token,
    required this.role,
    required this.username,
  }) : super(key: key);

  @override
  _PacienteDashboardState createState() => _PacienteDashboardState();
}

// Implementar WidgetsBindingObserver para el Idle Timeout
class _PacienteDashboardState extends State<PacienteDashboard> with WidgetsBindingObserver {
  bool _isLoading = true;
  User? _user;
  List<dynamic> _clinicas = [];

  final Color primaryBlue = const Color(0xFF2563EB);
  final Color darkBlue = const Color(0xFF0F172A);

  // --- Lógica de Timeout ---
  DateTime? _lastInteractionTime;
  final int _timeoutMinutes = 2; // 2 minutos de inactividad

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _lastInteractionTime = DateTime.now();
    _loadInitialData();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.paused) {
      // Guardar tiempo al minimizar la app
      _lastInteractionTime = DateTime.now();
    } else if (state == AppLifecycleState.resumed) {
      // Al volver, comprobar si pasaron 2 minutos
      if (_lastInteractionTime != null) {
        final difference = DateTime.now().difference(_lastInteractionTime!);
        if (difference.inMinutes >= _timeoutMinutes) {
          _forceLogoutDueToInactivity();
        } else {
          _lastInteractionTime = DateTime.now();
        }
      }
    }
  }

  void _userInteracted() {
    _lastInteractionTime = DateTime.now();
  }

  void _forceLogoutDueToInactivity() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Tu sesión ha expirado por inactividad.'),
        backgroundColor: Colors.orange,
      ),
    );
    _handleLogout(context, force: true);
  }
  // --------------------------

  Future<void> _loadInitialData() async {
    try {
      final userData = await AuthService.getCurrentUser(widget.token);
      final clinicasData = await AuthService.getClinicasPublicas();
      setState(() {
        _user = userData;
        _clinicas = clinicasData;
        _isLoading = false;
      });
    } catch (e) {
      debugPrint("Error loading data: $e");
      setState(() => _isLoading = false);
    }
  }

  void _handleLogout(BuildContext context, {bool force = false}) {
    if (force) {
      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (context) => const LoginScreen()),
        (Route<dynamic> route) => false,
      );
      return;
    }

    // Confirmación visual
    showDialog(
      context: context,
      builder: (BuildContext ctx) {
        return AlertDialog(
          title: Text('Cerrar Sesión', style: GoogleFonts.outfit(fontWeight: FontWeight.bold)),
          content: Text('¿Está seguro que desea cerrar su sesión?', style: GoogleFonts.outfit()),
          actions: [
            TextButton(
              child: Text('Cancelar', style: GoogleFonts.outfit(color: Colors.grey)),
              onPressed: () => Navigator.of(ctx).pop(),
            ),
            TextButton(
              child: Text('Sí, Salir', style: GoogleFonts.outfit(color: Colors.red, fontWeight: FontWeight.bold)),
              onPressed: () {
                Navigator.of(ctx).pop();
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (context) => const LoginScreen()),
                  (Route<dynamic> route) => false,
                );
              },
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    // Usamos GestureDetector para resetear el timer de inactividad mientras usa la app
    return GestureDetector(
      onTap: _userInteracted,
      onPanDown: (_) => _userInteracted,
      // PopScope intercepta el botón atrás físico del celular
      child: PopScope(
        canPop: false,
        onPopInvoked: (bool didPop) {
          if (didPop) return;
          _handleLogout(context); // Muestra confirmación en lugar de cerrar app
        },
        child: Scaffold(
          backgroundColor: const Color(0xFFF8FAFC),
          appBar: AppBar(
            backgroundColor: Colors.white,
            elevation: 0,
            iconTheme: IconThemeData(color: darkBlue),
            title: Text(
              'PsicoSystem',
              style: GoogleFonts.outfit(color: primaryBlue, fontWeight: FontWeight.bold, fontSize: 20),
            ),
            actions: [
              PopupMenuButton<String>(
                icon: Icon(Icons.account_circle_outlined, color: darkBlue, size: 28),
                onSelected: (value) async {
                  _userInteracted();
                  if (value == 'logout') {
                    _handleLogout(context);
                  } else if (value == 'perfil') {
                    if (_user != null) {
                      final updated = await Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => PacienteProfileScreen(user: _user!, token: widget.token)),
                      );
                      if (updated == true) {
                        setState(() => _isLoading = true);
                        _loadInitialData(); // Recargar datos si se actualizó
                      }
                    }
                  } else if (value == 'password') {
                    Navigator.push(context, MaterialPageRoute(builder: (context) => PacientePasswordScreen(token: widget.token)));
                  } else if (value == 'pagos') {
                    Navigator.push(context, MaterialPageRoute(builder: (context) => const PacientePagosScreen()));
                  }
                },
                itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
                  PopupMenuItem<String>(
                    enabled: false,
                    child: Text('Hola, ${widget.username.split("@").first}', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: Colors.black87)),
                  ),
                  const PopupMenuDivider(),
                  PopupMenuItem<String>(
                    value: 'perfil',
                    child: Row(children: [Icon(Icons.person, color: primaryBlue, size: 20), const SizedBox(width: 10), Text('Mi Perfil', style: GoogleFonts.outfit())]),
                  ),
                  PopupMenuItem<String>(
                    value: 'pagos',
                    child: Row(children: [Icon(Icons.payment, color: primaryBlue, size: 20), const SizedBox(width: 10), Text('Realizar Pagos', style: GoogleFonts.outfit())]),
                  ),
                  PopupMenuItem<String>(
                    value: 'password',
                    child: Row(children: [Icon(Icons.lock_reset, color: primaryBlue, size: 20), const SizedBox(width: 10), Text('Cambiar Contraseña', style: GoogleFonts.outfit())]),
                  ),
                  const PopupMenuDivider(),
                  PopupMenuItem<String>(
                    value: 'logout',
                    child: Row(children: [const Icon(Icons.logout, color: Colors.red, size: 20), const SizedBox(width: 10), Text('Cerrar Sesión', style: GoogleFonts.outfit(color: Colors.red))]),
                  ),
                ],
              ),
            ],
          ),
          body: _isLoading
              ? Center(child: CircularProgressIndicator(color: primaryBlue))
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '¿En qué podemos ayudarte hoy?',
                        style: GoogleFonts.outfit(fontSize: 24, fontWeight: FontWeight.bold, color: darkBlue),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Centros de atención médica disponibles:',
                        style: GoogleFonts.outfit(fontSize: 14, color: Colors.grey.shade600),
                      ),
                      const SizedBox(height: 16),
                      
                      // Mostramos DINÁMICAMENTE la lista de clínicas públicas
                      if (_clinicas.isNotEmpty)
                        ..._clinicas.map((clinica) => Padding(
                          padding: const EdgeInsets.only(bottom: 16.0),
                          child: _buildClinicCard(
                            nombre: clinica['nombre'] ?? 'Clínica',
                            direccion: clinica['direccion'] ?? 'Dirección no registrada',
                            especialidades: clinica['especialidades'] ?? 'Psicología General',
                            logo: clinica['logo'],
                            planSuscripcion: clinica['plan_suscripcion'],
                            psicologosCount: clinica['psicologos_count'],
                            planBeneficios: clinica['plan_beneficios'],
                            horario: clinica['horario'],
                          ),
                        )).toList()
                      else
                        const Center(child: Text("No hay clínicas disponibles actualmente.")),
                        
                      const SizedBox(height: 30),
                    ],
                  ),
                ),
        ),
      ),
    );
  }

  Widget _buildClinicCard({
    required String nombre, 
    required String direccion, 
    required String especialidades,
    String? logo,
    String? planSuscripcion,
    int? psicologosCount,
    String? planBeneficios,
    String? horario,
  }) {
    String capInfo = psicologosCount != null ? "$psicologosCount Profesional(es) Activo(s)" : "";

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 15, offset: const Offset(0, 5))],
        border: Border.all(color: Colors.grey.shade100),
      ),
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 52,
                height: 52,
                decoration: BoxDecoration(
                  color: primaryBlue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: logo != null && logo.isNotEmpty
                    ? ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: Image.network(
                          logo,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) => Icon(Icons.health_and_safety, color: primaryBlue, size: 28),
                        ),
                      )
                    : Icon(Icons.health_and_safety, color: primaryBlue, size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(child: Text(nombre, style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, color: darkBlue), overflow: TextOverflow.ellipsis)),
                        if (planSuscripcion != null)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: planSuscripcion == 'Premium' ? Colors.amber.shade100 : planSuscripcion == 'Profesional' ? Colors.blue.shade50 : Colors.grey.shade200,
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              planSuscripcion,
                              style: GoogleFonts.outfit(
                                fontSize: 10, 
                                fontWeight: FontWeight.bold,
                                color: planSuscripcion == 'Premium' ? Colors.amber.shade900 : planSuscripcion == 'Profesional' ? Colors.blue.shade700 : Colors.grey.shade700
                              ),
                            ),
                          )
                      ],
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(Icons.location_on, size: 14, color: Colors.grey),
                        const SizedBox(width: 4),
                        Expanded(child: Text(direccion, style: GoogleFonts.outfit(fontSize: 12, color: Colors.grey.shade600))),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(10)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (horario != null) ...[
                  Row(
                    children: [
                      const Icon(Icons.access_time, size: 16, color: Colors.grey),
                      const SizedBox(width: 8),
                      Expanded(child: Text(horario, style: GoogleFonts.outfit(fontSize: 12, color: darkBlue, fontWeight: FontWeight.w500))),
                    ],
                  ),
                  const SizedBox(height: 6),
                ],
                Row(
                  children: [
                    Icon(Icons.psychology, size: 16, color: primaryBlue),
                    const SizedBox(width: 8),
                    Expanded(child: Text(especialidades, style: GoogleFonts.outfit(fontSize: 12, color: Colors.grey.shade700))),
                  ],
                ),
                if (capInfo.isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      const Icon(Icons.group, size: 16, color: Colors.grey),
                      const SizedBox(width: 8),
                      Expanded(child: Text(capInfo, style: GoogleFonts.outfit(fontSize: 12, color: Colors.grey.shade700))),
                    ],
                  ),
                ],
                if (planBeneficios != null) ...[
                  const SizedBox(height: 6),
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.star, size: 16, color: Colors.amber),
                      const SizedBox(width: 8),
                      Expanded(child: Text(planBeneficios, style: GoogleFonts.outfit(fontSize: 12, color: Colors.grey.shade700, fontStyle: FontStyle.italic))),
                    ],
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Consultando historial en $nombre...', style: GoogleFonts.outfit()), backgroundColor: primaryBlue),
                    );
                  },
                  style: OutlinedButton.styleFrom(
                    foregroundColor: darkBlue, side: BorderSide(color: Colors.grey.shade300),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: Text('Consultar Citas', style: GoogleFonts.outfit(fontWeight: FontWeight.w600)),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: () {
                    if (_user != null) {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => AgendarCitaStepperScreen(
                            user: _user!, 
                            token: widget.token,
                            clinicaSeleccionada: nombre,
                          ),
                        ),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Error: No se pudo cargar la información del usuario.', style: GoogleFonts.outfit()), backgroundColor: Colors.red),
                      );
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: primaryBlue,
                    elevation: 0,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: Text('Programar Cita', style: GoogleFonts.outfit(color: Colors.white, fontWeight: FontWeight.w600)),
                ),
              ),
            ],
          )
        ],
      ),
    );
  }
}
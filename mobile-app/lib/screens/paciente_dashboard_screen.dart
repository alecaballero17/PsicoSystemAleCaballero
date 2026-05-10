import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/auth_service.dart';
import 'login_screen.dart';
import 'agendar_cita_stepper_screen.dart';
import '../models/user_model.dart';

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

class _PacienteDashboardState extends State<PacienteDashboard> {
  bool _isLoading = true;
  User? _user;

  final Color primaryBlue = const Color(0xFF2563EB);
  final Color darkBlue = const Color(0xFF0F172A);

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
  }

  Future<void> _loadUserInfo() async {
    try {
      final data = await AuthService.getCurrentUser(widget.token);
      setState(() {
        _user = data;
        _isLoading = false;
      });
    } catch (e) {
      debugPrint("Error loading user: $e");
      setState(() => _isLoading = false);
    }
  }

  void _handleLogout(BuildContext context) {
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context) => const LoginScreen()),
      (Route<dynamic> route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
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
            onSelected: (value) {
              if (value == 'logout') _handleLogout(context);
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
                value: 'historial',
                child: Row(children: [Icon(Icons.history, color: primaryBlue, size: 20), const SizedBox(width: 10), Text('Historial de Pagos', style: GoogleFonts.outfit())]),
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
                    'Selecciona uno de nuestros centros especializados',
                    style: GoogleFonts.outfit(fontSize: 14, color: Colors.grey.shade600),
                  ),
                  const SizedBox(height: 24),
                  _buildClinicCard(
                    nombre: _user?.clinicaNombre ?? 'Clínica San Aurelio',
                    direccion: 'Av. Principal #123, Zona Sur',
                    especialidades: 'Terapia Cognitiva, Parejas, Infantil',
                  ),
                  const SizedBox(height: 16),
                  _buildClinicCard(
                    nombre: 'Clínica Mente Sana',
                    direccion: 'Calle Los Pinos #45, Centro',
                    especialidades: 'Psiquiatría, Ansiedad, Depresión',
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildClinicCard({required String nombre, required String direccion, required String especialidades}) {
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
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: primaryBlue.withOpacity(0.1), borderRadius: BorderRadius.circular(16)),
                child: Icon(Icons.health_and_safety, color: primaryBlue, size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(nombre, style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, color: darkBlue)),
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
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(10)),
            child: Row(
              children: [
                Icon(Icons.psychology, size: 16, color: primaryBlue),
                const SizedBox(width: 8),
                Expanded(child: Text(especialidades, style: GoogleFonts.outfit(fontSize: 12, color: darkBlue, fontWeight: FontWeight.w500))),
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
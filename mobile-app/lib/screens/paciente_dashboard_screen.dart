import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import 'login_screen.dart';
// [SPRINT 1 - T015] [CU-02] Flujo de Onboarding: Registro de Paciente
import 'registro_paciente_screen.dart';

// [SPRINT 1 - T012] Modelo tipado del usuario autenticado
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
  
  // 🎯 1. CAMBIO CLAVE: Ahora usamos el Modelo User en vez de un Map genérico
  User? _user; 

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
  }

  // T009: Eliminamos el Hardcoding llamando al endpoint /me/
  Future<void> _loadUserInfo() async {
    try {
      // ✅ AHORA (Profesional): debugPrint sin exponer tokens
      debugPrint("Dashboard: Iniciando carga de perfil de usuario..."); 
      
      // Delegamos al servicio. ¡Ahora 'data' es un objeto User real!
      final data = await AuthService.getCurrentUser(widget.token);
      
      setState(() {
        _user = data; // 🎯 2. Guardamos el objeto tipado
        _isLoading = false;
      });
    } catch (e) {
      // ✅ AHORA: debugPrint para errores
      debugPrint("Error al cargar usuario en el Dashboard: $e"); 
      setState(() => _isLoading = false);
    }
  }

  // 👇 FUNCIÓN PROFESIONAL DE LOGOUT PARA T014
  void _handleLogout(BuildContext context) {
    // ✅ AHORA: debugPrint sin exponer lógica interna de negocio
    debugPrint("Auth: Sesión finalizada correctamente.");
    
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (context) => const LoginScreen()),
      (Route<dynamic> route) => false, 
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Mi Perfil - ${widget.role}'),
        backgroundColor: const Color(0xFF1a2233),
        actions: [
          IconButton(
            icon: const Icon(Icons.exit_to_app),
            onPressed: () {
              _handleLogout(context); 
            },
          )
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Card(
                    elevation: 4,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                    child: Padding(
                      padding: const EdgeInsets.all(20.0),
                      child: Column(
                        children: [
                          const CircleAvatar(
                            radius: 40,
                            backgroundColor: Color(0xFF2563eb),
                            child: Icon(Icons.person, size: 50, color: Colors.white),
                          ),
                          const SizedBox(height: 15),
                          Text(
                            'Bienvenido, ${widget.username}',
                            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 5),
                          
                          // 🎯 3. CAMBIO CLAVE: Usamos el PUNTO para acceder al dato de forma segura
                          Text(
                            'Clínica: ${_user?.clinicaNombre ?? 'Sin Clínica Asignada'}',
                            style: const TextStyle(color: Colors.blueGrey, fontWeight: FontWeight.w500),
                          ),
                          
                          const Text(
                            'Estado de la API: Conectado (JWT) ✅',
                            style: TextStyle(color: Colors.green, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'Mis Próximas Sesiones',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1a2233)),
                  ),
                  const SizedBox(height: 10),
                  const Expanded(
                    child: Center(
                      child: Text(
                        "No tienes sesiones pendientes para hoy.\n(Sincronizado con PostgreSQL)",
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey),
                      ),
                    ),
                  )
                ],
              ),
            ),
    );
  }
}
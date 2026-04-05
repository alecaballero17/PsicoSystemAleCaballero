import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart'; // NECESARIO PARA kIsWeb
import 'dart:convert';
import 'package:http/http.dart' as http;

// T014: Interoperabilidad (Mobile App). 
// Manejo Dinámico de IP: Si corres en Web (Edge) usa 127.0.0.1, si es Emulador usa 10.0.2.2.
final String API_BASE_URL = kIsWeb ? 'http://127.0.0.1:8000/api' : 'http://192.168.0.196:8000/api';

void main() {
  runApp(const PsicoSystemApp());
}

class PsicoSystemApp extends StatelessWidget {
  const PsicoSystemApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PsicoSystem Paciente',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primaryColor: const Color(0xFF1a2233), // Azul profundo oscuro
        scaffoldBackgroundColor: const Color(0xFFF0F4F8),
        colorScheme: ColorScheme.fromSwatch().copyWith(
          secondary: const Color(0xFF2563eb), // Azul brillante web
        ),
        fontFamily: 'Roboto',
      ),
      home: const LoginScreen(),
    );
  }
}

// =====================================================================
// MODO PACIENTE: PANTALLA DE AUTENTICACIÓN (CU-01 / RF-01)
// =====================================================================
class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _login() async {
    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse('$API_BASE_URL/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': _usernameController.text,
          'password': _passwordController.text,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final role = data['role'];
        final token = data['access'];

        // Validación de Seguridad Estricta (Solo Pacientes en la App Móvil)
        if (role == 'PACIENTE') {
           Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => PacienteDashboard(
                token: token,
                role: role,
                username: _usernameController.text,
              ),
            ),
          );
        } else {
          _showError('Acceso Denegado: Aplicación exclusiva para pacientes.');
        }
      } else {
        _showError('Credenciales incorrectas (HTTP ${response.statusCode})');
      }
    } catch (e) {
      _showError('Error de red: Revise la conexión de su emulador o WiFi.');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.redAccent),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1a2233), // Themed background
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.psychology, size: 80, color: Colors.white),
              const SizedBox(height: 20),
              const Text(
                'PsicoSystem',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const Text(
                'Portal de Pacientes',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.white70,
                ),
              ),
              const SizedBox(height: 40),
              // Caja de formulario
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(15),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    )
                  ],
                ),
                child: Column(
                  children: [
                    TextField(
                      controller: _usernameController,
                      decoration: const InputDecoration(
                        labelText: 'Usuario',
                        prefixIcon: Icon(Icons.person),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 20),
                    TextField(
                      controller: _passwordController,
                      obscureText: true,
                      decoration: const InputDecoration(
                        labelText: 'Contraseña',
                        prefixIcon: Icon(Icons.lock),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 30),
                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563eb),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        onPressed: _isLoading ? null : _login,
                        child: _isLoading
                            ? const CircularProgressIndicator(color: Colors.white)
                            : const Text(
                                'INGRESAR',
                                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// =====================================================================
// DASHBOARD DEL PACIENTE (Visualización de Citas y Perfil)
// =====================================================================
class PacienteDashboard extends StatelessWidget {
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
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Mi Perfil - $role'),
        backgroundColor: const Color(0xFF1a2233),
        actions: [
          IconButton(
            icon: const Icon(Icons.exit_to_app),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
              );
            },
          )
        ],
      ),
      body: Padding(
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
                      'Bienvenido, $username',
                      style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 5),
                    const Text('Estado de la API: Conectado (JWT) ✅', 
                      style: TextStyle(color: Colors.green, fontWeight: FontWeight.w500)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Text(
              'Mis Sesiones Clínicas',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1a2233)),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: ListView(
                children: const [
                   Card(
                    child: ListTile(
                      leading: Icon(Icons.calendar_today, color: Color(0xFF2563eb)),
                      title: Text('Sesión Psicológica Inicial'),
                      subtitle: Text('Fecha a definir (Sprint 2 del Backend)'),
                      trailing: Chip(label: Text('Pendiente')),
                    ),
                  )
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}

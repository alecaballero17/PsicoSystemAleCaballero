import 'package:flutter/material.dart';

// 1. IMPORTAMOS NUESTRO SERVICIO
import '../services/auth_service.dart'; 
import 'package:psicosystem_mobile/screens/paciente_dashboard_screen.dart';

// 🔥 2. IMPORTAMOS TUS NUEVOS WIDGETS
import '../widgets/custom_button.dart';
import '../widgets/custom_input.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  // FUNCIÓN DE LOGIN REFACTORIZADA (Tipado Fuerte Aplicado)
  Future<void> _login() async {
    setState(() => _isLoading = true);

    try {
      // Delegamos al servicio. ¡Ahora response es un objeto AuthResponse!
      final response = await AuthService.login(
        _usernameController.text, 
        _passwordController.text
      );

      // 🔥 TIPADO FUERTE: Accedemos a las propiedades con "punto", no con corchetes
      final role = response.role;
      final token = response.access;

      // Validación de Seguridad Estricta (Solo Pacientes)
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
    } catch (e) {
      _showError(e.toString().replaceAll('Exception: ', ''));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.redAccent),
    );
  }

  // =====================================================================
  // INTERFAZ DE USUARIO (Limpia, Corta y Reutilizable)
  // =====================================================================
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1a2233), 
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
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const Text(
                'Portal de Pacientes',
                style: TextStyle(fontSize: 16, color: Colors.white70),
              ),
              const SizedBox(height: 40),
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
                    // 🎯 1. USAMOS TU WIDGET DE INPUT
                    CustomInput(
                      label: 'Usuario',
                      icon: Icons.person,
                      controller: _usernameController,
                    ),
                    const SizedBox(height: 20),
                    
                    // 🎯 2. USAMOS TU WIDGET DE INPUT PARA CONTRASEÑA
                    CustomInput(
                      label: 'Contraseña',
                      icon: Icons.lock,
                      controller: _passwordController,
                      isPassword: true,
                    ),
                    const SizedBox(height: 30),
                    
                    // 🎯 3. USAMOS TU WIDGET DE BOTÓN
                    _isLoading 
                      ? const CircularProgressIndicator(color: Color(0xFF2563eb))
                      : CustomButton(
                          text: 'INGRESAR',
                          color: const Color(0xFF2563eb),
                          onPressed: _login,
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
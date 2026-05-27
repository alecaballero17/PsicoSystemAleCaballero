// [SPRINT 1 - T015] Onboarding Móvil Público: Interfaz Flutter para auto-registro de pacientes.
// [RF-02] Registro de Pacientes.
// [RF-29] Aislamiento SaaS: El paciente selecciona su clínica en on-boarding.
// [CU-02] Registro de Paciente (Autogestión).

import 'package:flutter/material.dart';
import '../services/paciente_service.dart';

// ==============================================================================
// PANTALLA: REGISTRO DE PACIENTE PÚBLICO [SPRINT 1 - T015]
// ==============================================================================
class RegistroPacienteScreen extends StatefulWidget {
  const RegistroPacienteScreen({Key? key}) : super(key: key);

  @override
  State<RegistroPacienteScreen> createState() => _RegistroPacienteScreenState();
}

class _RegistroPacienteScreenState extends State<RegistroPacienteScreen> {
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  // Controladores de campos
  final _nombreCtrl = TextEditingController();
  final _ciCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _fechaNacimientoCtrl = TextEditingController();
  final _telefonoCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _ciCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _fechaNacimientoCtrl.dispose();
    _telefonoCtrl.dispose();
    super.dispose();
  }

  // [SPRINT 1 - T015] [CU-02] Envío del formulario simplificado
  Future<void> _registrar() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      await PacienteService.registrarPacientePublico(
        nombre: _nombreCtrl.text.trim(),
        ci: _ciCtrl.text.trim(),
        email: _emailCtrl.text.trim(),
        password: _passwordCtrl.text,
        telefono: _telefonoCtrl.text.trim(),
        // clinicaId y fechaNacimiento son ahora opcionales en el backend
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Registro exitoso. ¡Ahora inicia sesión!'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 3),
        ),
      );
      Navigator.pop(context); 
    } catch (e) {
      if (!mounted) return;
      _showError(e.toString().replaceAll("Exception: ", ""));
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('❌ $message'), backgroundColor: Colors.redAccent),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF0F4F8),
      appBar: AppBar(
        title: const Text(
          'Crear Cuenta',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1a2233),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'ÚNETE A PSICOSYSTEM',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: Color(0xFF1e293b)),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Ingresa tus datos básicos para comenzar.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Color(0xFF64748b)),
                ),
                const SizedBox(height: 32),

                _buildField(
                  controller: _nombreCtrl,
                  label: 'Nombre Completo',
                  icon: Icons.person,
                  validator: (v) => (v == null || v.isEmpty) ? 'Ingresa tu nombre' : null,
                ),
                const SizedBox(height: 16),

                _buildField(
                  controller: _ciCtrl,
                  label: 'Cédula de Identidad (CI)',
                  icon: Icons.credit_card,
                  keyboardType: TextInputType.number,
                  validator: (v) => (v == null || v.isEmpty) ? 'Ingresa tu CI' : null,
                ),
                const SizedBox(height: 16),

                _buildField(
                  controller: _emailCtrl,
                  label: 'Correo Electrónico',
                  icon: Icons.email,
                  keyboardType: TextInputType.emailAddress,
                  validator: (v) => (v == null || !v.contains('@')) ? 'Correo inválido' : null,
                ),
                const SizedBox(height: 16),

                _buildField(
                  controller: _telefonoCtrl,
                  label: 'Teléfono / WhatsApp',
                  icon: Icons.phone_android,
                  keyboardType: TextInputType.phone,
                  validator: (v) => (v == null || v.isEmpty) ? 'Ingresa tu teléfono' : null,
                ),
                const SizedBox(height: 16),

                _buildField(
                  controller: _passwordCtrl,
                  label: 'Contraseña de Acceso',
                  icon: Icons.lock,
                  obscureText: true,
                  validator: (v) {
                    if (v == null || v.isEmpty) return 'Campo obligatorio';
                    if (v.length < 8) return 'Mínimo 8 caracteres';
                    if (!RegExp(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$').hasMatch(v)) {
                      return 'Usa 1 mayúscula, 1 minúscula y 1 número';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 32),

                _isLoading
                    ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563eb)))
                    : ElevatedButton(
                        onPressed: _registrar,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563eb),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 18),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          elevation: 4,
                        ),
                        child: const Text(
                          'REGISTRARME AHORA',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, letterSpacing: 1),
                        ),
                      ),
                const SizedBox(height: 20),
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('¿Ya tienes cuenta? Inicia Sesión', style: TextStyle(color: Color(0xFF2563eb), fontWeight: FontWeight.w600)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  InputDecoration _inputDecoration(String label, IconData icon) {
    return InputDecoration(
      labelText: label,
      prefixIcon: Icon(icon, color: const Color(0xFF64748b), size: 20),
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFFcbd5e1))),
      enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFFcbd5e1))),
      focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF2563eb), width: 1.5)),
      errorBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Colors.redAccent)),
      labelStyle: const TextStyle(fontSize: 13, color: Color(0xFF64748b)),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
    );
  }

  Widget _buildField({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool obscureText = false,
    TextInputType keyboardType = TextInputType.text,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      obscureText: obscureText,
      validator: validator,
      decoration: _inputDecoration(label, icon),
    );
  }
}

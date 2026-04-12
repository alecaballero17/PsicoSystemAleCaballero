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
  List<Map<String, dynamic>> _clinicas = [];
  int? _selectedClinica;

  // Controladores de campos
  final _nombreCtrl = TextEditingController();
  final _ciCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _cargarClinicas();
  }

  Future<void> _cargarClinicas() async {
    final clinicas = await PacienteService.getClinicasPublic();
    if (mounted) {
      setState(() {
        _clinicas = clinicas;
      });
    }
  }

  @override
  void dispose() {
    _nombreCtrl.dispose();
    _ciCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  // [SPRINT 1 - T015] [CU-02] Envío del formulario al API REST público
  Future<void> _registrar() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      await PacienteService.registrarPacientePublico(
        nombre: _nombreCtrl.text.trim(),
        ci: _ciCtrl.text.trim(),
        email: _emailCtrl.text.trim(),
        password: _passwordCtrl.text,
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Registro completado. ¡Inicia sesión!'),
          backgroundColor: Colors.green,
          duration: Duration(seconds: 3),
        ),
      );
      Navigator.pop(context); // Vuelve al login
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

  // ==============================================================================
  // CONSTRUCCIÓN DE LA INTERFAZ
  // ==============================================================================
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
        iconTheme: const IconThemeData(color: Colors.white),
        elevation: 0,
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildSectionTitle('DATOS PERSONALES'),
                const SizedBox(height: 12),

                _buildField(
                  controller: _nombreCtrl,
                  label: 'Nombre Completo',
                  icon: Icons.person,
                  validator: (v) => (v == null || v.isEmpty) ? 'Campo obligatorio' : null,
                ),
                const SizedBox(height: 14),

                _buildField(
                  controller: _ciCtrl,
                  label: 'Cédula de Identidad (CI)',
                  icon: Icons.badge,
                  keyboardType: TextInputType.number,
                  validator: (v) => (v == null || v.isEmpty) ? 'Campo obligatorio' : null,
                ),
                const SizedBox(height: 20),

                _buildSectionTitle('CREDENCIALES DE ACCESO'),
                const SizedBox(height: 12),

                _buildField(
                  controller: _emailCtrl,
                  label: 'Correo Electrónico',
                  icon: Icons.email,
                  keyboardType: TextInputType.emailAddress,
                  validator: (v) => (v == null || !v.contains('@')) ? 'Correo inválido' : null,
                ),
                const SizedBox(height: 14),

                // [RNF-03] Máscara de asteriscos para contraseña
                _buildField(
                  controller: _passwordCtrl,
                  label: 'Contraseña',
                  icon: Icons.lock,
                  obscureText: true,
                  validator: (v) => (v == null || v.length < 6) ? 'Mínimo 6 caracteres' : null,
                ),
                const SizedBox(height: 28),

                _isLoading
                    ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563eb)))
                    : ElevatedButton.icon(
                        onPressed: _registrar,
                        icon: const Icon(Icons.check_circle),
                        label: const Text(
                          'COMPLETAR REGISTRO',
                          style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563eb),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                      ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF64748b), letterSpacing: 1.0,
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

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/auth_service.dart';
import '../models/user_model.dart';

class PacienteProfileScreen extends StatefulWidget {
  final User user;
  final String token;

  const PacienteProfileScreen({Key? key, required this.user, required this.token}) : super(key: key);

  @override
  _PacienteProfileScreenState createState() => _PacienteProfileScreenState();
}

class _PacienteProfileScreenState extends State<PacienteProfileScreen> {
  late TextEditingController _firstNameController;
  late TextEditingController _ciController;
  late TextEditingController _telefonoController;
  bool _isLoading = false;

  final Color primaryBlue = const Color(0xFF2563EB);

  @override
  void initState() {
    super.initState();
    _firstNameController = TextEditingController(text: widget.user.firstName ?? '');
    _ciController = TextEditingController(text: widget.user.ci ?? '');
    _telefonoController = TextEditingController(text: widget.user.telefono ?? '');
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _ciController.dispose();
    _telefonoController.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    setState(() => _isLoading = true);
    try {
      await AuthService.updateProfile(
        widget.token,
        _firstNameController.text.trim(),
        _ciController.text.trim(), // Enviamos CI en lugar de apellido
        _telefonoController.text.trim(),
      );
      
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Perfil actualizado correctamente'), backgroundColor: Colors.green),
      );
      Navigator.pop(context, true); // Devuelve true para recargar el dashboard
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString()), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: Text('Editar Mi Perfil', style: GoogleFonts.outfit(color: Colors.black87, fontWeight: FontWeight.bold)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Stack(
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundColor: primaryBlue.withOpacity(0.1),
                    child: Icon(Icons.person, size: 50, color: primaryBlue),
                  ),
                  Positioned(
                    bottom: 0,
                    right: 0,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: const BoxDecoration(color: Colors.white, shape: BoxShape.circle),
                      child: Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(color: primaryBlue, shape: BoxShape.circle),
                        child: const Icon(Icons.edit, size: 16, color: Colors.white),
                      ),
                    ),
                  )
                ],
              ),
            ),
            const SizedBox(height: 32),
            
            _buildTextField('Nombre', _firstNameController, Icons.person),
            const SizedBox(height: 16),
            _buildTextField('Cédula de Identidad (CI)', _ciController, Icons.credit_card),
            const SizedBox(height: 16),
            _buildTextField('Teléfono', _telefonoController, Icons.phone),
            const SizedBox(height: 16),
            
            // Campo de solo lectura para el email
            TextField(
              controller: TextEditingController(text: widget.user.email ?? widget.user.username),
              enabled: false,
              decoration: InputDecoration(
                labelText: 'Correo Electrónico (No editable)',
                prefixIcon: const Icon(Icons.email_outlined, color: Colors.grey),
                filled: true,
                fillColor: Colors.grey.shade200,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
              ),
            ),
            
            const SizedBox(height: 40),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _saveProfile,
                style: ElevatedButton.styleFrom(
                  backgroundColor: primaryBlue,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: _isLoading 
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text('Guardar Cambios', style: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, IconData icon) {
    return TextField(
      controller: controller,
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon, color: primaryBlue),
        filled: true,
        fillColor: Colors.white,
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: Colors.grey.shade200)),
        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: primaryBlue, width: 2)),
      ),
    );
  }
}

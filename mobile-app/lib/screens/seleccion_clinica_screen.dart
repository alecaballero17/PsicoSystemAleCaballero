import 'package:flutter/material.dart';
import '../services/paciente_service.dart';
import '../widgets/custom_button.dart';
import 'paciente_dashboard_screen.dart';

class SeleccionClinicaScreen extends StatefulWidget {
  final String token;
  final String username;

  const SeleccionClinicaScreen({
    Key? key,
    required this.token,
    required this.username,
  }) : super(key: key);

  @override
  _SeleccionClinicaScreenState createState() => _SeleccionClinicaScreenState();
}

class _SeleccionClinicaScreenState extends State<SeleccionClinicaScreen> {
  bool _isLoading = false;
  List<Map<String, dynamic>> _clinicas = [];
  int? _selectedClinica;

  @override
  void initState() {
    super.initState();
    _fetchClinicas();
  }

  Future<void> _fetchClinicas() async {
    setState(() => _isLoading = true);
    try {
      final clinicas = await PacienteService.getClinicasPublic();
      setState(() => _clinicas = clinicas);
    } catch (e) {
      _showError('No se pudieron cargar las clínicas.');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _finalizarVinculacion() async {
    if (_selectedClinica == null) {
      _showError('Por favor selecciona una clínica.');
      return;
    }

    setState(() => _isLoading = true);
    try {
      await PacienteService.vincularClinica(
        token: widget.token,
        clinicaId: _selectedClinica!,
      );

      if (!mounted) return;
      
      // ✅ ÉXITO: Navegar al Dashboard
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => PacienteDashboard(
            token: widget.token,
            role: 'PACIENTE',
            username: widget.username,
          ),
        ),
      );
    } catch (e) {
      _showError(e.toString().replaceAll('Exception: ', ''));
    } finally {
      if (mounted) setState(() => _isLoading = false);
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
      backgroundColor: const Color(0xFF1a2233),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.location_city, size: 80, color: Colors.white),
              const SizedBox(height: 20),
              const Text(
                'Selecciona tu Clínica',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 10),
              const Text(
                'Para continuar, necesitamos saber en qué centro te atenderás.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.white70),
              ),
              const SizedBox(height: 40),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(15),
                ),
                child: Column(
                  children: [
                    _isLoading && _clinicas.isEmpty
                        ? const CircularProgressIndicator()
                        : DropdownButtonFormField<int>(
                            value: _selectedClinica,
                            items: _clinicas.map((c) {
                              return DropdownMenuItem<int>(
                                value: c['id'],
                                child: Text(c['nombre']),
                              );
                            }).toList(),
                            onChanged: (val) =>
                                setState(() => _selectedClinica = val),
                            decoration: const InputDecoration(
                              labelText: 'Clínica Disponible',
                              prefixIcon: Icon(Icons.apartment),
                              border: OutlineInputBorder(),
                            ),
                          ),
                    const SizedBox(height: 30),
                    _isLoading && _clinicas.isNotEmpty
                        ? const CircularProgressIndicator()
                        : CustomButton(
                            text: 'CONFIRMAR Y ENTRAR',
                            color: const Color(0xFF16a34a),
                            onPressed: _finalizarVinculacion,
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

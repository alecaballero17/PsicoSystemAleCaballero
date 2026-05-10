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
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: _isLoading && _clinicas.isEmpty
                      ? const Center(child: CircularProgressIndicator())
                      : _clinicas.isEmpty
                        ? const Center(child: Text("No hay clínicas disponibles", style: TextStyle(color: Colors.grey)))
                        : ListView.builder(
                            itemCount: _clinicas.length,
                            itemBuilder: (context, index) {
                              final c = _clinicas[index];
                              final isSelected = _selectedClinica == c['id'];
                              return Container(
                                margin: const EdgeInsets.symmetric(vertical: 4),
                                decoration: BoxDecoration(
                                  color: isSelected ? Colors.blue.withOpacity(0.1) : Colors.transparent,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: isSelected ? Colors.blue : Colors.grey.withOpacity(0.2),
                                    width: isSelected ? 2 : 1,
                                  ),
                                ),
                                child: ListTile(
                                  leading: Container(
                                    width: 45,
                                    height: 45,
                                    decoration: BoxDecoration(
                                      color: Colors.grey[100],
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: c['logo'] != null
                                        ? ClipRRect(
                                            borderRadius: BorderRadius.circular(8),
                                            child: Image.network(c['logo'], fit: BoxFit.cover),
                                          )
                                        : const Icon(Icons.business, color: Colors.blue),
                                  ),
                                  title: Text(
                                    c['nombre'],
                                    style: TextStyle(
                                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                                      color: isSelected ? Colors.blue : Colors.black87,
                                    ),
                                  ),
                                  subtitle: Text(c['email_contacto'] ?? 'Centro Médico', style: const TextStyle(fontSize: 11)),
                                  trailing: isSelected 
                                      ? const Icon(Icons.check_circle, color: Colors.blue)
                                      : null,
                                  onTap: () => setState(() => _selectedClinica = c['id']),
                                ),
                              );
                            },
                          ),
                ),
              ),
              const SizedBox(height: 20),
              if (_clinicas.isNotEmpty)
                _isLoading
                    ? const CircularProgressIndicator()
                    : CustomButton(
                        text: 'CONFIRMAR Y ENTRAR',
                        color: const Color(0xFF2563eb),
                        onPressed: _finalizarVinculacion,
                      ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}

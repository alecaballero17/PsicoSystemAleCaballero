import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../services/cita_pago_service.dart';

class HistorialMedicoScreen extends StatefulWidget {
  final String token;

  const HistorialMedicoScreen({
    Key? key,
    required this.token,
  }) : super(key: key);

  @override
  _HistorialMedicoScreenState createState() => _HistorialMedicoScreenState();
}

class _HistorialMedicoScreenState extends State<HistorialMedicoScreen> {
  bool _isLoading = true;
  List<dynamic> _todasCitas = [];
  String? _error;

  // Filtros
  String _filtroEstado = 'TODOS';
  String _filtroClinica = '';
  
  final Color primaryBlue = const Color(0xFF2563EB);
  final Color darkBlue = const Color(0xFF0F172A);

  @override
  void initState() {
    super.initState();
    _loadHistorial();
  }

  Future<void> _loadHistorial() async {
    try {
      final data = await CitaPagoService.getHistorial(widget.token);
      final citas = data['citas'] ?? data['results'] ?? data;
      setState(() {
        _todasCitas = citas is List ? citas : [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  List<dynamic> get _citasFiltradas {
    return _todasCitas.where((cita) {
      final estado = (cita['estado'] ?? 'PROGRAMADA').toUpperCase();
      final clinicaNombre = (cita['clinica_nombre'] ?? '').toUpperCase();
      
      if (_filtroEstado != 'TODOS' && estado != _filtroEstado) return false;
      if (_filtroClinica.isNotEmpty && !clinicaNombre.contains(_filtroClinica.toUpperCase())) return false;
      
      return true;
    }).toList();
  }

  Color _estadoColor(String estado) {
    switch (estado.toUpperCase()) {
      case 'REALIZADA': return Colors.green;
      case 'CANCELADA': return Colors.red;
      case 'PROGRAMADA': return primaryBlue;
      default: return Colors.orange;
    }
  }

  IconData _estadoIcon(String estado) {
    switch (estado.toUpperCase()) {
      case 'REALIZADA': return Icons.check_circle_rounded;
      case 'CANCELADA': return Icons.cancel_rounded;
      case 'PROGRAMADA': return Icons.calendar_month_rounded;
      default: return Icons.schedule_rounded;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: IconThemeData(color: darkBlue),
        title: Text('Historial Médico', style: GoogleFonts.outfit(color: darkBlue, fontWeight: FontWeight.bold, fontSize: 20)),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: primaryBlue),
            onPressed: () {
              setState(() => _isLoading = true);
              _loadHistorial();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          _buildFilters(),
          Expanded(
            child: _isLoading
                ? Center(child: CircularProgressIndicator(color: primaryBlue))
                : _error != null
                    ? _buildError()
                    : _citasFiltradas.isEmpty
                        ? _buildEmpty()
                        : _buildCitasList(),
          ),
        ],
      ),
    );
  }

  Widget _buildFilters() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Column(
        children: [
          TextField(
            decoration: InputDecoration(
              hintText: 'Buscar por clínica...',
              prefixIcon: const Icon(Icons.search),
              filled: true,
              fillColor: Colors.grey.shade100,
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
            ),
            onChanged: (val) {
              setState(() {
                _filtroClinica = val;
              });
            },
          ),
          const SizedBox(height: 12),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: ['TODOS', 'PROGRAMADA', 'REALIZADA', 'CANCELADA'].map((estado) {
                final isSelected = _filtroEstado == estado;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(estado, style: GoogleFonts.outfit(
                      color: isSelected ? Colors.white : darkBlue,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    )),
                    selected: isSelected,
                    onSelected: (selected) {
                      setState(() {
                        _filtroEstado = estado;
                      });
                    },
                    selectedColor: primaryBlue,
                    backgroundColor: Colors.grey.shade100,
                    checkmarkColor: Colors.white,
                  ),
                );
              }).toList(),
            ),
          )
        ],
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.wifi_off_rounded, size: 64, color: Colors.grey.shade400),
            const SizedBox(height: 16),
            Text('No se pudo cargar el historial', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: darkBlue, fontSize: 18)),
            const SizedBox(height: 8),
            Text(_error ?? '', style: GoogleFonts.outfit(color: Colors.grey.shade500, fontSize: 13), textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  Widget _buildEmpty() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.history_edu, size: 80, color: Colors.grey.shade300),
            const SizedBox(height: 24),
            Text('Sin historial', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 20, color: darkBlue)),
            const SizedBox(height: 12),
            Text(
              'No se encontraron citas con los filtros actuales.',
              style: GoogleFonts.outfit(color: Colors.grey.shade500, fontSize: 14),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCitasList() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _citasFiltradas.length,
      itemBuilder: (context, index) {
        final cita = _citasFiltradas[index];
        final fechaStr = cita['fecha_hora'] ?? '';
        final estado = cita['estado'] ?? 'PROGRAMADA';
        final psicologo = cita['psicologo_nombre'] ?? cita['psicologo'] ?? 'Psicólogo';
        final motivo = cita['motivo'] ?? '';
        final clinica = cita['clinica_nombre'] ?? 'Clínica Desconocida';
        final numeroFicha = cita['numero_ficha'] ?? 'FICHA-00000';

        DateTime? fecha;
        try { fecha = DateTime.parse(fechaStr).toLocal(); } catch (_) {}

        return Container(
          margin: const EdgeInsets.only(bottom: 16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4))],
            border: Border.all(color: Colors.grey.shade100),
          ),
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: _estadoColor(estado).withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Icon(_estadoIcon(estado), color: _estadoColor(estado), size: 22),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text("Ficha: $numeroFicha", style: GoogleFonts.outfit(color: Colors.grey.shade600, fontSize: 12, fontWeight: FontWeight.bold)),
                          Text(psicologo, style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 16, color: darkBlue)),
                          Text(clinica, style: GoogleFonts.outfit(color: primaryBlue, fontSize: 13, fontWeight: FontWeight.w600)),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                      decoration: BoxDecoration(color: _estadoColor(estado).withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
                      child: Text(estado, style: GoogleFonts.outfit(color: _estadoColor(estado), fontWeight: FontWeight.bold, fontSize: 11)),
                    ),
                  ],
                ),
                if (motivo.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text("Motivo: $motivo", style: GoogleFonts.outfit(color: Colors.grey.shade600, fontSize: 13, fontStyle: FontStyle.italic)),
                ],
                const SizedBox(height: 14),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(10)),
                  child: Row(
                    children: [
                      const Icon(Icons.calendar_today, size: 15, color: Colors.grey),
                      const SizedBox(width: 8),
                      if (fecha != null)
                        Text(DateFormat("dd/MM/yyyy 'a las' HH:mm").format(fecha), style: GoogleFonts.outfit(fontWeight: FontWeight.w600, fontSize: 13, color: darkBlue))
                      else
                        Text("Fecha no válida", style: GoogleFonts.outfit(color: Colors.red)),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

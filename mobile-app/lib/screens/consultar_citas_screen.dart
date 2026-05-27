import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../services/cita_pago_service.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'chatbot_screen.dart';
import '../services/chatbot_service.dart';

class ConsultarCitasScreen extends StatefulWidget {
  final String token;
  final String clinicaNombre;
  final int? clinicaId;

  const ConsultarCitasScreen({
    Key? key,
    required this.token,
    required this.clinicaNombre,
    this.clinicaId,
  }) : super(key: key);

  @override
  _ConsultarCitasScreenState createState() => _ConsultarCitasScreenState();
}

class _ConsultarCitasScreenState extends State<ConsultarCitasScreen> {
  bool _isLoading = true;
  List<dynamic> _citas = [];
  String? _error;
  Timer? _timer;

  final Color primaryBlue = const Color(0xFF2563EB);
  final Color darkBlue = const Color(0xFF0F172A);

  @override
  void initState() {
    super.initState();
    _loadCitas();
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (mounted) setState(() {});
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _loadCitas() async {
    try {
      final data = await CitaPagoService.getHistorial(
        widget.token,
        clinicaId: widget.clinicaId,
        estado: 'PENDIENTE',
      );
      final citas = data['citas'] ?? data['results'] ?? data;
      setState(() {
        _citas = citas is List ? citas : [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  String _buildCountdown(String fechaHoraStr) {
    try {
      final fecha = DateTime.parse(fechaHoraStr).toLocal();
      final now = DateTime.now();
      final diff = fecha.difference(now);
      if (diff.isNegative) return 'Ya pasó';
      final days = diff.inDays;
      final hours = diff.inHours % 24;
      final minutes = diff.inMinutes % 60;
      final seconds = diff.inSeconds % 60;
      if (days > 0) return 'En $days día(s), ${hours}h ${minutes}m';
      if (hours > 0) return 'En ${hours}h ${minutes}m ${seconds}s';
      return 'En ${minutes}m ${seconds}s';
    } catch (_) {
      return '';
    }
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
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Mis Citas', style: GoogleFonts.outfit(color: darkBlue, fontWeight: FontWeight.bold, fontSize: 18)),
            Text(widget.clinicaNombre, style: GoogleFonts.outfit(color: Colors.grey.shade500, fontSize: 12)),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh, color: primaryBlue),
            onPressed: () {
              setState(() => _isLoading = true);
              _loadCitas();
            },
          ),
        ],
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator(color: primaryBlue))
          : _error != null
              ? _buildError()
              : _citas.isEmpty
                  ? _buildEmpty()
                  : _buildCitasList(),
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
            Text('No se pudieron cargar las citas', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: darkBlue, fontSize: 18)),
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
            Icon(Icons.event_busy_rounded, size: 80, color: Colors.grey.shade300),
            const SizedBox(height: 24),
            Text('Sin citas registradas', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 20, color: darkBlue)),
            const SizedBox(height: 12),
            Text(
              'Aún no tienes citas agendadas en ${widget.clinicaNombre}.\nUsa "Programar Cita" para comenzar.',
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
      itemCount: _citas.length,
      itemBuilder: (context, index) {
        final cita = _citas[index];
        final fechaStr = cita['fecha_hora'] ?? '';
        final estado = cita['estado'] ?? 'PROGRAMADA';
        final psicologo = cita['psicologo_nombre'] ?? cita['psicologo'] ?? 'Psicólogo';
        final motivo = cita['motivo'] ?? '';
        final numeroFicha = cita['numero_ficha'] ?? 'FICHA-00000';
        final codigoQr = cita['codigo_qr'] ?? 'Sin QR';
        final citaId = cita['id'];

        DateTime? fecha;
        try { fecha = DateTime.parse(fechaStr).toLocal(); } catch (_) {}

        final bool esFutura = fecha != null && fecha.isAfter(DateTime.now());
        final countdown = esFutura ? _buildCountdown(fechaStr) : null;

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
                          if (motivo.isNotEmpty)
                            Text(motivo, style: GoogleFonts.outfit(color: Colors.grey.shade600, fontSize: 13), maxLines: 1, overflow: TextOverflow.ellipsis),
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
                const SizedBox(height: 14),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(10)),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (fecha != null) ...[
                              Row(
                                children: [
                                  const Icon(Icons.calendar_today, size: 15, color: Colors.grey),
                                  const SizedBox(width: 8),
                                  Expanded(child: Text(DateFormat("dd/MM/yyyy 'a las' HH:mm").format(fecha), style: GoogleFonts.outfit(fontWeight: FontWeight.w600, fontSize: 13, color: darkBlue))),
                                ],
                              ),
                              if (countdown != null) ...[
                                const SizedBox(height: 8),
                                Row(
                                  children: [
                                    Icon(Icons.timer_outlined, size: 15, color: primaryBlue),
                                    const SizedBox(width: 8),
                                    Text(countdown, style: GoogleFonts.outfit(color: primaryBlue, fontWeight: FontWeight.bold, fontSize: 13)),
                                  ],
                                ),
                              ],
                            ],
                          ],
                        ),
                      ),
                      // Código QR de la Ficha
                      Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(8)),
                        child: QrImageView(
                          data: codigoQr,
                          version: QrVersions.auto,
                          size: 60.0,
                          backgroundColor: Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
                if (esFutura && estado != 'CANCELADA' && estado != 'REALIZADA' && cita['estado_pago'] != 'PAGADO') ...[
                  const SizedBox(height: 14),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton(
                          onPressed: () => _confirmarCancelacion(citaId),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: Colors.red, side: const BorderSide(color: Colors.redAccent),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          child: Text('Cancelar', style: GoogleFonts.outfit(fontWeight: FontWeight.bold)),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => ChatbotScreen(
                                  token: widget.token,
                                  contextType: ChatbotContextType.cita,
                                  contextId: citaId,
                                  title: 'Sobre tu cita',
                                ),
                              ),
                            );
                          },
                          icon: const Icon(Icons.chat_bubble_outline, size: 16, color: Colors.white),
                          label: Text('Chatsito', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: Colors.white)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.teal.shade700,
                            elevation: 0,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                        ),
                      ),
                    ],
                  ),
                ]
              ],
            ),
          ),
        );
      },
    );
  }

  void _confirmarCancelacion(int citaId) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Cancelar Cita', style: GoogleFonts.outfit(color: Colors.red, fontWeight: FontWeight.bold)),
        content: Text(
          '¿Estás seguro de que deseas cancelar esta cita?\n\nRecuerda: No puedes cancelar citas faltando menos de 1 hora y tienes un límite de 2 cancelaciones diarias.',
          style: GoogleFonts.outfit(fontSize: 14),
        ),
        actions: [
          TextButton(
            child: Text('No, Volver', style: GoogleFonts.outfit(color: Colors.grey)),
            onPressed: () => Navigator.of(ctx).pop(),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: Text('Sí, Cancelar', style: GoogleFonts.outfit(color: Colors.white, fontWeight: FontWeight.bold)),
            onPressed: () async {
              Navigator.of(ctx).pop();
              setState(() => _isLoading = true);
              try {
                await CitaPagoService.cancelarCita(
                  token: widget.token,
                  citaId: citaId,
                );
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Cita cancelada con éxito.', style: GoogleFonts.outfit()), backgroundColor: Colors.green),
                );
                _loadCitas();
              } catch (e) {
                setState(() => _isLoading = false);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(e.toString(), style: GoogleFonts.outfit()), 
                    backgroundColor: Colors.red,
                    duration: const Duration(seconds: 4),
                  ),
                );
              }
            },
          ),
        ],
      ),
    );
  }
}

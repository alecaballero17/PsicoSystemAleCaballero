import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../services/notificacion_service.dart';
import 'package:intl/intl.dart';

class NotificacionesScreen extends StatefulWidget {
  final String token;
  const NotificacionesScreen({Key? key, required this.token}) : super(key: key);

  @override
  _NotificacionesScreenState createState() => _NotificacionesScreenState();
}

class _NotificacionesScreenState extends State<NotificacionesScreen> {
  List<dynamic> _notificaciones = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadNotificaciones();
  }

  Future<void> _loadNotificaciones() async {
    try {
      final notifs = await NotificacionService.getNotificaciones(widget.token);
      setState(() {
        _notificaciones = notifs;
        _isLoading = false;
      });
      _marcarComoLeidas();
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  Future<void> _marcarComoLeidas() async {
    try {
      await NotificacionService.marcarLeidas(widget.token);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF0F172A)),
        title: Text('Notificaciones', style: GoogleFonts.outfit(color: const Color(0xFF0F172A), fontWeight: FontWeight.bold)),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF2563EB)))
          : _error != null
              ? Center(child: Text(_error!))
              : _notificaciones.isEmpty
                  ? Center(child: Text('No tienes notificaciones.', style: GoogleFonts.outfit(color: Colors.grey, fontSize: 16)))
                  : ListView.builder(
                      padding: const EdgeInsets.all(16),
                      itemCount: _notificaciones.length,
                      itemBuilder: (context, index) {
                        final notif = _notificaciones[index];
                        final fecha = DateTime.parse(notif['fecha']).toLocal();
                        final isLeido = notif['leido'] ?? false;

                        return Container(
                          margin: const EdgeInsets.only(bottom: 12),
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: isLeido ? Colors.white : const Color(0xFFEFF6FF),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: Colors.grey.shade200),
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: Colors.blue.withOpacity(0.1),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(Icons.notifications_active, color: Color(0xFF2563EB), size: 20),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      notif['titulo'] ?? 'Aviso',
                                      style: GoogleFonts.outfit(
                                        fontWeight: isLeido ? FontWeight.w600 : FontWeight.bold,
                                        fontSize: 16,
                                        color: const Color(0xFF0F172A),
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      notif['mensaje'] ?? '',
                                      style: GoogleFonts.outfit(
                                        color: Colors.grey.shade700,
                                        fontSize: 14,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(
                                      DateFormat("dd MMM yyyy, HH:mm").format(fecha),
                                      style: GoogleFonts.outfit(
                                        color: Colors.grey.shade500,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
    );
  }
}

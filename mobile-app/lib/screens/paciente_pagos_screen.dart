import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:qr_flutter/qr_flutter.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:open_filex/open_filex.dart';
import '../services/cita_pago_service.dart';

class PacientePagosScreen extends StatefulWidget {
  final String token;
  const PacientePagosScreen({Key? key, required this.token}) : super(key: key);

  @override
  _PacientePagosScreenState createState() => _PacientePagosScreenState();
}

class _PacientePagosScreenState extends State<PacientePagosScreen> {
  final Color primaryBlue = const Color(0xFF2563EB);
  final Color darkBlue = const Color(0xFF0F172A);
  
  bool _isLoading = true;
  List<dynamic> _citas = [];
  String _filtroActual = 'TODOS';
  String _searchQuery = '';
  double _totalPendiente = 0.0;
  String? _error;

  final _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  bool _isProcessingVoice = false;

  String _tarjetaNumero = '';
  String _tarjetaFecha = '';
  String _tarjetaCvc = '';

  List<dynamic> get _citasFiltradas {
    return _citas.where((c) {
      final matchEstado = _filtroActual == 'TODOS' || (c['estado_pago'] ?? 'PENDIENTE').toString().toUpperCase() == _filtroActual;
      if (!matchEstado) return false;
      
      if (_searchQuery.isEmpty) return true;
      final query = _searchQuery.toLowerCase();
      final motivo = (c['motivo'] ?? '').toString().toLowerCase();
      final clinica = (c['clinica_nombre'] ?? '').toString().toLowerCase();
      
      return motivo.contains(query) || clinica.contains(query);
    }).toList();
  }

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }

  Future<void> _toggleRecording() async {
    try {
      if (await _audioRecorder.isRecording()) {
        final path = await _audioRecorder.stop();
        setState(() {
          _isRecording = false;
          _isProcessingVoice = true;
        });
        
        if (path != null) {
          _processAudioFile(path);
        } else {
          setState(() => _isProcessingVoice = false);
        }
      } else {
        if (await Permission.microphone.request().isGranted) {
          final tempDir = await getTemporaryDirectory();
          final path = '${tempDir.path}/report_audio.m4a';
          await _audioRecorder.start(
            const RecordConfig(encoder: AudioEncoder.aacLc),
            path: path,
          );
          setState(() {
            _isRecording = true;
          });
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Permiso de micrófono denegado.')),
          );
        }
      }
    } catch (e) {
      print('Error recording: $e');
      setState(() {
        _isRecording = false;
        _isProcessingVoice = false;
      });
    }
  }

  Future<void> _processAudioFile(String path) async {
    try {
      final text = await CitaPagoService.transcribeAudio(token: widget.token, filePath: path);
      setState(() => _isProcessingVoice = false);
      _mostrarEditorTexto(text);
    } catch (e) {
      setState(() => _isProcessingVoice = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al transcribir: $e'), backgroundColor: Colors.red),
      );
    }
  }

  void _mostrarEditorTexto(String textoInicial) {
    final controller = TextEditingController(text: textoInicial);
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Revisar Transcripción', style: GoogleFonts.outfit(fontWeight: FontWeight.bold)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Corrige cualquier error antes de solicitar el reporte:', style: GoogleFonts.outfit(fontSize: 14)),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              maxLines: 4,
              decoration: InputDecoration(
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            child: Text('Cancelar', style: GoogleFonts.outfit(color: Colors.grey)),
            onPressed: () => Navigator.pop(ctx),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: primaryBlue),
            child: Text('Generar Reporte', style: GoogleFonts.outfit(color: Colors.white)),
            onPressed: () {
              Navigator.pop(ctx);
              _solicitarReporte(controller.text);
            },
          ),
        ],
      ),
    );
  }

  Future<void> _solicitarReporte(String texto) async {
    setState(() => _isProcessingVoice = true);
    try {
      final res = await CitaPagoService.generarReporte(token: widget.token, transcript: texto);
      setState(() => _isProcessingVoice = false);
      _mostrarBotonesDescarga(res['pdf_base64'], res['excel_base64']);
    } catch (e) {
      setState(() => _isProcessingVoice = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al generar: $e'), backgroundColor: Colors.red),
      );
    }
  }

  void _mostrarBotonesDescarga(String? pdfBase64, String? excelBase64) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Reporte Generado', style: GoogleFonts.outfit(fontWeight: FontWeight.bold)),
        content: Text('Tus reportes por filtros de voz están listos.', style: GoogleFonts.outfit()),
        actionsAlignment: MainAxisAlignment.center,
        actions: [
          if (pdfBase64 != null)
            ElevatedButton.icon(
              icon: const Icon(Icons.picture_as_pdf, color: Colors.white),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
              label: Text('Abrir PDF', style: GoogleFonts.outfit(color: Colors.white)),
              onPressed: () => _guardarYAbrirArchivo(pdfBase64, 'reporte.pdf'),
            ),
          if (excelBase64 != null)
            ElevatedButton.icon(
              icon: const Icon(Icons.table_chart, color: Colors.white),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
              label: Text('Abrir Excel', style: GoogleFonts.outfit(color: Colors.white)),
              onPressed: () => _guardarYAbrirArchivo(excelBase64, 'reporte.xlsx'),
            ),
        ],
      ),
    );
  }

  Future<void> _guardarYAbrirArchivo(String base64Str, String filename) async {
    try {
      final bytes = base64.decode(base64Str);
      final dir = await getApplicationDocumentsDirectory();
      final file = File('${dir.path}/$filename');
      await file.writeAsBytes(bytes);
      
      final _localNotifications = FlutterLocalNotificationsPlugin();
      await _localNotifications.show(
        id: DateTime.now().millisecond,
        title: 'Reporte Listo',
        body: 'Aquí está tu reporte generado ($filename)',
        notificationDetails: const NotificationDetails(
          android: AndroidNotificationDetails(
            'high_importance_channel',
            'High Importance Notifications',
            importance: Importance.max,
            priority: Priority.high,
            icon: '@mipmap/ic_launcher',
          ),
        ),
      );
      
      await OpenFilex.open(file.path);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al abrir el archivo: $e')),
      );
    }
  }

  Future<void> _loadData() async {
    try {
      final data = await CitaPagoService.getHistorial(widget.token);
      final citas = data['citas'] ?? data['results'] ?? data;
      final lista = citas is List ? citas : [];
      double pendiente = 0.0;
      for (final c in lista) {
        if ((c['estado_pago'] ?? '') == 'PENDIENTE') {
          pendiente += double.tryParse(c['monto']?.toString() ?? '0') ?? 0;
        }
      }
      setState(() {
        _citas = lista;
        _totalPendiente = pendiente;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString().replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  String _generarReporteHTML() {
    final now = DateFormat("dd/MM/yyyy HH:mm").format(DateTime.now());
    final filas = _citas.isEmpty
        ? '<tr><td colspan="5" style="text-align:center;color:#999;padding:24px;">Sin registros de pagos aún</td></tr>'
        : _citas.map((c) {
            final fecha = c['fecha_hora'] != null
                ? DateFormat("dd/MM/yyyy HH:mm").format(DateTime.parse(c['fecha_hora']).toLocal())
                : '-';
            final psi = c['psicologo_nombre'] ?? c['psicologo'] ?? '-';
            final motivo = c['motivo'] ?? '-';
            final monto = '\$${c['monto'] ?? '0.00'}';
            final estado = c['estado_pago'] ?? 'PENDIENTE';
            final color = estado == 'PAGADO' ? '#10b981' : '#f59e0b';
            return '<tr><td>$fecha</td><td>$psi</td><td>$motivo</td><td>$monto</td><td style="color:$color;font-weight:bold;">$estado</td></tr>';
          }).join('\n');

    return '''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Reporte de Pagos — PsicoSystem</title>
  <style>
    body{font-family:Inter,sans-serif;background:#f8fafc;margin:0;padding:24px;color:#0f172a;}
    h1{color:#2563eb;font-size:22px;margin-bottom:4px;}
    .subtitle{color:#64748b;font-size:13px;margin-bottom:24px;}
    .badge{display:inline-block;background:#fee2e2;color:#dc2626;border-radius:8px;padding:10px 20px;font-size:20px;font-weight:bold;margin-bottom:24px;}
    table{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.06);}
    th{background:#2563eb;color:#fff;padding:12px 16px;text-align:left;font-size:13px;}
    td{padding:12px 16px;border-bottom:1px solid #f1f5f9;font-size:13px;}
    tr:last-child td{border-bottom:none;}
    .footer{margin-top:24px;color:#94a3b8;font-size:11px;text-align:center;}
  </style>
</head>
<body>
  <h1>📋 Reporte de Pagos y Citas</h1>
  <div class="subtitle">Generado el $now — PsicoSystem</div>
  <div class="badge">💰 Saldo Pendiente: \$$_totalPendiente</div>
  <table>
    <thead>
      <tr><th>Fecha y Hora</th><th>Psicólogo</th><th>Motivo</th><th>Monto</th><th>Estado Pago</th></tr>
    </thead>
    <tbody>$filas</tbody>
  </table>
  <div class="footer">PsicoSystem &copy; 2026 — Documento generado automáticamente</div>
</body>
</html>''';
  }

  void _mostrarReporte() {
    final html = _generarReporteHTML();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(children: [
          Icon(Icons.description, color: primaryBlue),
          const SizedBox(width: 10),
          Text('Reporte HTML', style: GoogleFonts.outfit(fontWeight: FontWeight.bold)),
        ]),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('El reporte está listo. Copia el contenido HTML para abrirlo en tu navegador.', style: GoogleFonts.outfit(fontSize: 13, color: Colors.grey.shade600)),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(8), border: Border.all(color: Colors.grey.shade200)),
                child: SelectableText(html, style: const TextStyle(fontFamily: 'monospace', fontSize: 11)),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(child: Text('Cerrar', style: GoogleFonts.outfit(color: Colors.grey)), onPressed: () => Navigator.of(ctx).pop()),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        title: Text('Historial de Pagos', style: GoogleFonts.outfit(color: Colors.black87, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: Icon(Icons.picture_as_pdf, color: primaryBlue),
            tooltip: 'Exportar Reporte',
            onPressed: _mostrarReporte,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        backgroundColor: _isRecording ? Colors.red : primaryBlue,
        onPressed: _isProcessingVoice ? null : _toggleRecording,
        child: _isProcessingVoice 
            ? const CircularProgressIndicator(color: Colors.white)
            : Icon(_isRecording ? Icons.stop : Icons.mic, color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextField(
              decoration: InputDecoration(
                hintText: 'Buscar por motivo o clínica...',
                prefixIcon: const Icon(Icons.search),
                filled: true,
                fillColor: Colors.grey.shade100,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              ),
              onChanged: (val) {
                setState(() => _searchQuery = val);
              },
            ),
            const SizedBox(height: 16),
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: ['TODOS', 'PENDIENTE', 'PAGADO', 'CANCELADO'].map((filtro) {
                  return Padding(
                    padding: const EdgeInsets.only(right: 8.0),
                    child: ChoiceChip(
                      label: Text(filtro, style: GoogleFonts.outfit(fontSize: 12, fontWeight: FontWeight.bold)),
                      selected: _filtroActual == filtro,
                      selectedColor: primaryBlue.withOpacity(0.2),
                      onSelected: (selected) {
                        if (selected) setState(() => _filtroActual = filtro);
                      },
                    ),
                  );
                }).toList(),
              ),
            ),
            const SizedBox(height: 16),
            Text('Historial Reciente', style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, color: const Color(0xFF0F172A))),
            const SizedBox(height: 16),
            if (_isLoading)
              const Center(child: CircularProgressIndicator())
            else if (_citasFiltradas.isEmpty)
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Text('Aún no hay datos de pagos que coincidan.', style: GoogleFonts.outfit(color: Colors.grey)),
              )
            else
              ..._citasFiltradas.map((c) {
                final pagado = (c['estado_pago'] ?? '') == 'PAGADO';
                final fecha = c['fecha_hora'] != null
                    ? DateFormat("dd MMM yyyy HH:mm").format(DateTime.parse(c['fecha_hora']).toLocal())
                    : '-';
                return _buildPagoItem(c, c['motivo'] ?? 'Consulta', fecha, '\$${c['monto'] ?? "0.00"}', pagado);
              }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildPagoItem(dynamic citaData, String concepto, String fecha, String monto, bool pagado) {
    final clinica = citaData['clinica_nombre'] ?? 'Sin Clínica';
    final psicologo = citaData['psicologo_nombre'] ?? 'Sin Psicólogo';
    final numeroFicha = citaData['numero_ficha'] ?? 'N/A';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(color: pagado ? Colors.green.shade50 : Colors.orange.shade50, borderRadius: BorderRadius.circular(10)),
            child: Icon(pagado ? Icons.check_circle : Icons.access_time, color: pagado ? Colors.green : Colors.orange),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(concepto, style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 16)),
                const SizedBox(height: 4),
                Text('Clínica: $clinica', style: GoogleFonts.outfit(fontSize: 13, color: Colors.grey.shade700)),
                Text('Psicólogo: $psicologo', style: GoogleFonts.outfit(fontSize: 13, color: Colors.grey.shade700)),
                Text('Ficha N°: $numeroFicha', style: GoogleFonts.outfit(fontSize: 13, color: primaryBlue, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(fecha, style: GoogleFonts.outfit(color: Colors.grey.shade500, fontSize: 12)),
                if (!pagado) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      ElevatedButton(
                        onPressed: () => _simularPago(context, citaData),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: primaryBlue,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        child: Text('Pagar Ahora', style: GoogleFonts.outfit(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                      ),
                      const SizedBox(width: 8),
                      OutlinedButton(
                        onPressed: () => _cancelarCita(context, citaData),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Colors.red,
                          side: const BorderSide(color: Colors.red),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        child: Text('Cancelar', style: GoogleFonts.outfit(fontSize: 12, fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                ]
              ],
            ),
          ),
          Text(monto, style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 16, color: pagado ? Colors.green : Colors.orange)),
        ],
      ),
    );
  }

  void _simularPago(BuildContext context, dynamic citaData) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
      builder: (ctx) {
        return _PagoModal(
          citaData: citaData,
          onConfirmarPago: (metodo) {
            Navigator.of(ctx).pop();
            _procesarPago(citaData['id'], metodo);
          },
        );
      },
    );
  }

  Future<void> _procesarPago(int citaId, String metodo) async {
    // Mostrar validación
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (c) => AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text('Validando pago en la clínica...', style: GoogleFonts.outfit()),
          ],
        ),
      ),
    );

    // Simulamos un retraso para que se vea el proceso de validación
    await Future.delayed(const Duration(seconds: 3));

    try {
      await CitaPagoService.pagarCita(
        token: widget.token,
        citaId: citaId,
        metodoPago: metodo,
      );

      if (mounted) Navigator.of(context).pop(); // Cerrar carga

      if (mounted) {
        showDialog(
          context: context,
          builder: (c) => AlertDialog(
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.check_circle, color: Colors.green, size: 60),
                const SizedBox(height: 16),
                Text('Pago Exitoso', style: GoogleFonts.outfit(fontSize: 20, fontWeight: FontWeight.bold)),
              ],
            ),
            actions: [
              TextButton(
                onPressed: () {
                  Navigator.of(c).pop();
                  setState(() => _isLoading = true);
                  _loadData();
                },
                child: Text('Aceptar', style: GoogleFonts.outfit(color: primaryBlue, fontWeight: FontWeight.bold)),
              )
            ],
          ),
        );
      }
    } catch (e) {
      if (mounted) Navigator.of(context).pop(); // Cerrar carga
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al procesar el pago: $e', style: GoogleFonts.outfit()), backgroundColor: Colors.red),
        );
      }
    }
  }

  void _cancelarCita(BuildContext context, dynamic citaData) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Cancelar Cita', style: GoogleFonts.outfit(color: Colors.red, fontWeight: FontWeight.bold)),
        content: Text('¿Estás seguro de cancelar esta cita? Recuerda que no se puede cancelar faltando menos de 1 hora.', style: GoogleFonts.outfit()),
        actions: [
          TextButton(
            child: Text('No, Mantener', style: GoogleFonts.outfit(color: Colors.grey)),
            onPressed: () => Navigator.of(ctx).pop(),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: Text('Sí, Cancelar', style: GoogleFonts.outfit(color: Colors.white)),
            onPressed: () async {
              Navigator.of(ctx).pop();
              setState(() => _isLoading = true);
              try {
                await CitaPagoService.cancelarCita(token: widget.token, citaId: citaData['id']);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Cita cancelada con éxito.', style: GoogleFonts.outfit()), backgroundColor: Colors.green),
                );
                _loadData();
              } catch (e) {
                setState(() => _isLoading = false);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Error al cancelar: $e', style: GoogleFonts.outfit()), backgroundColor: Colors.red),
                );
              }
            },
          ),
        ],
      ),
    );
  }
}

class _PagoModal extends StatefulWidget {
  final dynamic citaData;
  final Function(String) onConfirmarPago;
  
  const _PagoModal({required this.citaData, required this.onConfirmarPago});

  @override
  _PagoModalState createState() => _PagoModalState();
}

class _PagoModalState extends State<_PagoModal> {
  String metodoSeleccionado = '';
  String tarjetaNumero = '';
  String tarjetaFecha = '';
  String tarjetaCvc = '';
  
  final primaryBlue = const Color(0xFF2563EB);
  final darkBlue = const Color(0xFF0F172A);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        bottom: MediaQuery.of(context).viewInsets.bottom + 24,
        left: 24, right: 24, top: 24
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Container(
            width: 40, height: 4,
            margin: const EdgeInsets.only(bottom: 20),
            decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2)),
          ),
          Text('Completar Pago', style: GoogleFonts.outfit(color: darkBlue, fontWeight: FontWeight.bold, fontSize: 22)),
          const SizedBox(height: 8),
          Text('Monto a cancelar: \$${widget.citaData['monto'] ?? "120.00"}', style: GoogleFonts.outfit(fontSize: 16, color: Colors.grey.shade700)),
          const SizedBox(height: 24),
          
          if (metodoSeleccionado == '') ...[
            Text('Selecciona un método de pago:', style: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            ListTile(
              leading: Icon(Icons.qr_code_scanner, color: primaryBlue),
              title: Text('Pago Rápido QR', style: GoogleFonts.outfit(fontWeight: FontWeight.bold)),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: Colors.grey.shade200)),
              onTap: () => setState(() => metodoSeleccionado = 'QR'),
            ),
            const SizedBox(height: 12),
            ListTile(
              leading: Icon(Icons.credit_card, color: primaryBlue),
              title: Text('Pago con Tarjeta', style: GoogleFonts.outfit(fontWeight: FontWeight.bold)),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: Colors.grey.shade200)),
              onTap: () => setState(() => metodoSeleccionado = 'TARJETA'),
            ),
          ] else if (metodoSeleccionado == 'QR') ...[
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.arrow_back),
                  onPressed: () => setState(() => metodoSeleccionado = ''),
                ),
                Text('Pago con QR', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 18)),
              ],
            ),
            const SizedBox(height: 16),
            QrImageView(
              data: "PAGO_CITA_${widget.citaData['id']}_${widget.citaData['monto'] ?? '120'}",
              version: QrVersions.auto,
              size: 180.0,
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: primaryBlue, padding: const EdgeInsets.symmetric(vertical: 16)),
                onPressed: () => widget.onConfirmarPago('QR'),
                child: Text('Confirmar Pago', style: GoogleFonts.outfit(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),
          ] else if (metodoSeleccionado == 'TARJETA') ...[
            Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.arrow_back),
                  onPressed: () => setState(() => metodoSeleccionado = ''),
                ),
                Text('Datos de Tarjeta', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 18)),
              ],
            ),
            const SizedBox(height: 16),
            TextFormField(
              decoration: InputDecoration(
                labelText: 'Número de Tarjeta',
                prefixIcon: const Icon(Icons.credit_card),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
              keyboardType: TextInputType.number,
              onChanged: (v) => tarjetaNumero = v,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: TextFormField(
                  decoration: InputDecoration(labelText: 'MM/YY', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
                  keyboardType: TextInputType.number,
                  inputFormatters: [
                    FilteringTextInputFormatter.digitsOnly,
                    LengthLimitingTextInputFormatter(4),
                    ExpirationDateFormatter(),
                  ],
                  onChanged: (v) => tarjetaFecha = v,
                )),
                const SizedBox(width: 12),
                Expanded(child: TextFormField(
                  decoration: InputDecoration(labelText: 'CVC', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12))),
                  onChanged: (v) => tarjetaCvc = v,
                )),
              ],
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: darkBlue, padding: const EdgeInsets.symmetric(vertical: 16)),
                onPressed: () {
                  if (tarjetaNumero.length < 15 || tarjetaFecha.isEmpty || tarjetaCvc.isEmpty) {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Por favor llena los datos de la tarjeta correctamente')));
                    return;
                  }
                  widget.onConfirmarPago('TARJETA');
                },
                child: Text('Confirmar Pago', style: GoogleFonts.outfit(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class ExpirationDateFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
      TextEditingValue oldValue, TextEditingValue newValue) {
    var text = newValue.text;
    if (newValue.selection.baseOffset == 0) {
      return newValue;
    }
    var buffer = StringBuffer();
    for (int i = 0; i < text.length; i++) {
      buffer.write(text[i]);
      var nonZeroIndex = i + 1;
      if (nonZeroIndex % 2 == 0 && nonZeroIndex != text.length) {
        buffer.write('/');
      }
    }
    var string = buffer.toString();
    return newValue.copyWith(
        text: string,
        selection: TextSelection.collapsed(offset: string.length));
  }
}

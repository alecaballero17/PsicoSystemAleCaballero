import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/recomendacion_service.dart';

class RecomendacionesScreen extends StatefulWidget {
  final String token;
  const RecomendacionesScreen({Key? key, required this.token}) : super(key: key);

  @override
  _RecomendacionesScreenState createState() => _RecomendacionesScreenState();
}

class _RecomendacionesScreenState extends State<RecomendacionesScreen> {
  List<dynamic> recomendaciones = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchRecomendaciones();
  }

  Future<void> _fetchRecomendaciones() async {
    setState(() => isLoading = true);
    try {
      final data = await RecomendacionService.getRecomendaciones(widget.token);
      setState(() {
        recomendaciones = data;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cargar recomendaciones')),
      );
    } finally {
      setState(() => isLoading = false);
    }
  }

  Future<void> _updateEstado(int id, String estado) async {
    try {
      await RecomendacionService.updateEstadoRecomendacion(widget.token, id, estado);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Estado actualizado')),
      );
      _fetchRecomendaciones();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al actualizar estado')),
      );
    }
  }

  String _formatDate(String isoDate) {
    if (isoDate.isEmpty) return 'Desconocida';
    try {
      final dt = DateTime.parse(isoDate).toLocal();
      return DateFormat('dd/MM/yyyy HH:mm').format(dt);
    } catch (e) {
      return isoDate;
    }
  }

  Color _getColorForEstado(String estado) {
    switch (estado) {
      case 'PENDIENTE':
        return Colors.orange;
      case 'EN_PROGRESO':
        return Colors.blue;
      case 'COMPLETADO':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF1F5F9),
      appBar: AppBar(
        title: const Text('Mis Recomendaciones'),
        backgroundColor: const Color(0xFF1E3A8A),
        foregroundColor: Colors.white,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : recomendaciones.isEmpty
              ? _buildEmptyState()
              : RefreshIndicator(
                  onRefresh: _fetchRecomendaciones,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: recomendaciones.length,
                    itemBuilder: (context, index) {
                      final r = recomendaciones[index];
                      return _buildRecomendacionCard(r);
                    },
                  ),
                ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.check_circle_outline, size: 80, color: Colors.grey),
          const SizedBox(height: 16),
          const Text(
            'Sin recomendaciones',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.grey),
          ),
          const SizedBox(height: 8),
          const Text(
            'Tu psicólogo no te ha asignado tareas.',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildRecomendacionCard(Map<String, dynamic> r) {
    return Card(
      elevation: 3,
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.lightbulb, color: Colors.amber, size: 28),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Recomendación Clínica',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Color(0xFF1E3A8A)),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getColorForEstado(r['estado']).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: _getColorForEstado(r['estado'])),
                  ),
                  child: Text(
                    r['estado'],
                    style: TextStyle(
                      color: _getColorForEstado(r['estado']),
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
            const Divider(height: 24),
            Row(
              children: [
                const Icon(Icons.person, size: 16, color: Colors.grey),
                const SizedBox(width: 4),
                Text('Psicólogo: ${r['psicologo_nombre']}', style: const TextStyle(color: Colors.black87)),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.business, size: 16, color: Colors.grey),
                const SizedBox(width: 4),
                Text('Clínica: ${r['clinica_nombre']}', style: const TextStyle(color: Colors.black87)),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(Icons.calendar_today, size: 16, color: Colors.grey),
                const SizedBox(width: 4),
                Text('Sesión: ${_formatDate(r['fecha_sesion'] ?? r['fecha_creacion'])}', style: const TextStyle(color: Colors.black87)),
              ],
            ),
            const SizedBox(height: 16),
            const Text('Indicaciones:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.black87)),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFF8FAFC),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: const Color(0xFFE2E8F0)),
              ),
              child: Text(
                r['texto'] ?? '',
                style: const TextStyle(fontSize: 15, color: Colors.black87, height: 1.4),
              ),
            ),
            const SizedBox(height: 16),
            const Text('Actualizar estado:', style: TextStyle(fontWeight: FontWeight.w600, color: Colors.grey, fontSize: 13)),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildEstadoButton(r, 'PENDIENTE', 'Pendiente', Icons.schedule),
                _buildEstadoButton(r, 'EN_PROGRESO', 'En Progreso', Icons.trending_up),
                _buildEstadoButton(r, 'COMPLETADO', 'Completado', Icons.check_circle),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEstadoButton(Map<String, dynamic> r, String targetEstado, String label, IconData icon) {
    bool isSelected = r['estado'] == targetEstado;
    Color color = _getColorForEstado(targetEstado);
    
    return InkWell(
      onTap: () {
        if (!isSelected) {
          _updateEstado(r['id'], targetEstado);
        }
      },
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? color : Colors.transparent,
          border: Border.all(color: color),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Icon(icon, size: 20, color: isSelected ? Colors.white : color),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected ? Colors.white : color,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

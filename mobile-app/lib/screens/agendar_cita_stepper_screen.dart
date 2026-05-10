import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../models/user_model.dart';

class AgendarCitaStepperScreen extends StatefulWidget {
  final User user;
  final String token;
  final String clinicaSeleccionada;

  const AgendarCitaStepperScreen({
    super.key, 
    required this.user, 
    required this.token,
    required this.clinicaSeleccionada,
  });

  @override
  _AgendarCitaStepperScreenState createState() => _AgendarCitaStepperScreenState();
}

class _AgendarCitaStepperScreenState extends State<AgendarCitaStepperScreen> {
  int _currentStep = 0;
  bool _isLoading = false;

  final Color primaryBlue = const Color(0xFF2563EB);
  final Color darkBlue = const Color(0xFF0F172A);
  final Color bgGrey = const Color(0xFFF8FAFC);

  // Datos
  String? _selectedPsicologo;
  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  String? _selectedTime;
  int? _createdCitaId;

  final List<String> _psicologos = ['Lic. Juan Pérez (Terapia Cognitiva)', 'Lic. María Gómez (Parejas)', 'Lic. Carlos Ruiz (Infantil)'];
  final List<String> _horasManana = ['08:30', '09:15', '10:30', '10:45', '11:00', '11:15', '11:30', '11:45'];
  final List<String> _horasTarde = ['12:00', '12:15', '13:00', '13:15', '13:30', '14:15', '14:30', '14:45', '15:00', '15:15', '15:30', '15:45', '16:00', '16:15'];

  final List<String> _stepTitles = ['Especialista', 'Datos', 'Fecha', 'Hora', 'Confirmar'];

  void _nextStep() {
    if (_currentStep < 3) {
      setState(() => _currentStep += 1);
    } else if (_currentStep == 3) {
      _confirmarCita();
    }
  }

  void _prevStep() {
    if (_currentStep > 0) {
      setState(() => _currentStep -= 1);
    }
  }

  Future<void> _confirmarCita() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 2)); // Simulación
    setState(() {
      _isLoading = false;
      _createdCitaId = 1444476;
      _currentStep = 4;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: bgGrey,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        title: Text('Programar Cita', style: GoogleFonts.outfit(color: darkBlue, fontWeight: FontWeight.bold, fontSize: 18)),
        leading: IconButton(
          icon: Icon(Icons.arrow_back_ios_new, color: darkBlue, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: _isLoading
          ? Center(child: CircularProgressIndicator(color: primaryBlue))
          : Column(
              children: [
                _buildStepperHeader(),
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(20.0),
                    child: _currentStep == 4 ? _buildSuccessStep() : _buildCurrentStepContent(),
                  ),
                ),
                if (_currentStep < 4) _buildBottomControls(),
              ],
            ),
    );
  }

  Widget _buildStepperHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: List.generate(5, (index) {
          bool isCompleted = index < _currentStep;
          bool isActive = index == _currentStep;
          
          return Expanded(
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    children: [
                      AnimatedContainer(
                        duration: const Duration(milliseconds: 300),
                        width: isActive ? 32 : 28,
                        height: isActive ? 32 : 28,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: isCompleted ? const Color(0xFF10B981) : (isActive ? primaryBlue : Colors.grey.shade200),
                          boxShadow: isActive ? [BoxShadow(color: primaryBlue.withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 2))] : [],
                        ),
                        child: Center(
                          child: isCompleted
                              ? const Icon(Icons.check, color: Colors.white, size: 16)
                              : Text(
                                  '${index + 1}',
                                  style: GoogleFonts.outfit(
                                    color: (isActive) ? Colors.white : Colors.grey.shade600,
                                    fontWeight: FontWeight.bold,
                                    fontSize: isActive ? 14 : 12,
                                  ),
                                ),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _stepTitles[index],
                        maxLines: 1,
                        overflow: TextOverflow.visible,
                        style: GoogleFonts.outfit(
                          fontSize: 10,
                          fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                          color: (isCompleted || isActive) ? darkBlue : Colors.grey.shade500,
                        ),
                      ),
                    ],
                  ),
                ),
                if (index < 4)
                  Container(
                    width: 20,
                    height: 2,
                    color: isCompleted ? const Color(0xFF10B981) : Colors.grey.shade200,
                  ),
              ],
            ),
          );
        }),
      ),
    );
  }

  Widget _buildCurrentStepContent() {
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white, 
        borderRadius: BorderRadius.circular(20), 
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 20)],
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_currentStep == 0) ...[
            Text('Selecciona un Especialista', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 18, color: darkBlue)),
            const SizedBox(height: 16),
            ..._psicologos.map((p) => Container(
              margin: const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                border: Border.all(color: _selectedPsicologo == p ? primaryBlue : Colors.grey.shade200, width: _selectedPsicologo == p ? 2 : 1),
                borderRadius: BorderRadius.circular(12),
                color: _selectedPsicologo == p ? primaryBlue.withOpacity(0.05) : Colors.transparent,
              ),
              child: RadioListTile<String>(
                title: Text(p, style: GoogleFonts.outfit(fontWeight: FontWeight.w500)),
                value: p,
                activeColor: primaryBlue,
                groupValue: _selectedPsicologo,
                onChanged: (val) => setState(() => _selectedPsicologo = val),
              ),
            )),
          ],
          if (_currentStep == 1) ...[
            Text('Datos del Paciente', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 18, color: darkBlue)),
            const SizedBox(height: 24),
            _buildDataRow('Tipo de documento', 'CI'),
            _buildDataRow('Nro de documento', widget.user.username.split('@').first), 
            _buildDataRow('Nombre Completo', widget.user.username),
            _buildDataRow('Correo Electrónico', widget.user.email),
            const SizedBox(height: 24),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(color: const Color(0xFFFEF2F2), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFFECACA))),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444)),
                  const SizedBox(width: 12),
                  Expanded(child: Text('Las cancelaciones reiteradas restringirán su acceso. Su cita será cancelada si no se presenta a tiempo.', style: GoogleFonts.outfit(color: const Color(0xFF991B1B), fontSize: 12))),
                ],
              ),
            ),
          ],
          if (_currentStep == 2) ...[
            Text('Selecciona la fecha', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 18, color: darkBlue)),
            const SizedBox(height: 24),
            InkWell(
              onTap: () async {
                final date = await showDatePicker(
                  context: context,
                  initialDate: _selectedDate,
                  firstDate: DateTime.now(),
                  lastDate: DateTime.now().add(const Duration(days: 30)),
                  builder: (context, child) {
                    return Theme(
                      data: Theme.of(context).copyWith(colorScheme: ColorScheme.light(primary: primaryBlue)),
                      child: child!,
                    );
                  },
                );
                if (date != null) setState(() => _selectedDate = date);
              },
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  border: Border.all(color: primaryBlue.withOpacity(0.5)),
                  borderRadius: BorderRadius.circular(16),
                  color: primaryBlue.withOpacity(0.05),
                ),
                child: Row(
                  children: [
                    Container(padding: const EdgeInsets.all(10), decoration: BoxDecoration(color: primaryBlue, borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.calendar_month, color: Colors.white)),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Fecha seleccionada', style: GoogleFonts.outfit(color: Colors.grey.shade600, fontSize: 12)),
                          Text(DateFormat('EEEE, d MMMM yyyy', 'es').format(_selectedDate).toUpperCase(), style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: darkBlue, fontSize: 14)),
                        ],
                      ),
                    ),
                    Icon(Icons.edit, color: primaryBlue, size: 20),
                  ],
                ),
              ),
            )
          ],
          if (_currentStep == 3) ...[
            Text('Disponibilidad', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 18, color: darkBlue)),
            Text(DateFormat('EEEE, d MMMM', 'es').format(_selectedDate), style: GoogleFonts.outfit(color: Colors.grey.shade600)),
            const SizedBox(height: 24),
            Row(children: [const Icon(Icons.wb_twilight, color: Color(0xFFF59E0B), size: 18), const SizedBox(width: 8), Text('TURNO MAÑANA', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: Colors.grey.shade500, fontSize: 12))]),
            const SizedBox(height: 12),
            Wrap(spacing: 10, runSpacing: 10, children: _horasManana.map((h) => _buildTimeBtn(h)).toList()),
            const SizedBox(height: 32),
            Row(children: [const Icon(Icons.wb_sunny, color: Color(0xFFF59E0B), size: 18), const SizedBox(width: 8), Text('TURNO TARDE', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: Colors.grey.shade500, fontSize: 12))]),
            const SizedBox(height: 12),
            Wrap(spacing: 10, runSpacing: 10, children: _horasTarde.map((h) => _buildTimeBtn(h)).toList()),
          ],
        ],
      ),
    );
  }

  Widget _buildTimeBtn(String time) {
    bool isSelected = _selectedTime == time;
    return InkWell(
      onTap: () => setState(() => _selectedTime = time),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 75,
        padding: const EdgeInsets.symmetric(vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? primaryBlue : Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: isSelected ? primaryBlue : Colors.grey.shade300),
          boxShadow: isSelected ? [BoxShadow(color: primaryBlue.withOpacity(0.3), blurRadius: 8, offset: const Offset(0, 4))] : [],
        ),
        child: Center(
          child: Text(
            time,
            style: GoogleFonts.outfit(color: isSelected ? Colors.white : darkBlue, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }

  Widget _buildDataRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: GoogleFonts.outfit(color: Colors.grey.shade500, fontSize: 12, fontWeight: FontWeight.w500)),
          const SizedBox(height: 4),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            decoration: BoxDecoration(color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(10)),
            child: Text(value, style: GoogleFonts.outfit(fontWeight: FontWeight.w600, color: darkBlue, fontSize: 15)),
          )
        ],
      ),
    );
  }

  Widget _buildBottomControls() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, -5))]),
      child: Row(
        children: [
          Expanded(
            flex: 1,
            child: OutlinedButton(
              onPressed: _prevStep,
              style: OutlinedButton.styleFrom(
                side: BorderSide(color: Colors.grey.shade300),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: Text('Atrás', style: GoogleFonts.outfit(color: Colors.grey.shade700, fontWeight: FontWeight.bold)),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            flex: 2,
            child: ElevatedButton(
              onPressed: _nextStep,
              style: ElevatedButton.styleFrom(
                backgroundColor: primaryBlue,
                elevation: 0,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: Text(_currentStep == 3 ? 'Confirmar Cita' : 'Siguiente Paso', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 16)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessStep() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(color: const Color(0xFF10B981).withOpacity(0.1), shape: BoxShape.circle),
          child: const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 60),
        ),
        const SizedBox(height: 20),
        Text('¡Cita Confirmada!', style: GoogleFonts.outfit(fontSize: 24, fontWeight: FontWeight.bold, color: darkBlue)),
        Text('Te esperamos en el consultorio.', style: GoogleFonts.outfit(color: Colors.grey.shade600)),
        const SizedBox(height: 32),

        // Ticket Box
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 20, offset: const Offset(0, 10))],
          ),
          child: Column(
            children: [
              // Ticket Header
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(color: darkBlue, borderRadius: const BorderRadius.vertical(top: Radius.circular(24))),
                child: Column(
                  children: [
                    Text('TICKET DE ATENCIÓN', style: GoogleFonts.outfit(color: Colors.white70, letterSpacing: 2, fontSize: 10, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text('#$_createdCitaId', style: GoogleFonts.outfit(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
              // QR Area
              Container(
                padding: const EdgeInsets.all(24),
                child: Column(
                  children: [
                    QrImageView(data: 'PSICOSYSTEM_CITA:$_createdCitaId', size: 160, foregroundColor: darkBlue),
                    const SizedBox(height: 20),
                    const Divider(),
                    const SizedBox(height: 16),
                    _buildTicketRow('Paciente', widget.user.username),
                    const SizedBox(height: 12),
                    _buildTicketRow('Fecha', DateFormat('dd/MM/yyyy').format(_selectedDate)),
                    const SizedBox(height: 12),
                    _buildTicketRow('Hora', _selectedTime ?? "00:00"),
                    const SizedBox(height: 12),
                    _buildTicketRow('Ubicación', widget.clinicaSeleccionada),
                  ],
                ),
              )
            ],
          ),
        ),
        const SizedBox(height: 32),
        
        // Requisitos Medicos
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(16)),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.info_outline, color: primaryBlue, size: 20),
                  const SizedBox(width: 8),
                  Text('Indicaciones Importantes', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: darkBlue)),
                ],
              ),
              const SizedBox(height: 12),
              _buildReqItem('Llegar 15 minutos antes de la hora programada.'),
              _buildReqItem('Presentar este código QR en recepción.'),
              _buildReqItem('En caso de retraso mayor a 10 min, la cita se cancelará.'),
            ],
          ),
        ),
        const SizedBox(height: 32),
        
        // Botones Finales
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            icon: const Icon(Icons.picture_as_pdf, color: Colors.white, size: 20),
            style: ElevatedButton.styleFrom(backgroundColor: primaryBlue, padding: const EdgeInsets.symmetric(vertical: 16), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
            onPressed: () {},
            label: Text('Descargar Comprobante PDF', style: GoogleFonts.outfit(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
          ),
        ),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Volver al Inicio', style: GoogleFonts.outfit(color: Colors.grey.shade600, fontWeight: FontWeight.bold)),
          ),
        ),
        const SizedBox(height: 40),
      ],
    );
  }

  Widget _buildReqItem(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('• ', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold)),
          Expanded(child: Text(text, style: GoogleFonts.outfit(fontSize: 13, color: Colors.black87))),
        ],
      ),
    );
  }

  Widget _buildTicketRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: GoogleFonts.outfit(color: Colors.grey.shade500, fontSize: 13)),
        const SizedBox(width: 20),
        Expanded(child: Text(value, textAlign: TextAlign.right, style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: darkBlue, fontSize: 13))),
      ],
    );
  }
}

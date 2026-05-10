import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../models/user_model.dart';
import '../services/paciente_service.dart';
import '../services/auth_service.dart';

class AgendarCitaStepperScreen extends StatefulWidget {
  final User user;
  final String token;

  const AgendarCitaStepperScreen({super.key, required this.user, required this.token});

  @override
  _AgendarCitaStepperScreenState createState() => _AgendarCitaStepperScreenState();
}

class _AgendarCitaStepperScreenState extends State<AgendarCitaStepperScreen> {
  int _currentStep = 0;
  bool _isLoading = false;
  
  // Datos del agendamiento
  String? _selectedEspecialidad;
  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  TimeOfDay _selectedTime = const TimeOfDay(hour: 9, minute: 0);
  int? _createdCitaId;

  final List<String> _especialidades = [
    'Ansiedad y Depresión',
    'Terapia de Pareja',
    'Psicología Infantil',
    'Trastornos Alimenticios',
    'Terapia Familiar'
  ];

  void _nextStep() {
    if (_currentStep < 3) {
      setState(() => _currentStep += 1);
    } else {
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
    
    // Simulamos la petición al backend para agendar (CU11 / RF-06)
    // En una implementación real llamaríamos a CitaService.agendar(...)
    await Future.delayed(const Duration(seconds: 2));
    
    setState(() {
      _isLoading = false;
      _createdCitaId = 100 + (DateTime.now().millisecond % 900); // Mock ID
      _currentStep = 4; // Paso de éxito
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agendar Nueva Cita'),
        backgroundColor: const Color(0xFF2563EB),
        elevation: 0,
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator())
        : Theme(
            data: Theme.of(context).copyWith(
              colorScheme: const ColorScheme.light(primary: Color(0xFF2563EB)),
            ),
            child: Stepper(
              type: StepperType.horizontal,
              currentStep: _currentStep > 3 ? 3 : _currentStep,
              onStepContinue: _nextStep,
              onStepCancel: _prevStep,
              steps: _buildSteps(),
              controlsBuilder: (context, details) {
                if (_currentStep == 4) return const SizedBox.shrink();
                return Padding(
                  padding: const EdgeInsets.only(top: 20),
                  child: Row(
                    children: [
                      Expanded(
                        child: ElevatedButton(
                          onPressed: details.onStepContinue,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          child: Text(_currentStep == 3 ? 'CONFIRMAR CITA' : 'CONTINUAR'),
                        ),
                      ),
                      if (_currentStep > 0) ...[
                        const SizedBox(width: 12),
                        TextButton(
                          onPressed: details.onStepCancel,
                          child: const Text('ATRÁS', style: TextStyle(color: Colors.grey)),
                        ),
                      ]
                    ],
                  ),
                );
              },
            ),
          ),
    );
  }

  List<Step> _buildSteps() {
    if (_currentStep == 4) return [_buildSuccessStep()];
    
    return [
      Step(
        title: const Text('Motivo'),
        isActive: _currentStep >= 0,
        state: _currentStep > 0 ? StepState.complete : StepState.indexed,
        content: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('¿Qué tipo de atención buscas?', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 16),
            ..._especialidades.map((e) => RadioListTile<String>(
              title: Text(e),
              value: e,
              groupValue: _selectedEspecialidad,
              onChanged: (val) => setState(() => _selectedEspecialidad = val),
            )).toList(),
          ],
        ),
      ),
      Step(
        title: const Text('Datos'),
        isActive: _currentStep >= 1,
        state: _currentStep > 1 ? StepState.complete : StepState.indexed,
        content: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Información del Paciente', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 16),
            _buildDataField('Nombre Completo', widget.user.username),
            _buildDataField('Correo Electrónico', widget.user.email),
            const SizedBox(height: 8),
            const Card(
              color: Color(0xFFFEF2F2),
              child: Padding(
                padding: EdgeInsets.all(12),
                child: Row(
                  children: [
                    Icon(Icons.warning_amber_rounded, color: Color(0xFFDC2626)),
                    SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Las cancelaciones reiteradas restringirán su acceso.',
                        style: TextStyle(color: Color(0xFFDC2626), fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      Step(
        title: const Text('Horario'),
        isActive: _currentStep >= 2,
        state: _currentStep > 2 ? StepState.complete : StepState.indexed,
        content: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Seleccione Fecha y Hora', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.calendar_today, color: Color(0xFF2563EB)),
              title: Text(DateFormat('EEEE, d MMMM yyyy').format(_selectedDate)),
              onTap: () async {
                final date = await showDatePicker(
                  context: context,
                  initialDate: _selectedDate,
                  firstDate: DateTime.now(),
                  lastDate: DateTime.now().add(const Duration(days: 30)),
                );
                if (date != null) setState(() => _selectedDate = date);
              },
            ),
            ListTile(
              leading: const Icon(Icons.access_time, color: Color(0xFF2563EB)),
              title: Text(_selectedTime.format(context)),
              onTap: () async {
                final time = await showTimePicker(
                  context: context,
                  initialTime: _selectedTime,
                );
                if (time != null) setState(() => _selectedTime = time);
              },
            ),
          ],
        ),
      ),
      Step(
        title: const Text('Confirmar'),
        isActive: _currentStep >= 3,
        content: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFFF8FAFC),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E8F0)),
          ),
          child: Column(
            children: [
              _buildSummaryItem('Especialidad', _selectedEspecialidad ?? 'No seleccionada'),
              _buildSummaryItem('Fecha', DateFormat('dd/MM/yyyy').format(_selectedDate)),
              _buildSummaryItem('Hora', _selectedTime.format(context)),
              _buildSummaryItem('Clínica', 'San Aurelio (Principal)'),
            ],
          ),
        ),
      ),
    ];
  }

  Step _buildSuccessStep() {
    return Step(
      title: const Text('Éxito'),
      isActive: true,
      content: Center(
        child: Column(
          children: [
            const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 80),
            const SizedBox(height: 16),
            const Text('¡Cita Programada!', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
            const Text('Su reserva ha sido registrada correctamente', style: TextStyle(color: Color(0xFF64748B))),
            const SizedBox(height: 32),
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 20, offset: const Offset(0, 10))],
              ),
              child: Column(
                children: [
                  QrImageView(
                    data: 'CITA_ID:$_createdCitaId|PACIENTE:${widget.user.username}',
                    version: QrVersions.auto,
                    size: 200.0,
                  ),
                  const SizedBox(height: 16),
                  Text('TICKET #$_createdCitaId', style: const TextStyle(fontWeight: FontWeight.bold, letterSpacing: 2)),
                ],
              ),
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0F172A)),
              child: const Text('VOLVER AL INICIO'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDataField(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B), fontWeight: FontWeight.w600)),
          const SizedBox(height: 4),
          Text(value, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
        ],
      ),
    );
  }

  Widget _buildSummaryItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Color(0xFF64748B))),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
        ],
      ),
    );
  }
}

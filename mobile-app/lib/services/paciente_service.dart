// [SPRINT 1 - T015] Servicio dedicado para operaciones de pacientes en la App Móvil.
// [RF-02] Registro de Pacientes: Persistencia vía API REST con validación de datos.
// [RF-29] Aislamiento SaaS: El token JWT incluye el tenant; el Backend lo asigna automáticamente.
// [CU-02] Registro de Paciente (Onboarding): Serialización del formulario móvil.

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/paciente_model.dart';

class PacienteService {
  // [SPRINT 1 - T015] Listar clínicas activas (Público)
  static Future<List<Map<String, dynamic>>> getClinicasPublic() async {
    try {
      final response = await http.get(Uri.parse(ApiConfig.clinicas));
      if (response.statusCode == 200) {
        return List<Map<String, dynamic>>.from(json.decode(response.body));
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  // [SPRINT 1 - T015] Registro Público (Autogestión / Onboarding)
  // [MODIFICACIÓN V3.0]: Parámetros simplificados y opcionales.
  static Future<void> registrarPacientePublico({
    int? clinicaId,
    required String nombre,
    required String ci,
    required String email,
    required String password,
    String? fechaNacimiento,
    required String telefono,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.pacientesRegistroPublico),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          if (clinicaId != null) 'clinica_id': clinicaId,
          'nombre': nombre,
          'ci': ci,
          'email': email,
          'password': password,
          if (fechaNacimiento != null) 'fecha_nacimiento': fechaNacimiento,
          'telefono': telefono,
        }),
      );

      if (response.statusCode == 201) return;
      if (response.statusCode == 400) {
        final errors = json.decode(response.body);
        final firstError = errors.values.first;
        final msg = firstError is List ? firstError.first : firstError.toString();
        throw Exception('Error de validación: $msg');
      }
      throw Exception('Error del servidor (HTTP ${response.statusCode}).');
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Error de conexión con el servidor.');
    }
  }

  // [ALINEACIÓN SPRINT 1 - RF-29] Vinculación post-login (Usuario Huérfano)
  static Future<void> vincularClinica({
    required String token,
    required int clinicaId,
  }) async {
    try {
      final response = await http.patch(
        Uri.parse(ApiConfig.associateClinic),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({'clinica_id': clinicaId}),
      );

      if (response.statusCode == 200) return;
      
      final body = json.decode(response.body);
      throw Exception(body['detail'] ?? 'Error al vincular clínica.');
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Error de conexión al intentar vincular clínica.');
    }
  }

  // [SPRINT 1 - T015] [RF-02] [CU-02] Registrar un nuevo paciente vía POST
  static Future<Paciente> registrarPaciente({
    required String token,
    required String nombre,
    required String ci,
    required String fechaNacimiento,
    required String telefono,
    String? motivoConsulta,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(ApiConfig.pacientesRegistrar),
        headers: {
          'Content-Type': 'application/json',
          // [RF-29] El JWT lleva el clinica_id del tenant → Backend lo asigna automáticamente
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'nombre': nombre,
          'ci': ci,
          'fecha_nacimiento': fechaNacimiento,
          'telefono': telefono,
          if (motivoConsulta != null && motivoConsulta.isNotEmpty)
            'motivo_consulta': motivoConsulta,
        }),
      );

      if (response.statusCode == 201) {
        // El backend devuelve { "message": "...", "data": {...} }
        final body = json.decode(response.body);
        return Paciente.fromJson(body['data']);
      } else if (response.statusCode == 400) {
        final errors = json.decode(response.body);
        // Extraer primer mensaje de error del serializer
        final firstError = errors.values.first;
        final msg = firstError is List ? firstError.first : firstError.toString();
        throw Exception('Error de validación: $msg');
      } else if (response.statusCode == 401) {
        throw Exception('Tu sesión ha expirado. Por favor vuelve a iniciar sesión.');
      } else if (response.statusCode == 403) {
        throw Exception('Acceso denegado: No tienes permisos para registrar pacientes.');
      } else {
        throw Exception('Error del servidor (HTTP ${response.statusCode}).');
      }
    } catch (e) {
      // Solo re-lanzamos si no es ya una Exception nuestra
      if (e is Exception) rethrow;
      throw Exception('Error de conexión: No se pudo contactar con el servidor.');
    }
  }

  // [SPRINT 1 - T012] Listar pacientes de la clínica (T012: Consumo Auth API)
  static Future<List<Paciente>> getPacientes(String token) async {
    try {
      final response = await http.get(
        Uri.parse(ApiConfig.pacientes),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        final List<dynamic> body = json.decode(response.body);
        return body.map((item) => Paciente.fromJson(item)).toList();
      } else if (response.statusCode == 403) {
        throw Exception('Solo los psicólogos pueden consultar la lista de pacientes.');
      } else {
        throw Exception('Error al obtener pacientes (HTTP ${response.statusCode}).');
      }
    } catch (e) {
      if (e is Exception) rethrow;
      throw Exception('Error de conexión al obtener los pacientes.');
    }
  }
}

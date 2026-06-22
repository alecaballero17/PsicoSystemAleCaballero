import 'dart:convert';
import 'package:http/http.dart' as http;

import '../config/api_config.dart';

class CitaPagoService {
  static Map<String, String> _headers(String token) => {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
        'bypass-tunnel-reminder': 'true',
      };

  static Future<Map<String, dynamic>> getHistorial(
    String token, {
    String? estadoPago,
    String? estado,
    int? clinicaId,
  }) async {
    final params = <String, String>{};
    if (estadoPago != null && estadoPago.isNotEmpty) {
      params['estado_pago'] = estadoPago;
    }
    if (estado != null && estado.isNotEmpty) {
      params['estado'] = estado;
    }
    if (clinicaId != null) {
      params['clinica_id'] = clinicaId.toString();
    }

    final uri = Uri.parse('${ApiConfig.baseUrl}/mobile/citas/')
        .replace(queryParameters: params.isEmpty ? null : params);
    final response = await http.get(uri, headers: _headers(token));

    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<List<dynamic>> getPsicologos(String token) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/psicologos/'),
      headers: _headers(token),
    );

    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<Map<String, dynamic>> crearCita({
    required String token,
    required DateTime fechaHora,
    required String motivo,
    required String psicologoUsername,
    String monto = '120.00',
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/citas/'),
      headers: _headers(token),
      body: json.encode({
        'fecha_hora': fechaHora.toIso8601String(),
        'motivo': motivo,
        'psicologo_username': psicologoUsername,
        'monto': monto,
      }),
    );

    if (response.statusCode == 201) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<Map<String, dynamic>> pagarCita({
    required String token,
    required int citaId,
    required String metodoPago,
    String numeroTarjeta = '4242424242424242',
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/paciente/pagar/'),
      headers: _headers(token),
      body: json.encode({
        'cita_id': citaId,
        'metodo_pago': metodoPago,
        'numero_tarjeta': numeroTarjeta,
      }),
    );

    if (response.statusCode == 201) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<Map<String, dynamic>> cancelarCita({
    required String token,
    required int citaId,
    String motivo = 'Cancelacion solicitada desde la app movil',
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/citas/$citaId/cancelar/'),
      headers: _headers(token),
      body: json.encode({'motivo': motivo}),
    );

    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<Map<String, dynamic>> reporteIA({
    required String token,
    required String comando,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/reportes/ia/'),
      headers: _headers(token),
      body: json.encode({'comando': comando}),
    );

    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<String> chatbot({
    required String token,
    required String mensaje,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/chatbot/'),
      headers: _headers(token),
      body: json.encode({'mensaje': mensaje}),
    );

    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      return data['respuesta'] ?? 'Sin respuesta.';
    }
    throw Exception(_extractError(response));
  }

  /// Chatbot personalizado por clínica (Groq + contexto de citas en esa clínica)
  static Future<String> chatbotClinica({
    required String token,
    required int clinicaId,
    required String mensaje,
    List<Map<String, String>> historial = const [],
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/clinica/$clinicaId/chatbot/'),
      headers: _headers(token),
      body: json.encode({
        'mensaje': mensaje,
        'historial': historial,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      return data['respuesta'] ?? 'Sin respuesta.';
    }
    throw Exception(_extractError(response));
  }

  /// URL del comprobante PDF de una cita pagada (se abre con el token en header)
  static String comprobantePdfUrl(int citaId) =>
      '${ApiConfig.baseUrl}/mobile/citas/$citaId/comprobante/pdf/';

  static String get reportePdfUrl => '${ApiConfig.baseUrl}/mobile/citas/reporte/pdf/';

  static String _extractError(http.Response response) {
    try {
      final body = json.decode(utf8.decode(response.bodyBytes));
      return body['error'] ?? body['detail'] ?? 'Error HTTP ${response.statusCode}';
    } catch (_) {
      return 'Error HTTP ${response.statusCode}';
    }
  }
}

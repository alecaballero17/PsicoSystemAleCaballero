import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';

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
    bool historialCompleto = false,
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
    if (historialCompleto) {
      params['historial_completo'] = 'true';
    }

    final uri = Uri.parse('${ApiConfig.baseUrl}/mobile/citas/')
        .replace(queryParameters: params.isEmpty ? null : params);
    final response = await http.get(uri, headers: _headers(token));

    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<List<dynamic>> getPsicologos(String token, {int? clinicaId}) async {
    final params = <String, String>{};
    if (clinicaId != null) {
      params['clinica_id'] = clinicaId.toString();
    }
    final uri = Uri.parse('${ApiConfig.baseUrl}/psicologos/')
        .replace(queryParameters: params.isEmpty ? null : params);
        
    final response = await http.get(
      uri,
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
    required int clinicaId,
    String monto = '120.00',
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/citas/'),
      headers: _headers(token),
      body: json.encode({
        'fecha_hora': fechaHora.toIso8601String(),
        'motivo': motivo,
        'psicologo_username': psicologoUsername,
        'clinica_id': clinicaId,
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
    String? paymentIntentId,
    String numeroTarjeta = '4242424242424242',
  }) async {
    final body = {
      'cita_id': citaId,
      'metodo_pago': metodoPago,
      'numero_tarjeta': numeroTarjeta,
    };
    if (paymentIntentId != null) {
      body['payment_intent_id'] = paymentIntentId;
    }
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/paciente/pagar/'),
      headers: _headers(token),
      body: json.encode(body),
    );

    if (response.statusCode == 201) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<Map<String, dynamic>> createStripePaymentIntent({
    required String token,
    required int citaId,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/stripe/create-payment-intent/'),
      headers: _headers(token),
      body: json.encode({'cita_id': citaId}),
    );

    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<Map<String, dynamic>> createStripeCheckoutSession({
    required String token,
    required int citaId,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/stripe/create-checkout-session/'),
      headers: _headers(token),
      body: json.encode({'cita_id': citaId}),
    );

    if (response.statusCode == 200) {
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

  static Future<String> transcribeAudio({
    required String token,
    required String filePath,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}/mobile/transcribe/');
    final request = http.MultipartRequest('POST', uri)
      ..headers.addAll({'Authorization': 'Bearer $token'})
      ..files.add(await http.MultipartFile.fromPath('audio', filePath));
      
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      return data['transcription'] ?? '';
    }
    throw Exception(_extractError(response));
  }

  static Future<Map<String, dynamic>> generarReporte({
    required String token,
    required String transcript,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/generar-reporte/'),
      headers: _headers(token),
      body: json.encode({'transcript': transcript}),
    );

    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception(_extractError(response));
  }

  static Future<List<String>> getDisponibilidad({
    required String token,
    required String psicologoUsername,
    required String fecha,
  }) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}/mobile/citas/disponibilidad/')
        .replace(queryParameters: {
      'psicologo_username': psicologoUsername,
      'fecha': fecha,
    });
    final response = await http.get(uri, headers: _headers(token));

    if (response.statusCode == 200) {
      final data = json.decode(utf8.decode(response.bodyBytes));
      return List<String>.from(data['horas_ocupadas'] ?? []);
    }
    throw Exception(_extractError(response));
  }

  static Future<String> chatbot({
    required String token,
    required String message,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiConfig.baseUrl}/mobile/chat/global/'),
      headers: _headers(token),
      body: json.encode({'mensaje': message}),
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

  /// Descarga el comprobante PDF y lo guarda temporalmente
  static Future<String> downloadComprobantePdf(String token, int citaId) async {
    final uri = Uri.parse('${ApiConfig.baseUrl}/mobile/citas/$citaId/comprobante/pdf/');
    final response = await http.get(uri, headers: _headers(token));

    if (response.statusCode == 200) {
      final tempDir = await getTemporaryDirectory();
      final file = File('${tempDir.path}/comprobante_$citaId.pdf');
      await file.writeAsBytes(response.bodyBytes);
      return file.path;
    }
    throw Exception('Error al descargar comprobante PDF');
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

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

enum ChatbotContextType { global, clinica, cita }

class ChatbotService {
  static Map<String, String> _headers(String token) => {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
        'bypass-tunnel-reminder': 'true',
      };

  static Future<String> sendMessage({
    required String token,
    required ChatbotContextType type,
    required String mensaje,
    int? contextId,
  }) async {
    String url;
    switch (type) {
      case ChatbotContextType.global:
        url = ApiConfig.chatGlobal;
        break;
      case ChatbotContextType.clinica:
        if (contextId == null) throw Exception("Falta contextId para la clínica");
        url = ApiConfig.chatClinica(contextId);
        break;
      case ChatbotContextType.cita:
        if (contextId == null) throw Exception("Falta contextId para la cita");
        url = ApiConfig.chatCita(contextId);
        break;
    }

    try {
      final response = await http.post(
        Uri.parse(url),
        headers: _headers(token),
        body: json.encode({'mensaje': mensaje}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        return data['respuesta'] ?? 'Sin respuesta.';
      }
      
      return 'Lo siento, hubo un error al comunicarme con mis servidores. (Error ${response.statusCode})';
    } catch (e) {
      return 'Lo siento, no pude conectarme al servidor.';
    }
  }
}

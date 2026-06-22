import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

class NotificacionService {
  static Future<List<dynamic>> getNotificaciones(String token) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/mobile/notificaciones/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode == 200) {
      return json.decode(utf8.decode(response.bodyBytes));
    }
    throw Exception('Error al obtener notificaciones.');
  }

  static Future<void> marcarLeidas(String token) async {
    final response = await http.patch(
      Uri.parse('${ApiConfig.baseUrl}/mobile/notificaciones/'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Error al marcar como leídas.');
    }
  }
}

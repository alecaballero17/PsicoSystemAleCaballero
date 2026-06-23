import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

class RecomendacionService {
  static Future<List<dynamic>> getRecomendaciones(String token) async {
    final response = await http.get(
      Uri.parse('${ApiConfig.baseUrl}/mobile/recomendaciones/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al cargar recomendaciones');
    }
  }

  static Future<void> updateEstadoRecomendacion(String token, int id, String nuevoEstado) async {
    final response = await http.put(
      Uri.parse('${ApiConfig.baseUrl}/mobile/recomendaciones/$id/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'estado': nuevoEstado}),
    );

    if (response.statusCode != 200) {
      throw Exception('Error al actualizar el estado de la recomendación');
    }
  }
}

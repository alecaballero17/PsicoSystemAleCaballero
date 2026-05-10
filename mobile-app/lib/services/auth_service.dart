import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

// 👇 IMPORTAMOS LOS MODELOS QUE ACABAMOS DE CREAR
import '../models/auth_response_model.dart';
import '../models/user_model.dart';
import '../models/paciente_model.dart';

class AuthService {
  // CU-01 / RF-01: Ahora devuelve AuthResponse en vez de Map
  static Future<AuthResponse> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${ApiConfig.baseUrl}/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        // 🔥 Pasamos el Map al Constructor Factory
        return AuthResponse.fromJson(json.decode(response.body));
      } else {
        throw Exception('Error de credenciales (Código ${response.statusCode})');
      }
    } catch (e) {
      throw Exception('Error de conexión: No se pudo contactar con el servidor.');
    }
  }

  // T009: Ahora devuelve un objeto User en vez de Map
  static Future<User> getCurrentUser(String token) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/auth/me/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        // 🔥 Parseo seguro con Tipado Fuerte
        return User.fromJson(json.decode(response.body));
      } else {
        throw Exception('Sesión expirada o token inválido (Código ${response.statusCode})');
      }
    } catch (e) {
      throw Exception('Error de conexión al obtener el perfil del paciente.');
    }
  }

  // T014: Ahora devuelve una List<Paciente> en vez de List<dynamic>
  static Future<List<Paciente>> getPacientes(String token) async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/pacientes/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        List<dynamic> body = json.decode(response.body);
        // 🔥 Convertimos la lista cruda en una lista de OBJETOS reales
        return body.map((item) => Paciente.fromJson(item)).toList();
      } else if (response.statusCode == 403) {
        throw Exception('Acceso Denegado: Tu rol actual no tiene permisos de Psicólogo.');
      } else {
        throw Exception('Error al cargar la lista (Código ${response.statusCode})');
      }
    } catch (e) {
      throw Exception('Error de conexión al obtener los pacientes: $e');
    }
  }

  // Obtener la lista pública de Clínicas
  static Future<List<dynamic>> getClinicasPublicas() async {
    try {
      final response = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/clinicas/publicas/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      } else {
        throw Exception('Error al cargar clínicas (Código ${response.statusCode})');
      }
    } catch (e) {
      throw Exception('Error de conexión al obtener las clínicas disponibles: $e');
    }
  }

  // Actualizar Perfil
  static Future<void> updateProfile(String token, String firstName, String ci, String telefono) async {
    try {
      final response = await http.put(
        Uri.parse('${ApiConfig.baseUrl}/auth/me/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'first_name': firstName,
          'ci': ci,
          'telefono': telefono,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Error al actualizar el perfil (Código ${response.statusCode})');
      }
    } catch (e) {
      throw Exception('Error de conexión al actualizar el perfil: $e');
    }
  }

  // Cambiar Contraseña
  static Future<void> changePassword(String token, String newPassword) async {
    try {
      final response = await http.put(
        Uri.parse('${ApiConfig.baseUrl}/auth/change_password/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'new_password': newPassword,
        }),
      );

      if (response.statusCode != 200) {
        final errorMsg = json.decode(response.body)['detail'] ?? 'Error desconocido';
        throw Exception(errorMsg);
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }
}
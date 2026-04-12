class AuthResponse {
  final String access;
  final String refresh;
  final String role;
  final int? clinicaId; // [RF-29]

  AuthResponse({
    required this.access,
    required this.refresh,
    required this.role,
    this.clinicaId,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      access: json['access'] ?? '',
      refresh: json['refresh'] ?? '',
      role: json['role'] ?? 'PACIENTE',
      clinicaId: json['clinica_id'], // Puede ser nulo
    );
  }
}
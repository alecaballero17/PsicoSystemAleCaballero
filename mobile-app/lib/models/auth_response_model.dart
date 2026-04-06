class AuthResponse {
  final String access;
  final String refresh;
  final String role;

  AuthResponse({required this.access, required this.refresh, required this.role});

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      access: json['access'] ?? '',
      refresh: json['refresh'] ?? '',
      role: json['role'] ?? 'PACIENTE',
    );
  }
}
class User {
  final int id;
  final String username;
  final String clinicaNombre;

  User({required this.id, required this.username, required this.clinicaNombre});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? 0,
      username: json['username'] ?? 'Usuario',
      clinicaNombre: json['clinica_nombre'] ?? 'Sin Clínica',
    );
  }
}
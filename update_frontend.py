import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\test_frontend.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add logout button next to login
if 'logout()' not in content:
    content = content.replace(
        '<button onclick="login()">Iniciar Sesión</button>',
        '<button onclick="login()">Iniciar Sesión</button>\n                <button onclick="logout()" style="background-image: linear-gradient(to right, #ff4b4b 0%, #ff8e53 100%);">Cerrar Sesión</button>'
    )
    
    logout_script = '''
        function logout() {
            token = '';
            document.getElementById('login-status').innerHTML = '<span class="error">Sesión cerrada.</span>';
            alert("Has cerrado sesión.");
        }
'''
    content = content.replace('// 2. BUSCAR PACIENTES', logout_script + '\n        // 2. BUSCAR PACIENTES')


# Add edit and delete options for appointments
if 'editarCita()' not in content:
    citas_html = '''
            <div class="row" style="margin-top: 15px; border-top: 1px solid #3b3b55; padding-top: 15px;">
                <input type="number" id="mod-cita-id" placeholder="ID de Cita a Modificar">
                <select id="mod-cita-estado">
                    <option value="PENDIENTE">Pendiente</option>
                    <option value="COMPLETADA">Completada</option>
                    <option value="CANCELADA">Cancelada</option>
                </select>
                <button onclick="editarCita()">✏️ Editar Estado</button>
                <button onclick="eliminarCita()" style="background-image: linear-gradient(to right, #ff4b4b 0%, #ff8e53 100%);">🗑️ Eliminar (Soft-Delete)</button>
            </div>
            <p id="mod-cita-status"></p>
'''
    content = content.replace(
        '<p id="cita-status"></p>\n        </div>',
        '<p id="cita-status"></p>\n' + citas_html + '        </div>'
    )
    
    citas_script = '''
        async function editarCita() {
            if(!token) return alert("Inicia sesión primero");
            const status = document.getElementById('mod-cita-status');
            try {
                const id = document.getElementById('mod-cita-id').value;
                const estado = document.getElementById('mod-cita-estado').value;
                const res = await fetch(${BASE_URL}/citas//, { 
                    method: 'PATCH', 
                    headers: headers(), 
                    body: JSON.stringify({ estado: estado }) 
                });
                const data = await res.json();
                if(res.ok) status.innerHTML = <span class="success">✅ Cita editada. Nuevo estado: </span>;
                else status.innerHTML = <span class="error">❌ Error: </span>;
            } catch (e) { status.innerHTML = e; }
        }

        async function eliminarCita() {
            if(!token) return alert("Inicia sesión primero");
            const status = document.getElementById('mod-cita-status');
            try {
                const id = document.getElementById('mod-cita-id').value;
                const res = await fetch(${BASE_URL}/citas//, { 
                    method: 'DELETE', 
                    headers: headers()
                });
                if(res.ok) status.innerHTML = <span class="success">✅ Cita eliminada correctamente (Soft-Delete).</span>;
                else status.innerHTML = <span class="error">❌ Error al eliminar.</span>;
            } catch (e) { status.innerHTML = e; }
        }
'''
    content = content.replace('// 4. CREAR NOTA DE EVOLUCION', citas_script + '\n        // 4. CREAR NOTA DE EVOLUCION')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("test_frontend.html updated")

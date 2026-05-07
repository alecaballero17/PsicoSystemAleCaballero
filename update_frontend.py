import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\test_frontend.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add Step 7 HTML
html_old = '            <p id="pdf-status"></p>\n        </div>\n    </div>'
html_new = '''            <p id="pdf-status"></p>
        </div>

        <!-- 7. REPORTES Y AUDIO -->
        <div class="card" id="step7">
            <h2>Paso 7: Reportes Dinámicos y de Audio <span class="badge">NUEVO</span></h2>
            <div class="row">
                <div>
                    <label style="font-size: 0.8em; color: #aaa;">Fecha Inicio:</label>
                    <input type="date" id="rep-fecha-inicio" value="2026-05-01">
                </div>
                <div>
                    <label style="font-size: 0.8em; color: #aaa;">Fecha Fin:</label>
                    <input type="date" id="rep-fecha-fin" value="2026-05-31">
                </div>
            </div>
            <div style="margin: 10px 0;">
                <label style="cursor: pointer;">
                    <input type="checkbox" id="rep-generar-audio" checked style="width: auto;"> Generar MP3 (Audio)
                </label>
            </div>
            <button onclick="generarReporte()">🎙️ Generar Reporte</button>
            <pre id="reporte-result">El texto del reporte aparecerá aquí...</pre>
            <div id="audio-container" style="margin-top: 10px;"></div>
        </div>
    </div>'''

if '<!-- 7. REPORTES Y AUDIO -->' not in content:
    content = content.replace(html_old, html_new)

# Add Step 7 JS
js_old = '''                a.click(); window.URL.revokeObjectURL(url);
                status.innerHTML = <span class="success">✅ PDF descargado.</span>;
            } catch (e) { status.innerHTML = <span class="error">❌ Error: </span>; }
        }
    </script>'''

js_new = '''                a.click(); window.URL.revokeObjectURL(url);
                status.innerHTML = <span class="success">✅ PDF descargado.</span>;
            } catch (e) { status.innerHTML = <span class="error">❌ Error: </span>; }
        }

        // 7. REPORTES Y AUDIO
        async function generarReporte() {
            if(!token) return alert("Inicia sesión primero");
            const resBox = document.getElementById('reporte-result');
            const audioBox = document.getElementById('audio-container');
            resBox.innerText = "⏳ Procesando reporte y generando audio (esto puede tardar unos segundos)...";
            audioBox.innerHTML = "";

            try {
                const payload = {
                    fecha_inicio: document.getElementById('rep-fecha-inicio').value,
                    fecha_fin: document.getElementById('rep-fecha-fin').value,
                    generar_audio: document.getElementById('rep-generar-audio').checked
                };
                
                const res = await fetch(${BASE_URL}/reportes/personalizado/, { 
                    method: 'POST', 
                    headers: headers(), 
                    body: JSON.stringify(payload) 
                });
                
                const data = await res.json();
                
                if(res.ok) {
                    resBox.innerText = data.texto;
                    if(data.audio_url) {
                        const audioFullUrl = http://localhost:8000;
                        audioBox.innerHTML = 
                            <p style="color: #00f2fe; margin-bottom: 5px;">Escuchar Reporte:</p>
                            <audio controls src="" style="width: 100%;"></audio>
                            <br>
                            <a href="" target="_blank" style="color: #4facfe; font-size: 0.9em;">Descargar MP3</a>
                        ;
                    }
                } else {
                    resBox.innerHTML = <span class="error">❌ Error: </span>;
                }
            } catch (e) { resBox.innerText = e; }
        }
    </script>'''

if '// 7. REPORTES Y AUDIO' not in content:
    content = content.replace(js_old, js_new)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done frontend update')

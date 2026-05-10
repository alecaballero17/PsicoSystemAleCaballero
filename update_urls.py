import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P3_Logistica_Citas\urls.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'ListaEsperaViewSet' not in content:
    content = content.replace('from django.urls import path', 'from django.urls import path, include\nfrom rest_framework.routers import SimpleRouter')
    content = content.replace('CitaRetrieveUpdateAPIView,', 'CitaRetrieveUpdateAPIView,\n    ListaEsperaViewSet,')
    
    new_urls = '''
router = SimpleRouter()
router.register(r'api/lista-espera', ListaEsperaViewSet, basename='lista-espera')

urlpatterns = [
    path('', include(router.urls)),
    path("api/citas/", CitaListCreateAPIView.as_view(), name="api_citas"),
    path(
        "api/citas/<int:pk>/",
        CitaRetrieveUpdateAPIView.as_view(),
        name="api_citas_detalle",
    ),
]
'''
    import re
    content = re.sub(r'urlpatterns = \[.*?\]', new_urls, content, flags=re.DOTALL)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated urls.py")
else:
    print("Already updated")

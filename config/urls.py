import time
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from django.db import connection


def healthz(request):
    start_time = time.time()
    db_status = "connected"
    http_status = 200

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
    except Exception as e:
        db_status = f"unavailable: {str(e)}"
        http_status = 503

    latency_ms = round((time.time() - start_time) * 1000, 2)

    # Если запрос сделан из браузера — возвращаем аккуратную статус-карточку
    if "text/html" in request.META.get("HTTP_ACCEPT", ""):
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="utf-8">
            <title>System Status | MAI Appeals Center</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }}
                .card {{ background: #1e293b; border-radius: 12px; padding: 32px; width: 440px; box-shadow: 0 10px 25px rgba(0,0,0,0.3); border: 1px solid #334155; }}
                .header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; }}
                .badge {{ background: #059669; color: #ecfdf5; padding: 4px 10px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }}
                .badge.err {{ background: #dc2626; }}
                .dot {{ width: 8px; height: 8px; background: #34d399; border-radius: 50%; }}
                .row {{ display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid #334155; font-size: 14px; }}
                .val {{ font-weight: 600; color: #38bdf8; }}
            </style>
        </head>
        <body>
            <div class="card">
                <div class="header">
                    <h2 style="margin: 0; font-size: 18px;">МАИ • Кафедра 317</h2>
                    <span class="badge {'err' if http_status != 200 else ''}">
                        <span class="dot" style="background: {'#f87171' if http_status != 200 else '#34d399'}"></span>
                        {'OPERATIONAL' if http_status == 200 else 'DEGRADED'}
                    </span>
                </div>
                <div class="row"><span>Django Core</span><span class="val">Running</span></div>
                <div class="row"><span>Database</span><span class="val" style="color: {'#34d399' if http_status == 200 else '#f87171'}">{db_status}</span></div>
                <div class="row"><span>Response Latency</span><span class="val">{latency_ms} ms</span></div>
                <div class="row" style="border: none;"><span>Static Assets Engine</span><span class="val">WhiteNoise</span></div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html_content, status=http_status)

    # Для API / систем мониторинга — чистый JSON
    return JsonResponse(
        {
            "status": "ok" if http_status == 200 else "degraded",
            "database": db_status,
            "latency_ms": latency_ms,
            "service": "mai-appeals-center",
        },
        status=http_status,
    )


urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("accounts.urls")),
    path("", include("appeals.urls")),
]

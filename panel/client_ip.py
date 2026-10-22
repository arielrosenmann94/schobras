def get_client_ip(request):
    """IP real del visitante detrás del router de Heroku (un solo proxy).

    El router agrega la IP del cliente al final de X-Forwarded-For; las
    entradas anteriores las puede escribir el propio visitante, por eso se
    toma la última. Sin la cabecera (local, pruebas) se usa REMOTE_ADDR.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    parts = [part.strip() for part in forwarded.split(",") if part.strip()]
    if parts:
        return parts[-1]
    return request.META.get("REMOTE_ADDR")

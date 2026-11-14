#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batería de pruebas de seguridad - Gestión de Citas Inteligente
===============================================================
SOLO para entornos LOCALES o de pruebas propios y autorizados.
No usa dependencias externas (solo biblioteca estándar de Python 3.8+).

Qué hace:
  - Registra 2 usuarios de prueba (A y B) y trabaja solo con datos creados por el propio script.
  - Ejecuta pruebas de JWT, autorización (BOLA/IDOR), inyección, errores, CORS, cabeceras y límites.
  - Borra al final los datos que creó (si el servidor se lo permite).
  - Guarda un JSON con los resultados para comparar "antes" y "después".

Uso (PowerShell, desde la carpeta del script):
  py security_tests.py --base http://localhost:8280 --out resultados_antes.json
  py security_tests.py --base http://localhost:8080          # stack "develop"
  py security_tests.py --base http://localhost:8280 --secret "mi-secreto-real"

Estados:
  OK          la protección funciona (resultado esperado en un sistema seguro)
  VULN        resultado inseguro: la vulnerabilidad/riesgo se reprodujo
  INCONCLUSO  no se pudo concluir (falta un dato, p. ej. el secreto JWT, o el servicio no respondió)
  INFO        hallazgo informativo / riesgo potencial que requiere criterio
"""
import argparse
import base64
import hashlib
import hmac
import json
import os
import random
import socket
import statistics
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta

DEFAULT_SECRET = "gestion-de-citas-inteligente-2026-super-secret-key"  # valor por defecto en JwtService.java
PAD = "0123456789abcdef0123456789abcdef"  # relleno que aplica JwtService si el secreto mide < 32
PASSWORD = "Prueba#2026seg"
RESULTS = []
BASE = ""


# ------------------------------------------------------------------ utilidades
class Resp:
    def __init__(self, status, headers, text):
        self.status = status
        self.headers = headers or {}
        self.text = text or ""
        try:
            self.json = json.loads(self.text)
        except Exception:
            self.json = None

    def header(self, name):
        for k, v in dict(self.headers).items():
            if k.lower() == name.lower():
                return v
        return None


def http(method, path, token=None, body=None, raw=None, headers=None, timeout=20):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else raw
    req = urllib.request.Request(url, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    elif raw is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return Resp(r.status, r.headers, r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return Resp(e.code, e.headers, e.read().decode("utf-8", "replace"))
    except Exception as e:  # sin conexión, timeout, etc.
        return Resp(0, {}, str(e))


def b64u(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def b64u_dec(s):
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def forge(claims, secret, alg="HS256"):
    """Construye un JWT. alg='none' devuelve un token sin firma."""
    h = b64u(json.dumps({"alg": alg, "typ": "JWT"}, separators=(",", ":")).encode())
    p = b64u(json.dumps(claims, separators=(",", ":")).encode())
    if alg == "none":
        return "%s.%s." % (h, p)
    key = (secret if len(secret) >= 32 else secret + PAD).encode()
    dig = {"HS256": hashlib.sha256, "HS384": hashlib.sha384, "HS512": hashlib.sha512}[alg]
    sig = hmac.new(key, ("%s.%s" % (h, p)).encode(), dig).digest()
    return "%s.%s.%s" % (h, p, b64u(sig))


def claims(email, uid, role, exp_delta=600):
    now = int(time.time())
    # iss/aud son los que emite users-service; sin ellos los servicios ya corregidos rechazarían el token por otra causa
    return {"sub": email, "userId": uid, "role": role, "iss": "citas-users-service", "aud": "citas-api",
            "iat": now, "exp": now + exp_delta}


def record(tid, nombre, estado, detalle=""):
    RESULTS.append({"id": tid, "prueba": nombre, "estado": estado, "detalle": detalle})
    print("[%-10s] %-4s %s" % (estado, tid, nombre))
    if detalle:
        print("             -> %s" % detalle)


def denied(tid, nombre, r, ok_detail=""):
    """Para pruebas donde el resultado seguro es 401/403."""
    if r.status in (401, 403):
        record(tid, nombre, "OK", "HTTP %d %s" % (r.status, ok_detail))
    elif r.status == 0:
        record(tid, nombre, "INCONCLUSO", "sin respuesta: " + r.text[:120])
    elif r.status >= 500:
        record(tid, nombre, "VULN", "HTTP %d: error no controlado del servidor" % r.status)
    else:
        record(tid, nombre, "VULN", "HTTP %d: la petición NO fue rechazada" % r.status)


def denied_no_leak(tid, nombre, r, marker):
    """Resultado seguro: no se devuelven datos ajenos. Acepta 401/403 y avisa si el código HTTP no es el ideal."""
    if r.status == 0:
        record(tid, nombre, "INCONCLUSO", "sin respuesta: " + r.text[:120])
    elif r.status >= 500:
        record(tid, nombre, "VULN", "HTTP %d: error no controlado del servidor" % r.status)
    elif r.status == 200 or (marker and marker in r.text):
        record(tid, nombre, "VULN", "HTTP %d: se devolvieron datos de otro usuario" % r.status)
    elif r.status in (401, 403):
        record(tid, nombre, "OK", "HTTP %d" % r.status)
    else:
        record(tid, nombre, "OK", "acceso denegado sin filtrar datos, pero con HTTP %d (lo ideal es 403)" % r.status)


def rnd(n=6):
    return "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))


def future_iso():
    dt = datetime.now() + timedelta(days=random.randint(60, 400))
    dt = dt.replace(hour=random.randint(8, 17), minute=random.randint(0, 59),
                    second=random.randint(0, 59), microsecond=0)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def new_user(tag):
    email = "auditoria.%s.%s@example.test" % (tag.lower(), rnd())
    r = http("POST", "/users", body={"nombre": "Auditoria " + tag, "email": email, "password": PASSWORD})
    if r.status != 201:
        return None, "registro HTTP %d %s" % (r.status, r.text[:150])
    l = http("POST", "/users/login", body={"email": email, "password": PASSWORD})
    if l.status != 200 or not l.json or not l.json.get("token"):
        return None, "login HTTP %d %s" % (l.status, l.text[:150])
    return {"id": l.json["id"], "email": email, "token": l.json["token"], "rol": l.json.get("rol")}, ""


def turno_body(uid):
    return {"idUsuario": uid, "especialidad": "Medicina General", "doctor": "Dr. Andres Mu\u00f1oz",
            "fechaHora": future_iso()}


# ------------------------------------------------------------------ pruebas
def run(args):
    A, err = new_user("A")
    if not A:
        print("No se pudo preparar el usuario A:", err)
        return
    B, err = new_user("B")
    if not B:
        print("No se pudo preparar el usuario B:", err)
        return
    print("Usuarios de prueba creados: A(id=%s) B(id=%s)\n" % (A["id"], B["id"]))
    secret = args.secret
    cleanup = []  # (metodo, ruta, token)

    # ---------------- JWT ----------------
    print("== JWT y autenticación ==")
    denied("J01", "Acceso sin token a recurso protegido (GET /users/{id})", http("GET", "/users/%s" % A["id"]))
    denied("J02", "Token inválido (cadena aleatoria)", http("GET", "/users/%s" % A["id"], token="abc.def.ghi"))

    good = forge(claims(A["email"], A["id"], "CLIENTE"), secret)
    r = http("GET", "/users/%s" % A["id"], token=good)
    secret_known = r.status == 200
    usando_defecto = (secret == DEFAULT_SECRET)
    nombre_j00 = "Secreto JWT predecible (valor por defecto del código)"
    if secret_known and usando_defecto:
        record("J00", nombre_j00, "VULN", "un token firmado por el atacante con el secreto del repositorio fue ACEPTADO")
    elif secret_known:
        record("J00", nombre_j00, "INFO", "se usa el secreto indicado en --secret (aceptado); sirve para las pruebas J03 y J07-J09")
    elif r.status in (401, 403):
        record("J00", nombre_j00, "OK", "el secreto desplegado NO es el del código. Pasa --secret si lo conoces para activar J03 y J07-J09")
    else:
        record("J00", nombre_j00, "INCONCLUSO", "HTTP %d" % r.status)

    if secret_known:
        denied("J03", "Token vencido (exp en el pasado, firma válida)",
               http("GET", "/users/%s" % A["id"], token=forge(claims(A["email"], A["id"], "CLIENTE", -3600), secret)))
    else:
        record("J03", "Token vencido (exp en el pasado, firma válida)", "INCONCLUSO", "requiere conocer el secreto (J00)")

    h, p, s = A["token"].split(".")
    pl = json.loads(b64u_dec(p))
    pl["role"] = "ADMIN"
    tampered = "%s.%s.%s" % (h, b64u(json.dumps(pl, separators=(",", ":")).encode()), s)
    denied("J04", "Token modificado (role=ADMIN en el payload, firma original)", http("GET", "/users", token=tampered))
    denied("J05", "Firma incorrecta (firmado con otra clave)",
           http("GET", "/users/%s" % A["id"], token=forge(claims(A["email"], A["id"], "CLIENTE"), "clave-del-atacante-0123456789-abcdef-xyz")))
    denied("J06", "Algoritmo 'none' (token sin firma)",
           http("GET", "/users/%s" % A["id"], token=forge(claims(A["email"], A["id"], "ADMIN"), "", alg="none")))
    if secret_known:
        denied("J07", "Algoritmo no permitido (HS384 con el mismo secreto; RFC 8725 3.1)",
               http("GET", "/users/%s" % A["id"], token=forge(claims(A["email"], A["id"], "CLIENTE"), secret, alg="HS384")))
        denied("J08", "Manipulación de claims con firma válida (role=ADMIN, usuario CLIENTE)",
               http("GET", "/users", token=forge(claims(A["email"], A["id"], "ADMIN"), secret)))
        denied("J09", "Token válido de usuario inexistente/eliminado",
               http("GET", "/users/%s" % A["id"], token=forge(claims("noexiste.%s@example.test" % rnd(), 999999, "CLIENTE"), secret)))
    else:
        for tid, n in (("J07", "Algoritmo no permitido (HS384)"), ("J08", "Manipulación de claims con firma válida"),
                       ("J09", "Token válido de usuario inexistente/eliminado")):
            record(tid, n, "INCONCLUSO", "requiere conocer el secreto (J00)")

    lg = http("POST", "/users/logout", token=A["token"])
    if lg.status in (200, 204):
        record("J10", "Revocación / cierre de sesión en servidor", "INFO",
               "existe POST /users/logout (HTTP %d). Verifica manualmente que el token anterior quede invalidado." % lg.status)
    else:
        record("J10", "Revocación / cierre de sesión en servidor", "INFO",
               "no hay endpoint de logout (HTTP %d) ni lista de revocación: un token robado sigue válido hasta que expire." % lg.status)
    c = pl.copy()
    c["role"] = "CLIENTE"
    faltan = [k for k in ("iss", "aud", "nbf") if k not in c]
    vida = (c.get("exp", 0) - c.get("iat", 0)) // 60
    record("J11", "Contenido del payload del JWT (no está cifrado)", "INFO",
           "claims=%s; faltan=%s; vida=%d min" % (sorted(c.keys()), faltan, vida))

    # ---------------- Autorización: users-service ----------------
    print("\n== Autorización: users-service ==")
    denied_no_leak("A01", "IDOR: B lee el perfil de A (GET /users/{idA})",
                   http("GET", "/users/%s" % A["id"], token=B["token"]), A["email"])
    rput = http("PUT", "/users/%s" % A["id"], token=B["token"],
                body={"nombre": "Modificado por B", "email": A["email"], "password": PASSWORD})
    despues = http("GET", "/users/%s" % A["id"], token=A["token"])
    cambiado = despues.status == 200 and despues.json and despues.json.get("nombre") == "Modificado por B"
    if cambiado:
        record("A02", "IDOR: B modifica el perfil de A (PUT /users/{idA})", "VULN", "el perfil de A fue modificado por B (HTTP %d)" % rput.status)
    elif rput.status == 0 or despues.status == 0:
        record("A02", "IDOR: B modifica el perfil de A (PUT /users/{idA})", "INCONCLUSO", "sin respuesta")
    elif rput.status >= 500:
        record("A02", "IDOR: B modifica el perfil de A (PUT /users/{idA})", "VULN", "HTTP %d: error no controlado" % rput.status)
    else:
        record("A02", "IDOR: B modifica el perfil de A (PUT /users/{idA})", "OK",
               "el perfil de A no cambió; respuesta HTTP %d%s" % (rput.status, "" if rput.status in (401, 403) else " (lo ideal es 403)"))
    denied("A03", "Escalamiento vertical: CLIENTE lista todos los usuarios (GET /users)", http("GET", "/users", token=B["token"]))

    email_c = "auditoria.c.%s@example.test" % rnd()
    r = http("POST", "/users", body={"nombre": "Auditoria C", "email": email_c, "password": PASSWORD, "rol": "ADMIN"})
    if r.status == 201 and r.json:
        ok_create = r.json.get("rol") == "CLIENTE"
        l = http("POST", "/users/login", body={"email": email_c, "password": PASSWORD})
        ok_update = True
        if l.status == 200 and l.json:
            u = http("PUT", "/users/%s" % l.json["id"], token=l.json["token"],
                     body={"nombre": "Auditoria C", "email": email_c, "password": PASSWORD, "rol": "ADMIN"})
            ok_update = (u.status == 200 and u.json and u.json.get("rol") == "CLIENTE") or u.status in (401, 403)
            cleanup.append(("DELETE", "/users/%s" % l.json["id"], l.json["token"]))
        record("A04", "Mass assignment del rol (registro y actualización con rol=ADMIN)",
               "OK" if (ok_create and ok_update) else "VULN",
               "rol en registro=%s" % r.json.get("rol"))
    else:
        record("A04", "Mass assignment del rol (registro con rol=ADMIN)", "INCONCLUSO", "HTTP %d" % r.status)

    # ---------------- Autorización: turnos ----------------
    print("\n== Autorización: turnos-service ==")
    r = http("GET", "/turnos")
    if r.status == 200:
        n = len(r.json) if isinstance(r.json, list) else "?"
        record("A05", "Listar TODOS los turnos sin autenticación (GET /turnos)", "VULN", "HTTP 200, %s registros expuestos" % n)
    else:
        denied("A05", "Listar TODOS los turnos sin autenticación (GET /turnos)", r)

    ta = http("POST", "/turnos", token=A["token"], body=turno_body(A["id"]))
    tid = ta.json.get("idTurno") if ta.status == 201 and ta.json else None
    if tid:
        cleanup.append(("DELETE", "/turnos/%s" % tid, A["token"]))
    spoof = http("POST", "/turnos", token=B["token"], body=turno_body(A["id"]))
    if spoof.status == 201 and spoof.json:
        cleanup.append(("DELETE", "/turnos/%s" % spoof.json.get("idTurno"), B["token"]))
        if spoof.json.get("idUsuario") == A["id"]:
            record("A06", "BOLA: B crea un turno a nombre de A (idUsuario tomado del cuerpo)", "VULN",
                   "HTTP 201 y el turno quedó a nombre de A: el servidor confía en el idUsuario del cliente")
        else:
            record("A06", "BOLA: B crea un turno a nombre de A (idUsuario tomado del cuerpo)", "OK",
                   "HTTP 201 pero el turno quedó a nombre de %s (se usa la identidad del token)" % spoof.json.get("idUsuario"))
    else:
        denied("A06", "BOLA: B crea un turno a nombre de A (idUsuario tomado del cuerpo)", spoof)

    if tid:
        r = http("GET", "/turnos/usuario/%s" % A["id"], token=B["token"])
        if r.status == 200:
            record("A07", "BOLA: B lee los turnos de A (GET /turnos/usuario/{idA})", "VULN", "HTTP 200, datos de A visibles para B")
        else:
            denied("A07", "BOLA: B lee los turnos de A (GET /turnos/usuario/{idA})", r)
        denied("A07b", "BOLA: B lee un turno de A por id (GET /turnos/{id})", http("GET", "/turnos/%s" % tid, token=B["token"]))
        body = turno_body(B["id"])
        denied("A08", "BOLA: B reasigna/edita el turno de A (PUT /turnos/{id})", http("PUT", "/turnos/%s" % tid, token=B["token"], body=body))
        denied("A08b", "BOLA: B cancela el turno de A (PUT /turnos/cancelar/{id})", http("PUT", "/turnos/cancelar/%s" % tid, token=B["token"]))
        denied("A08c", "BOLA: B elimina el turno de A (DELETE /turnos/{id})", http("DELETE", "/turnos/%s" % tid, token=B["token"]))
    else:
        for t_, n_ in (("A07", "B lee turnos de A"), ("A08", "B edita turno de A")):
            record(t_, "BOLA: " + n_, "INCONCLUSO", "no se pudo crear un turno legítimo de A (HTTP %d)" % ta.status)

    # ---------------- Autorización: notifications ----------------
    print("\n== Autorización: notifications-service ==")
    r = http("GET", "/notifications")
    if r.status == 200:
        record("A09", "Listar TODAS las notificaciones sin autenticación", "VULN",
               "HTTP 200, %s registros" % (len(r.json) if isinstance(r.json, list) else "?"))
    else:
        denied("A09", "Listar TODAS las notificaciones sin autenticación", r)
    nb = {"idUsuario": A["id"], "titulo": "Prueba auditoria", "mensaje": "mensaje de prueba", "tipo": "INFO"}
    na = http("POST", "/notifications", token=A["token"], body=nb)
    nid = na.json.get("id") if na.status == 201 and na.json else None
    if nid:
        cleanup.append(("DELETE", "/notifications/%s" % nid, A["token"]))
    rn = http("POST", "/notifications", token=B["token"], body=nb)
    if rn.status == 201 and rn.json:
        cleanup.append(("DELETE", "/notifications/%s" % rn.json.get("id"), B["token"]))
        if rn.json.get("idUsuario") == A["id"]:
            record("A09b", "B crea una notificación falsa para A", "VULN", "HTTP 201 y quedó a nombre de A: cualquiera puede suplantar notificaciones")
        else:
            record("A09b", "B crea una notificación falsa para A", "OK", "HTTP 201 pero a nombre de %s (se usa la identidad del token)" % rn.json.get("idUsuario"))
    else:
        denied("A09b", "B crea una notificación falsa para A", rn)
    if nid:
        denied("A09c", "B marca como leída la notificación de A", http("PUT", "/notifications/%s/leida" % nid, token=B["token"]))
        denied("A09d", "B elimina la notificación de A", http("DELETE", "/notifications/%s" % nid, token=B["token"]))
    else:
        record("A09c", "B marca como leída la notificación de A", "INCONCLUSO", "no se pudo crear una notificación legítima de A (HTTP %d)" % na.status)

    # ---------------- Autorización: audit ----------------
    print("\n== Autorización: audit-service ==")
    r = http("GET", "/audit")
    if r.status == 200:
        record("A10", "Leer TODA la auditoría sin autenticación", "VULN",
               "HTTP 200, %s registros" % (len(r.json) if isinstance(r.json, list) else "?"))
    else:
        denied("A10", "Leer TODA la auditoría sin autenticación", r)
    ev = {"idUsuario": A["id"], "accion": "EVENTO_FORJADO_PRUEBA", "descripcion": "registro creado por la batería de pruebas",
          "servicioOrigen": "security_tests"}
    ra = http("POST", "/audit", body=ev)
    aid = ra.json.get("id") if ra.status == 201 and ra.json else None
    if aid:
        record("A10b", "Falsificar eventos de auditoría sin autenticación (POST /audit)", "VULN", "HTTP 201")
        d = http("DELETE", "/audit/%s" % aid)
        if d.status in (200, 204):
            record("A10c", "Borrar registros de auditoría sin autenticación (DELETE /audit/{id})", "VULN", "HTTP %d" % d.status)
        else:
            denied("A10c", "Borrar registros de auditoría sin autenticación (DELETE /audit/{id})", d)
            cleanup.append(("DELETE", "/audit/%s" % aid, A["token"]))
    else:
        denied("A10b", "Falsificar eventos de auditoría sin autenticación (POST /audit)", ra)

    host = urllib.parse.urlparse(BASE).hostname or "localhost"
    abiertos = []
    for port in (8081, 8082, 8083, 8084, 8281, 8282, 8283, 8284, 5433, 5434, 5435, 5453, 5454, 5455, 27017, 27019):
        s = socket.socket()
        s.settimeout(0.6)
        if s.connect_ex((host, port)) == 0:
            abiertos.append(port)
        s.close()
    record("A11", "Servicios y bases de datos accesibles directamente (saltándose el gateway)",
           "VULN" if abiertos else "OK", "puertos abiertos en %s: %s" % (host, abiertos or "ninguno"))

    # ---------------- Cuentas, errores, fuerza bruta ----------------
    print("\n== Cuentas, errores y fuerza bruta ==")
    r = http("POST", "/users", body={"nombre": "Dup", "email": A["email"], "password": PASSWORD})
    msg = (r.json or {}).get("error", r.text)[:80]
    record("I01", "Enumeración de usuarios por registro duplicado", "VULN" if "existe" in msg.lower() else "OK", "respuesta: %r" % msg)

    def t_login(email):
        t0 = time.perf_counter()
        http("POST", "/users/login", body={"email": email, "password": "Incorrecta#2026"})
        return time.perf_counter() - t0
    t_ex = statistics.median([t_login(A["email"]) for _ in range(5)])
    t_no = statistics.median([t_login("noexiste.%s@example.test" % rnd()) for _ in range(5)])
    ratio = t_ex / t_no if t_no > 0 else 0
    record("I02", "Enumeración de usuarios por tiempo de respuesta en login",
           "VULN" if ratio >= 5 else ("OK" if ratio < 2 else "INFO"), "mediana usuario existente=%.0f ms, inexistente=%.0f ms (x%.1f)" % (t_ex * 1000, t_no * 1000, ratio))

    r1 = http("POST", "/users", raw=b'{"nombre": "x", ')
    r2 = http("GET", "/turnos/abc", token=A["token"])
    leaks = [m for m in ("org.springframework", "Exception", "at com.", "stackTrace", "jdbc", "hibernate")
             if m.lower() in (r1.text + r2.text).lower()]
    record("I03", "Fuga de información en mensajes de error", "VULN" if leaks else "OK",
           "marcas internas halladas: %s (HTTP %d / %d)" % (leaks, r1.status, r2.status) if leaks else "HTTP %d / %d sin trazas internas" % (r1.status, r2.status))

    codigos = [http("POST", "/users/login", body={"email": B["email"], "password": "Mala#%d" % i}).status for i in range(25)]
    record("I04", "Fuerza bruta: 25 intentos de login fallidos seguidos",
           "OK" if 429 in codigos else "VULN",
           "códigos=%s" % sorted(set(codigos)) + ("" if 429 in codigos else " (sin bloqueo ni limitación de tasa)"))

    # ---------------- Inyección ----------------
    print("\n== Inyección ==")
    r = http("POST", "/users/login", body={"email": "admin@example.test' OR '1'='1", "password": "x' OR '1'='1"})
    record("I05", "SQL Injection en login (email/password)", "VULN" if r.status == 200 else "OK", "HTTP %d" % r.status)
    r = http("GET", "/turnos/doctores/" + urllib.parse.quote("' OR '1'='1"), token=A["token"])
    record("I06", "SQL Injection en parámetro de ruta (/turnos/doctores/{esp})",
           "OK" if r.status in (200, 400, 401, 403, 404) and r.status < 500 and (r.json in ([], None) or r.status != 200) else "VULN",
           "HTTP %d, respuesta=%s" % (r.status, r.text[:60]))
    r = http("GET", "/audit/accion/" + urllib.parse.quote('{"$ne": null}'), token=A["token"])
    n_resp = len(r.json) if r.status == 200 and isinstance(r.json, list) else 0
    record("I07", "NoSQL Injection en audit ({\"$ne\": null} en ruta)", "VULN" if n_resp > 0 else "OK", "HTTP %d, %d registros devueltos" % (r.status, n_resp))
    xss = {"idUsuario": A["id"], "titulo": "<script>alert(1)</script>", "mensaje": "<img src=x onerror=alert(1)>", "tipo": "INFO"}
    r = http("POST", "/notifications", token=A["token"], body=xss)
    if r.status == 201 and r.json:
        cleanup.append(("DELETE", "/notifications/%s" % r.json.get("id"), A["token"]))
        record("I08", "XSS almacenado: el backend guarda HTML/JS sin sanitizar", "INFO",
               "guardado tal cual (titulo=%r). Riesgo real depende del frontend: confirma que Angular lo escapa y que no se usa [innerHTML]." % r.json.get("titulo"))
    else:
        record("I08", "XSS almacenado: el backend guarda HTML/JS sin sanitizar", "INCONCLUSO", "HTTP %d" % r.status)

    # ---------------- Configuración ----------------
    print("\n== Configuración ==")
    evil = http("OPTIONS", "/users/login", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    acao = evil.header("Access-Control-Allow-Origin")
    record("I09", "CORS: origen no autorizado (https://evil.example)", "VULN" if acao in ("*", "https://evil.example") else "OK", "Access-Control-Allow-Origin=%r" % acao)
    for ep in ("/users/health", "/turnos/especialidades"):
        r = http("GET", ep)
        falt = [h for h in ("X-Content-Type-Options", "X-Frame-Options", "Content-Security-Policy") if not r.header(h)]
        record("I10", "Cabeceras de seguridad en %s" % ep, "VULN" if falt else "OK", "faltan: %s" % (falt or "ninguna"))
    big = {"idUsuario": A["id"], "titulo": "grande", "mensaje": "A" * 300000, "tipo": "INFO"}
    r = http("POST", "/notifications", token=A["token"], body=big)
    if r.status == 201 and r.json:
        cleanup.append(("DELETE", "/notifications/%s" % r.json.get("id"), A["token"]))
        record("I11", "Límite de tamaño de entrada (mensaje de 300 000 caracteres)", "VULN", "HTTP 201: sin límite de longitud")
    elif r.status >= 500:
        record("I11", "Límite de tamaño de entrada (mensaje de 300 000 caracteres)", "VULN",
               "HTTP %d: no hay validación de longitud en la API; el error de la base de datos llega como 500 (debería ser 400)" % r.status)
    else:
        record("I11", "Límite de tamaño de entrada (mensaje de 300 000 caracteres)", "OK" if r.status in (400, 401, 403, 413) else "INCONCLUSO", "HTTP %d" % r.status)

    # ---------------- Limpieza ----------------
    print("\n== Limpieza ==")
    hechos = 0
    for m, path, tok in cleanup:
        rr = http(m, path, token=tok)
        hechos += 1 if rr.status in (200, 204) else 0
    for u in (A, B):
        rr = http("DELETE", "/users/%s" % u["id"], token=u["token"])
        hechos += 1 if rr.status in (200, 204) else 0
    print("Elementos de prueba eliminados: %d de %d (el resto ya no existía o el servidor rechazó borrarlo)" % (hechos, len(cleanup) + 2))


def main():
    global BASE
    ap = argparse.ArgumentParser(description="Batería de pruebas de seguridad (solo entornos locales/autorizados)")
    ap.add_argument("--base", default="http://localhost:8280", help="URL del api-gateway (main=8280, develop=8080)")
    ap.add_argument("--secret", default=os.environ.get("JWT_SECRET", DEFAULT_SECRET), help="secreto JWT a probar (por defecto el del código)")
    ap.add_argument("--out", default="resultados.json", help="archivo JSON de resultados")
    ap.add_argument("--autorizado", action="store_true", help="confirma que el host no local es tuyo y está autorizado para pruebas")
    args = ap.parse_args()
    BASE = args.base.rstrip("/")
    host = urllib.parse.urlparse(BASE).hostname
    if host not in ("localhost", "127.0.0.1", "::1", "host.docker.internal") and not args.autorizado:
        print("Rechazado: %s no es un host local. Usa --autorizado solo si el sistema es tuyo y tienes permiso." % host)
        sys.exit(2)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print("Objetivo: %s\nInicio: %s\n" % (BASE, datetime.now().isoformat(timespec="seconds")))
    if http("GET", "/users/health").status == 0:
        print("No hay respuesta del gateway en %s. ¿Están levantados los contenedores?" % BASE)
        sys.exit(3)
    run(args)
    resumen = {}
    for x in RESULTS:
        resumen[x["estado"]] = resumen.get(x["estado"], 0) + 1
    print("\n== Resumen ==\n%s" % json.dumps(resumen, ensure_ascii=False))
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"objetivo": BASE, "fecha": datetime.now().isoformat(timespec="seconds"), "resumen": resumen, "resultados": RESULTS},
                  f, ensure_ascii=False, indent=2)
    print("Resultados guardados en %s" % args.out)
    sys.exit(1 if resumen.get("VULN") else 0)


if __name__ == "__main__":
    main()

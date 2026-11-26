from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from html import escape


# ==========================================
# 1. CATÁLOGO DE POSTRES
# ==========================================

CATALOGO = {
    "tres_capas": {
        "nombre": "Copa Tres Capas",
        "precio": 9000,
        "costo": 4800
    },
    "oreo": {
        "nombre": "Mousse de Oreo",
        "precio": 8000,
        "costo": 4200
    },
    "fresa": {
        "nombre": "Cheesecake de fresa en vasito",
        "precio": 8000,
        "costo": 4300
    },
    "cafe": {
        "nombre": "Mousse de café con crema",
        "precio": 8500,
        "costo": 4500
    },
    "chocolate": {
        "nombre": "Mousse de chocolate crocante",
        "precio": 8500,
        "costo": 4600
    },
    "pina_coco": {
        "nombre": "Postre de piña y coco",
        "precio": 8000,
        "costo": 4100
    }
}


# ==========================================
# 2. REGLAS DE DESCUENTO
# ==========================================

CODIGO_PROMO = "DULCE10"
DESCUENTO_CODIGO = 0.10

UNIDADES_COMBO = 6
DESCUENTO_COMBO = 0.08


# ==========================================
# 3. FUNCIONES AUXILIARES
# ==========================================

def formato_pesos(valor):
    """Convierte un valor numérico a pesos colombianos."""
    return "$" + f"{round(valor):,}".replace(",", ".")


def calcular_pedido(clave, cantidad, codigo=""):
    """Calcula el valor del pedido y la ganancia estimada."""

    # Validar el producto
    if clave not in CATALOGO:
        raise ValueError("Por favor selecciona un postre.")

    # Validar la cantidad
    if cantidad < 1:
        raise ValueError("La cantidad debe ser mínimo 1.")

    if cantidad > 500:
        raise ValueError(
            "Para pedidos de más de 500 unidades escríbenos por WhatsApp."
        )

    postre = CATALOGO[clave]

    # Calcular subtotal
    subtotal = postre["precio"] * cantidad

    # Aplicar descuentos
    porcentaje = 0
    avisos = []

    if cantidad >= UNIDADES_COMBO:
        porcentaje += DESCUENTO_COMBO
        avisos.append(
            "Combo aplicado: 8% de descuento por llevar 6 o más."
        )

    codigo = codigo.strip().upper()

    if codigo == CODIGO_PROMO:
        porcentaje += DESCUENTO_CODIGO
        avisos.append(
            "Código DULCE10 aplicado: 10% de descuento."
        )
    elif codigo != "":
        avisos.append("El código ingresado no es válido.")

    # Calcular descuento y total
    descuento = subtotal * porcentaje
    total = subtotal - descuento

    # Calcular costo y ganancia
    costo_total = postre["costo"] * cantidad
    ganancia = total - costo_total

    # Calcular margen
    margen = (ganancia / total) * 100

    return {
        "nombre": postre["nombre"],
        "cantidad": cantidad,
        "subtotal": subtotal,
        "porcentaje_descuento": porcentaje * 100,
        "descuento": descuento,
        "total": total,
        "costo_total": costo_total,
        "ganancia": ganancia,
        "margen": margen,
        "avisos": avisos,
        "codigo_invalido": codigo != "" and codigo != CODIGO_PROMO
    }


# ==========================================
# 4. CONSTRUIR EL RESULTADO HTML
# ==========================================

def mostrar_resultado(pedido, modo_emprendedora):

    avisos = "".join(
        f"<br>{escape(aviso)}"
        for aviso in pedido["avisos"]
    )

    clase = "error" if pedido["codigo_invalido"] else "ok"

    ganancia_html = ""

    if modo_emprendedora:
        ganancia_html = f"""
            <div class="bloque-ganancia">
                <p class="res-linea">
                    <span>Costo estimado</span>
                    <span>{formato_pesos(pedido["costo_total"])}</span>
                </p>

                <p class="res-linea">
                    <span>Ganancia estimada</span>
                    <strong>{formato_pesos(pedido["ganancia"])}</strong>
                </p>

                <p class="res-linea">
                    <span>Margen</span>
                    <strong>{pedido["margen"]:.0f}%</strong>
                </p>
            </div>
        """

    return f"""
        <p class="res-etiqueta">Postre seleccionado</p>

        <strong class="res-producto">
            {pedido["cantidad"]} x {escape(pedido["nombre"])}
        </strong>

        <hr>

        <p class="res-linea">
            <span>Subtotal</span>
            <span>{formato_pesos(pedido["subtotal"])}</span>
        </p>

        <p class="res-linea">
            <span>Descuento ({pedido["porcentaje_descuento"]:.0f}%)</span>
            <span>-{formato_pesos(pedido["descuento"])}</span>
        </p>

        <p class="res-total-etiqueta">Valor total</p>

        <span class="valor-total">
            {formato_pesos(pedido["total"])}
        </span>

        {ganancia_html}

        <p class="mensaje-calculadora {clase}">
            Valor estimado de tu pedido.
            {avisos}
            <br>
            Escríbenos por WhatsApp para confirmar tu pedido.
        </p>
    """


def mostrar_error(mensaje):
    return f"""
        <p class="res-etiqueta">Postre seleccionado</p>

        <strong class="res-producto">
            No se pudo calcular el pedido
        </strong>

        <hr>

        <p class="res-total-etiqueta">Valor total</p>

        <span class="valor-total">$0</span>

        <p class="mensaje-calculadora error">
            {escape(mensaje)}
        </p>
    """


# ==========================================
# 5. RESPUESTA DEL SERVIDOR
# ==========================================

class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        longitud = int(self.headers.get("Content-Length", 0))

        datos = self.rfile.read(longitud).decode("utf-8")

        formulario = parse_qs(datos)

        producto = formulario.get("producto", [""])[0]

        cantidad_texto = formulario.get("cantidad", ["1"])[0]

        codigo = formulario.get("codigo", [""])[0]

        modo_emprendedora = (
            formulario.get("modo", [""])[0] == "on"
        )

        try:
            cantidad = int(cantidad_texto)

            pedido = calcular_pedido(
                producto,
                cantidad,
                codigo
            )

            resultado = mostrar_resultado(
                pedido,
                modo_emprendedora
            )

        except ValueError as error:
            resultado = mostrar_error(str(error))

        except (TypeError, OverflowError):
            resultado = mostrar_error(
                "Ocurrió un problema con los datos ingresados."
            )

        self.responder(resultado)

    def responder(self, resultado):

        pagina = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <title>Resultado de tu pedido | Dulce Antojo Casero</title>

            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

            <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@600;700&family=Fraunces:wght@600;700&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">

            <link rel="stylesheet" href="/css/styles.css">
        </head>

        <body>

            <main class="seccion calculadora">

                <div class="seccion-encabezado">
                    <span class="etiqueta">Dulce Antojo Casero</span>
                    <h2>Resultado de tu pedido</h2>
                    <p>Este es el resumen de tu cotización.</p>
                </div>

                <div class="calculadora-contenedor">

                    <div class="resultado-calculadora">

                        <h3>Resumen de tu pedido</h3>

                        {resultado}

                        <a href="/#calculadora" class="boton">
                            Volver a la calculadora
                        </a>

                    </div>

                </div>

            </main>

        </body>
        </html>
        """

        datos = pagina.encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()

        self.wfile.write(datos)
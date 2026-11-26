

# ----------------------------------------------------------------
# 1. DATOS: catálogo de postres (precios y costos en pesos colombianos)
#    clave -> {nombre, precio de venta, costo de producción}
#    Cambia estos valores por los reales de tu negocio.
# ----------------------------------------------------------------
CATALOGO = {
    "tres_capas": {"nombre": "Copa Tres Capas", "precio": 9000, "costo": 4800},
    "oreo":       {"nombre": "Mousse de Oreo", "precio": 8000, "costo": 4200},
    "fresa":      {"nombre": "Cheesecake de fresa en vasito", "precio": 8000, "costo": 4300},
    "cafe":       {"nombre": "Mousse de café con crema", "precio": 8500, "costo": 4500},
    "chocolate":  {"nombre": "Mousse de chocolate crocante", "precio": 8500, "costo": 4600},
    "pina_coco":  {"nombre": "Postre de piña y coco", "precio": 8000, "costo": 4100},
}

# ----------------------------------------------------------------
# 2. REGLAS DE DESCUENTO
# ----------------------------------------------------------------
CODIGO_PROMO = "DULCE10"      # código del primer pedido
DESCUENTO_CODIGO = 0.10       # 10 %
UNIDADES_COMBO = 6            # a partir de 6 postres...
DESCUENTO_COMBO = 0.08        # ...se aplica 8 %


def formato_pesos(valor):
    """Convierte 45000 en '$45.000'."""
    return "$" + f"{round(valor):,}".replace(",", ".")


def calcular_pedido(clave, cantidad, codigo=""):
    """
    Algoritmo de la calculadora:
      1. Validar los datos.
      2. Calcular el subtotal  = precio x cantidad.
      3. Aplicar los descuentos (combo y/o código).
      4. Calcular total, costo y ganancia.
      5. Devolver todo en un diccionario.
    Si algún dato es incorrecto lanza ValueError con un mensaje claro.
    """
    # 1. Validar
    if clave not in CATALOGO:
        raise ValueError("Por favor selecciona un postre.")
    if cantidad < 1:
        raise ValueError("La cantidad debe ser mínimo 1.")
    if cantidad > 500:
        raise ValueError("Para pedidos de más de 500 unidades escríbenos por WhatsApp.")

    postre = CATALOGO[clave]

    # 2. Subtotal
    subtotal = postre["precio"] * cantidad

    # 3. Descuentos (se suman)
    porcentaje = 0.0
    avisos = []

    if cantidad >= UNIDADES_COMBO:
        porcentaje += DESCUENTO_COMBO
        avisos.append("Combo aplicado: 8% de descuento por llevar 6 o más.")

    codigo = codigo.strip().upper()
    if codigo == CODIGO_PROMO:
        porcentaje += DESCUENTO_CODIGO
        avisos.append("Código DULCE10 aplicado: 10% de descuento.")
    elif codigo != "":
        avisos.append("El código ingresado no es válido.")

    # 4. Totales
    descuento = subtotal * porcentaje
    total = subtotal - descuento
    costo_total = postre["costo"] * cantidad
    ganancia = total - costo_total
    margen = ganancia / total * 100

    # 5. Resultado
    return {
        "clave": clave,
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
        "codigo_invalido": codigo != "" and codigo != CODIGO_PROMO,
    }


if __name__ == "__main__":
    # Prueba rápida desde la terminal:  python calculadora.py
    pedido = calcular_pedido("oreo", 6, "dulce10")
    print(pedido["nombre"], "x", pedido["cantidad"])
    print("Subtotal:", formato_pesos(pedido["subtotal"]))
    print("Descuento:", formato_pesos(pedido["descuento"]))
    print("Total:", formato_pesos(pedido["total"]))
    print("Ganancia:", formato_pesos(pedido["ganancia"]))


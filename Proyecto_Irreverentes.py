import random
import numpy as np
import matplotlib.pyplot as plt
import itertools
import tkinter as tk
from tkinter import ttk, messagebox

# Parámetros iniciales
tamano_poblacion = 20
generaciones = 50
tasa_mutacion = 0.05
deposito = 0

# Función de distancia euclidiana
def distancia(punto1, punto2):
    return np.sqrt(np.sum((punto1 - punto2) ** 2))

# Evaluación de aptitud (fitness)
def calcular_aptitud(rutas, ubicaciones):
    distancia_total = 0
    for ruta in rutas:
        if len(ruta) > 0:
            distancia_total += distancia(ubicaciones[deposito], ubicaciones[ruta[0]])
            for i in range(len(ruta) - 1):
                distancia_total += distancia(ubicaciones[ruta[i]], ubicaciones[ruta[i + 1]])
            distancia_total += distancia(ubicaciones[ruta[-1]], ubicaciones[deposito])
    return distancia_total

# Fuerza Bruta para VRP
def fuerza_bruta_vrp(clientes, num_vehiculos, ubicaciones):
    mejor_distancia = float('inf')
    mejor_solucion = None
    for perm in itertools.permutations(clientes):
        for puntos_division in itertools.combinations(range(1, len(clientes)), num_vehiculos - 1):
            rutas = [list(perm[i:j]) for i, j in zip((0,) + puntos_division, puntos_division + (len(clientes),))]
            distancia_total = calcular_aptitud(rutas, ubicaciones)
            if distancia_total < mejor_distancia:
                mejor_distancia = distancia_total
                mejor_solucion = rutas
    return mejor_solucion, mejor_distancia

# Algoritmo Voraz para VRP
def voraz_vrp(clientes, num_vehiculos, ubicaciones):
    rutas = [[] for _ in range(num_vehiculos)]
    clientes_restantes = set(clientes)
    indices_vehiculos = list(range(num_vehiculos))
    
    # Inicializar rutas con el depósito
    for ruta in rutas:
        ruta.append(deposito)
    
    while clientes_restantes:
        for vehiculo in indices_vehiculos:
            if not clientes_restantes:
                break
            ubicacion_actual = rutas[vehiculo][-1]
            cliente_mas_cercano = min(clientes_restantes, key=lambda x: distancia(ubicaciones[ubicacion_actual], ubicaciones[x]))
            rutas[vehiculo].append(cliente_mas_cercano)
            clientes_restantes.remove(cliente_mas_cercano)
    
    # Añadir el depósito al final de cada ruta
    for ruta in rutas:
        ruta.append(deposito)
    
    # Quitar el depósito inicial de cada ruta para evitar duplicaciones
    for ruta in rutas:
        if ruta[0] == deposito:
            ruta.pop(0)
    
    return rutas

# Inicialización de la población
def crear_poblacion_inicial(num_clientes, num_vehiculos):
    poblacion = []
    for _ in range(tamano_poblacion):
        clientes = list(range(1, num_clientes + 1))
        random.shuffle(clientes)
        puntos_division = sorted(random.sample(range(1, num_clientes), num_vehiculos - 1))
        individuo = [clientes[i:j] for i, j in zip([0] + puntos_division, puntos_division + [num_clientes])]
        poblacion.append(individuo)
    return poblacion

# Selección aleatoria
def seleccion_aleatoria(poblacion):
    return random.choice(poblacion)

# Cruzamiento de orden corregido
def cruzamiento(padre1, padre2):
    tamano = sum(len(ruta) for ruta in padre1)
    corte1, corte2 = sorted(random.sample(range(tamano), 2))

    def aplanar(padre):
        return [item for sublist in padre for item in sublist]

    def des_aplanar(lista_planar, longitudes):
        resultado = []
        idx = 0
        for longitud in longitudes:
            resultado.append(lista_planar[idx:idx + longitud])
            idx += longitud
        return resultado

    segmento1 = aplanar(padre1)[corte1:corte2]
    segmento2 = aplanar(padre2)[corte1:corte2]

    def crear_hijo(segmento, padre):
        padre_planar = aplanar(padre)
        nuevo_planar = [item for item in padre_planar if item not in segmento]
        nuevo_planar[corte1:corte1] = segmento
        longitudes = [len(ruta) for ruta in padre]
        return des_aplanar(nuevo_planar, longitudes)

    hijo1 = crear_hijo(segmento2, padre1)
    hijo2 = crear_hijo(segmento1, padre2)

    return hijo1, hijo2

# Mutación sencilla sin duplicados
def mutacion(individuo):
    if random.random() < tasa_mutacion:
        ruta1, ruta2 = random.sample(individuo, 2)
        if ruta1 and ruta2:
            i, j = random.randint(0, len(ruta1) - 1), random.randint(0, len(ruta2) - 1)
            ruta1[i], ruta2[j] = ruta2[j], ruta1[i]

# Algoritmo Genético
def algoritmo_genetico(num_clientes, num_vehiculos, ubicaciones):
    poblacion = crear_poblacion_inicial(num_clientes, num_vehiculos)
    for generacion in range(generaciones):
        nueva_poblacion = []
        for _ in range(tamano_poblacion // 2):
            padre1 = seleccion_aleatoria(poblacion)
            padre2 = seleccion_aleatoria(poblacion)
            hijo1, hijo2 = cruzamiento(padre1, padre2)
            mutacion(hijo1)
            mutacion(hijo2)
            nueva_poblacion.extend([hijo1, hijo2])
        poblacion = nueva_poblacion
        mejor_individuo = min(poblacion, key=lambda ind: calcular_aptitud(ind, ubicaciones))
    return mejor_individuo, calcular_aptitud(mejor_individuo, ubicaciones)

# Función para graficar las soluciones
def graficar_soluciones(soluciones, ubicaciones, titulos):
    plt.figure(figsize=(15, 5))
    for idx, (solucion, titulo) in enumerate(zip(soluciones, titulos), 1):
        plt.subplot(1, len(soluciones), idx)
        ubicacion_deposito = ubicaciones[deposito]
        plt.scatter(ubicacion_deposito[0], ubicacion_deposito[1], c='red', label='Depósito')
        plt.scatter(ubicaciones[1:, 0], ubicaciones[1:, 1], c='blue', label='Clientes')

        for i, ruta in enumerate(solucion):
            ubicaciones_ruta = [ubicaciones[deposito]] + [ubicaciones[cliente] for cliente in ruta] + [ubicaciones[deposito]]
            plt.plot([ubicacion[0] for ubicacion in ubicaciones_ruta], [ubicacion[1] for ubicacion in ubicaciones_ruta], label=f'Vehículo {i + 1}')
        
        plt.legend()
        plt.xlabel('Coordenada X')
        plt.ylabel('Coordenada Y')
        plt.title(titulo)
    plt.tight_layout()
    plt.show()

# Función para resolver el VRP y mostrar los resultados
def resolver_vrp(num_clientes, num_vehiculos):
    # Generar ubicaciones de clientes aleatorias
    ubicaciones = np.random.rand(num_clientes + 1, 2)
    
    # Resolver usando fuerza bruta
    clientes = list(range(1, num_clientes + 1))
    mejor_solucion_fuerza_bruta, mejor_distancia_fuerza_bruta = fuerza_bruta_vrp(clientes, num_vehiculos, ubicaciones)

    # Resolver usando algoritmo voraz
    mejor_solucion_voraz = voraz_vrp(clientes, num_vehiculos, ubicaciones)
    mejor_distancia_voraz = calcular_aptitud(mejor_solucion_voraz, ubicaciones)

    # Resolver usando algoritmo genético
    mejor_solucion_genetico, mejor_distancia_genetico = algoritmo_genetico(num_clientes, num_vehiculos, ubicaciones)
    
    # Crear ventana para mostrar resultados
    ventana_resultados = tk.Toplevel()
    ventana_resultados.title("Resultados VRP")
    ventana_resultados.geometry("600x400")
    
    # Mostrar resultados de fuerza bruta
    tk.Label(ventana_resultados, text=f"Fuerza Bruta: Distancia = {mejor_distancia_fuerza_bruta}", font=("Arial", 12)).pack()
    tk.Label(ventana_resultados, text=f"Solución: {mejor_solucion_fuerza_bruta}", font=("Arial", 10)).pack()
    
    # Mostrar resultados de algoritmo voraz
    tk.Label(ventana_resultados, text=f"\n\nVoraz: Distancia = {mejor_distancia_voraz}", font=("Arial", 12)).pack()
    tk.Label(ventana_resultados, text=f"Solución: {mejor_solucion_voraz}", font=("Arial", 10)).pack()
    
    # Mostrar resultados de algoritmo genético
    tk.Label(ventana_resultados, text=f"\n\nGenético: Distancia = {mejor_distancia_genetico}", font=("Arial", 12)).pack()
    tk.Label(ventana_resultados, text=f"Solución: {mejor_solucion_genetico}\n\n\n", font=("Arial", 10)).pack()
    
    # Botón para graficar todas las soluciones
    tk.Button(ventana_resultados, text="Graficar Soluciones", command=lambda: graficar_soluciones(
        [mejor_solucion_fuerza_bruta, mejor_solucion_voraz, mejor_solucion_genetico],
        ubicaciones,
        ["Fuerza Bruta", "Voraz", "Genético"]
    )).pack()

# Función principal para crear la interfaz gráfica
def main():
    ventana = tk.Tk()
    ventana.title("VRP Solver")
    ventana.geometry("300x200")

    # Variables para número de clientes y vehículos
    num_clientes_var = tk.IntVar(value=5)
    num_vehiculos_var = tk.IntVar(value=2)

    # Widgets para ingresar datos
    tk.Label(ventana, text="Número de Clientes:", font=("Arial", 12)).pack(pady=10)
    tk.Entry(ventana, textvariable=num_clientes_var, font=("Arial", 12)).pack()
    
    tk.Label(ventana, text="Número de Vehículos:", font=("Arial", 12)).pack(pady=10)
    tk.Entry(ventana, textvariable=num_vehiculos_var, font=("Arial", 12)).pack()
    
    # Botón para resolver el VRP
    tk.Button(ventana, text="Resolver", command=lambda: resolver_vrp(num_clientes_var.get(), num_vehiculos_var.get())).pack(pady=20)

    ventana.mainloop()

if __name__ == "__main__":
    main()

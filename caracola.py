import numpy as np

# Parámetros del MDP
num_estados = 4
num_acciones = 4
factor_descuento = 0.9  # Factor de descuento gamma

# Matriz de recompensas (estado x acción)
recompensas = np.array([
    [0, 1, 0, 0],
    [0, 0, 0, 10],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
])

# Matriz de probabilidades de transición (estado x acción x estado_siguiente)
# En este ejemplo, se utiliza una matriz aleatoria para demostración.
# En la práctica, debes proporcionar las probabilidades correctas.
prob_transicion = np.random.rand(num_estados, num_acciones, num_estados)
prob_transicion /= prob_transicion.sum(axis=2, keepdims=True)

# Inicialización de los valores de estado
valores_estado = np.zeros(num_estados)

# Algoritmo de iteración de valor
num_iteraciones = 1000

for iteracion in range(num_iteraciones):
    nuevos_valores_estado = np.zeros(num_estados)
    
    for estado in range(num_estados):
        valores_acciones = np.zeros(num_acciones)
        
        for accion in range(num_acciones):
            valor_accion = recompensas[estado, accion]
            
            for estado_siguiente in range(num_estados):
                valor_accion += factor_descuento * prob_transicion[estado, accion, estado_siguiente] * valores_estado[estado_siguiente]
            
            valores_acciones[accion] = valor_accion
        
        nuevos_valores_estado[estado] = np.max(valores_acciones)
    
    valores_estado = nuevos_valores_estado

# Valores de estado finales
print("Valores de estado finales:")
print(valores_estado)

politica_optima = np.zeros(num_estados, dtype=int)  # Inicializa una política arbitraria

for estado in range(num_estados):
    valores_acciones = np.zeros(num_acciones)
    
    for accion in range(num_acciones):
        valor_accion = recompensas[estado, accion]
        
        for estado_siguiente in range(num_estados):
            valor_accion += factor_descuento * prob_transicion[estado, accion, estado_siguiente] * valores_estado[estado_siguiente]
        
        valores_acciones[accion] = valor_accion
    
    politica_optima[estado] = np.argmax(valores_acciones)

# La política óptima se encuentra en politica_optima
print("Política óptima:")
print(politica_optima)
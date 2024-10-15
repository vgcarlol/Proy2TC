import time
from collections import defaultdict
from gramatica import (
    cargar_gramatica,
    validar_gramatica,
    eliminar_producciones_epsilon,
    eliminar_producciones_unarias
)

def cargar_gramatica_cnf(gramatica):
    reglas = defaultdict(list)
    terminales = set()

    # Procesamos cada producción en la gramática
    for produccion in gramatica:
        no_terminal, cuerpo = produccion.split("->")
        no_terminal = no_terminal.strip()
        alternativas = [tuple(alt.strip().split()) for alt in cuerpo.split('|')]
        reglas[no_terminal].extend(alternativas)

        # Identificar terminales
        for alternativa in alternativas:
            for simbolo in alternativa:
                if simbolo.islower() or not simbolo.isalnum():
                    terminales.add(simbolo)

    # Asegurar que cada terminal tenga su propia regla
    for terminal in terminales:
        reglas[terminal] = [(terminal,)]

    return reglas

def cyk_algorithm(grammar, sentence):
    words = sentence.split()
    n = len(words)

    # Crear una tabla CYK de tamaño n x n
    table = [[set() for _ in range(n)] for _ in range(n)]

    # Crear un diccionario inverso para buscar producciones por su cuerpo
    inverse_rules = defaultdict(set)
    for left, right in grammar.items():
        for production in right:
            inverse_rules[production].add(left)

    print("\nReglas inversas:")
    for key, value in inverse_rules.items():
        print(f"{key} -> {value}")

    # Llenar la diagonal de la tabla con las producciones que generan cada palabra
    for j in range(n):
        word = words[j]
        if (word,) in inverse_rules:
            table[j][j] = inverse_rules[(word,)]
        else:
            print(f"Error: La palabra '{word}' no tiene una producción válida.")

    # Llenar el resto de la tabla usando programación dinámica
    for length in range(2, n + 1):  # Longitud de subcadenas
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                for B in table[i][k]:
                    for C in table[k + 1][j]:
                        print(f"Combinando: {B} + {C}")
                        if (B, C) in inverse_rules:
                            print(f"Producción encontrada: {inverse_rules[(B, C)]}")
                            table[i][j].update(inverse_rules[(B, C)])
                            print(f"Actualizando celda [{i},{j}] con: {inverse_rules[(B, C)]}")

    # Verificar si el símbolo inicial 'S' está en la celda [0][n-1]
    pertenece = 'S' in table[0][n - 1]
    return pertenece, table

def ejecutar_cyk(nombre_archivo, frase):
    print(f"\nCargando la gramática desde {nombre_archivo}...")
    gramatica = cargar_gramatica(nombre_archivo)

    if not validar_gramatica(gramatica):
        print("La gramática contiene errores. La ejecución se detiene.")
        return

    print("\nPreprocesando la gramática...")
    cnf = eliminar_producciones_unarias(eliminar_producciones_epsilon(gramatica))
    reglas_cnf = cargar_gramatica_cnf(cnf)

    print(f"\nReglas en CNF después del preprocesamiento:")
    for no_terminal, reglas in reglas_cnf.items():
        print(f"{no_terminal} -> {reglas}")

    print(f"\nValidando la frase: '{frase}'")
    start_time = time.time()
    resultado, tabla = cyk_algorithm(reglas_cnf, frase)
    end_time = time.time()

    if resultado:
        print("Resultado: SÍ, la frase pertenece al lenguaje.")
    else:
        print("Resultado: NO, la frase NO pertenece al lenguaje.")

    print(f"Tiempo de ejecución: {end_time - start_time:.6f} segundos")

    # Mostrar la tabla CYK
    print("\nTabla CYK:")
    for fila in tabla:
        print([list(celda) for celda in fila])

if __name__ == "__main__":
    ejecutar_cyk("gramaticas/gramatica1.txt", "the cat eats")

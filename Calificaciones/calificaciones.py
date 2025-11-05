import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

#archivos CSV por semestre
CSV_FILES = {1: "calificaciones_sem1.csv", 2: "calificaciones_sem2.csv"}

#datos de estudiantes por semestre
datos_semestre = {
    1: {"estudiantes": [], "notas": []},
    2: {"estudiantes": [], "notas": []}
}

#lista semestre de estudiantes
orden_estudiantes = []

semestre_actual = 1

#funciones
def cargar_datos(semestre):
    file = CSV_FILES[semestre]
    datos_semestre[semestre]["estudiantes"].clear()
    datos_semestre[semestre]["notas"].clear()
    if not os.path.exists(file):
        return
    with open(file, "r", encoding="utf-8") as f:
        lector = csv.reader(f)
        next(lector, None)
        for fila in lector:
            if len(fila) >= 9:
                datos_semestre[semestre]["estudiantes"].append(fila[0])
                datos_semestre[semestre]["notas"].append([float(x) if x else None for x in fila[1:9]])
                if fila[0] not in orden_estudiantes:
                    orden_estudiantes.append(fila[0])

def guardar_datos(semestre):
    file = CSV_FILES[semestre]
    with open(file, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["Nombre"] + [f"Asig{i+1}" for i in range(8)] + ["PromSemestre"])
        for i, nombre in enumerate(datos_semestre[semestre]["estudiantes"]):
            fila = [nombre]
            fila.extend(datos_semestre[semestre]["notas"][i])
            prom = calcular_promedio_semestre(datos_semestre[semestre]["notas"][i])
            fila.append(prom)
            escritor.writerow(fila)

def calcular_promedio_semestre(lista_notas):
    """Calcula el promedio de un semestre con 8 notas"""
    notas_validas = [n for n in lista_notas if n is not None]
    return round(sum(notas_validas)/len(notas_validas),2) if notas_validas else 0.0

def actualizar_tabla():
    tabla.delete(*tabla.get_children())
    for i, nombre in enumerate(orden_estudiantes):
        #obtener notas del semestre actual
        if nombre in datos_semestre[semestre_actual]["estudiantes"]:
            idx = datos_semestre[semestre_actual]["estudiantes"].index(nombre)
            notas = datos_semestre[semestre_actual]["notas"][idx]
        else:
            notas = [None]*8

        fila_notas = [f"{n:.2f}" if n is not None else "" for n in notas]

        prom_semestre = calcular_promedio_semestre(notas)

        if semestre_actual == 1:
            fila_tabla = [i+1, nombre] + fila_notas + [f"{prom_semestre:.2f}", "", "", ""]
        else:
            #obtener promedio del semestre 1
            if nombre in datos_semestre[1]["estudiantes"]:
                idx1 = datos_semestre[1]["estudiantes"].index(nombre)
                notas_s1 = datos_semestre[1]["notas"][idx1]
                prom_s1 = calcular_promedio_semestre(notas_s1)
            else:
                prom_s1 = 0

            prom_total = round((prom_s1 + prom_semestre)/2,2)
            estado = "Aprobado" if prom_total >= 7 else "Reprobado"
            fila_tabla = [i+1, nombre] + fila_notas + [f"{prom_s1:.2f}", f"{prom_semestre:.2f}", f"{prom_total:.2f}", estado]

        tabla.insert("", "end", values=fila_tabla)

def registrar_o_editar():
    nombre = entry_nombre.get().strip()
    if not nombre:
        messagebox.showwarning("Error", "Ingrese un nombre válido.")
        return

    if nombre not in orden_estudiantes:
        orden_estudiantes.append(nombre)

    for s in [1,2]:
        if nombre not in datos_semestre[s]["estudiantes"]:
            datos_semestre[s]["estudiantes"].append(nombre)
            datos_semestre[s]["notas"].append([None]*8)

    try:
        valores = []
        for i in range(8):
            valor = entry_asig[i].get().strip()
            if valor == "":
                valores.append(None)
            else:
                n = float(valor)
                if n < 0 or n > 10:
                    raise ValueError
                valores.append(n)
        idx = datos_semestre[semestre_actual]["estudiantes"].index(nombre)
        datos_semestre[semestre_actual]["notas"][idx] = valores
    except ValueError:
        messagebox.showwarning("Error","Ingrese notas válidas (0-10).")
        return

    entry_nombre.delete(0, tk.END)
    for e in entry_asig:
        e.delete(0, tk.END)

    actualizar_tabla()

def editar_notas():
    registrar_o_editar()

def eliminar_estudiante():
    nombre = entry_eliminar.get().strip()
    for s in [1,2]:
        if nombre in datos_semestre[s]["estudiantes"]:
            indice = datos_semestre[s]["estudiantes"].index(nombre)
            datos_semestre[s]["estudiantes"].pop(indice)
            datos_semestre[s]["notas"].pop(indice)
    if nombre in orden_estudiantes:
        orden_estudiantes.remove(nombre)
    entry_eliminar.delete(0, tk.END)
    actualizar_tabla()

def cambiar_semestre():
    global semestre_actual
    guardar_datos(semestre_actual)
    semestre_actual = 2 if semestre_actual == 1 else 1
    cargar_datos(semestre_actual)
    label_semestre.config(text=f"Semestre {semestre_actual}")
    btn_semestre.config(text=f"Ir a Semestre {1 if semestre_actual == 2 else 2}")
    actualizar_tabla()

#interfaz
ventana = tk.Tk()
ventana.title("Registro de Calificaciones")
ventana.geometry("1280x720")
ventana.resizable(False, False)
ventana.configure(bg="#f0f0f0")

tk.Label(ventana, text='Registro de calificaciones de tercero técnico "A"', 
         font=("Arial", 20, "bold"), bg="#f0f0f0").pack(pady=10)
label_semestre = tk.Label(ventana, text=f"Semestre {semestre_actual}", font=("Arial", 16), bg="#f0f0f0")
label_semestre.pack()

frame_inputs = tk.Frame(ventana, bg="#f0f0f0")
frame_inputs.pack(pady=10)

tk.Label(frame_inputs, text="Nombre del estudiante:", bg="#f0f0f0").grid(row=0, column=0, padx=5, pady=5)
entry_nombre = tk.Entry(frame_inputs, width=30)
entry_nombre.grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_inputs, text="Registrar/Editar", command=registrar_o_editar, bg="#90a4ae", width=20).grid(row=0, column=2, padx=5)

asignaturas = [f"Asig. {i+1}" for i in range(8)]
entry_asig = []
#asignaturas en filas
for i, asig in enumerate(asignaturas):
    tk.Label(frame_inputs, text=asig, bg="#f0f0f0").grid(row=1, column=i, padx=2, pady=2)
    entrada = tk.Entry(frame_inputs, width=10)
    entrada.grid(row=2, column=i, padx=30, pady=1)
    entry_asig.append(entrada)

tk.Label(frame_inputs, text="Eliminar por nombre:", bg="#f0f0f0").grid(row=3, column=0, padx=5, pady=10)
entry_eliminar = tk.Entry(frame_inputs, width=30)
entry_eliminar.grid(row=3, column=1, padx=5)
tk.Button(frame_inputs, text="Eliminar", command=eliminar_estudiante, bg="#78909c", width=15).grid(row=3, column=2, padx=5)

columnas = ["No","Nombre"] + asignaturas + ["PromSemestre1","PromSemestre2","PromTotal","Estado"]
tabla = ttk.Treeview(ventana, columns=columnas, show="headings", height=20)
for col in columnas:
    tabla.heading(col, text=col)
tabla.column("No", width=40, anchor="center")
tabla.column("Nombre", width=180)
for c in asignaturas:
    tabla.column(c, width=80, anchor="center")
tabla.column("PromSemestre1", width=80, anchor="center")
tabla.column("PromSemestre2", width=80, anchor="center")
tabla.column("PromTotal", width=80, anchor="center")
tabla.pack(pady=10, fill="x")

frame_botones = tk.Frame(ventana, bg="#f0f0f0")
frame_botones.pack(pady=10, fill="x")

tk.Button(frame_botones, text="Actualizar tabla", command=actualizar_tabla, bg="#90a4ae", width=20, height=2).pack(side="left", padx=10)
tk.Button(frame_botones, text="Guardar CSV", command=lambda: guardar_datos(semestre_actual), bg="#78909c", width=20, height=2).pack(side="left", padx=10)
tk.Button(frame_botones, text="Salir", command=ventana.destroy, bg="#b0bec5", width=20, height=2).pack(side="left", padx=10)
btn_semestre = tk.Button(frame_botones, text="Ir a Semestre 2", command=cambiar_semestre, bg="#546e7a", width=20, height=2)
btn_semestre.pack(side="right", padx=20)

#cargar datos iniciales y mostrar tabla
cargar_datos(semestre_actual)
actualizar_tabla()
ventana.mainloop()

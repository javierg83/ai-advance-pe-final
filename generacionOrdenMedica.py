from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def generar_orden_medica(nombre, edad, peso, rut, recomendacion):
    # Crear un nuevo documento
    document = Document()

    # Configurar la fuente por defecto para todo el documento (por ejemplo, Arial 12pt)
    style = document.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(12)

    # Agregar un título centrado
    parrafo_titulo = document.add_paragraph()
    parrafo_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_titulo = parrafo_titulo.add_run("ORDEN MÉDICA")
    run_titulo.bold = True
    run_titulo.font.size = Pt(16)

    document.add_paragraph()  # Línea en blanco

    # Sección de datos del paciente
    parrafo_datos = document.add_paragraph()
    run_encabezado = parrafo_datos.add_run("Datos del Paciente:\n")
    run_encabezado.bold = True
    parrafo_datos.add_run(f"Nombre: {nombre}\n")
    parrafo_datos.add_run(f"Edad: {edad} años\n")
    parrafo_datos.add_run(f"Peso: {peso} kg\n")
    parrafo_datos.add_run(f"RUT: {rut}\n")

    document.add_paragraph()  # Línea en blanco

    # Sección de recomendación médica
    parrafo_recomendacion = document.add_paragraph()
    run_recomendacion_enc = parrafo_recomendacion.add_run("Recomendación Médica:\n")
    run_recomendacion_enc.bold = True
    parrafo_recomendacion.add_run(recomendacion)

    # Guardar el documento en un archivo
    nombre_archivo = "orden_medica.docx"
    document.save(nombre_archivo)
    print(f"Documento guardado como '{nombre_archivo}'")

#if __name__ == "__main__":
    # Solicitar datos de entrada al usuario
    #nombre = input("Ingrese el nombre del paciente: ")
    #edad = input("Ingrese la edad: ")
    #peso = input("Ingrese el peso: ")
    #rut = input("Ingrese el RUT: ")
    #recomendacion = input("Ingrese la recomendación médica: ")

    #generar_orden_medica(nombre, edad, peso, rut, recomendacion)

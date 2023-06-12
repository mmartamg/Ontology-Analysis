# Ontology-Analysis

## Archivos
- TFMOntologiaCompleta.owl: ontología completa sin individuos.
- TFMCasoPrincipal.owl: ontología completa con el caso de estudio principal definido.
- TFMCasoEstudio2.owl: ontología completa con el caso de estudio 2 definido.
- TFMCasoEstudio3.owl: ontología completa con el caso de estudio 3 definido.
- ONTOLOGIATFMGESTION.py: programa de análisis de ontologías – script de gestión.
- ONTOLOGIATFMUSO.py: programa de análisis de ontologías – script de uso.
- informe.css: archivo CSS para definir el estilo del informe autogenerado.
---
## Requisitos
Los requisitos necesarios para el uso del sistema son:
 - Protégé (versión 5.6.1)
 - Python 3

Las librerías usadas:
-	Owlready2
- math
- matplotlib
- numpy
- os
- MdUtils
-	md2pdf
-	datetime
---
## Guía de Uso
Para poder analizar la ontología con el programa se debe definir la localización de la misma dentro de la función `main()` de **ONTOLOGÍATFMUSO.py** (línea [418](https://github.com/mmartamg/Ontology-Analysis/blob/fe94a547d7a96fab486c768d985ed18d88ff819c/ONTOLOGIATFMUSO.py#L418)):

`onto = get_ontology("ONTOLOGY LOCATION").load()`

También se debe definir la localización en la que se guardará la ontología actualizada (línea [421](https://github.com/mmartamg/Ontology-Analysis/blob/fe94a547d7a96fab486c768d985ed18d88ff819c/ONTOLOGIATFMUSO.py#L421)), para esto puede actualizarse el archivo o crearse uno nuevo:

`onto.save(file = "NEW ONTOLOGY LOCATION", format = "rdfxml")` 

Después de esto, se debe definir el IRI de la ontología con la que se trabaja dentro de la función `create_query(func)` de **ONTOLOGÍATFMGESTION.py** (línea [18](https://github.com/mmartamg/Ontology-Analysis/blob/235378adb0a3b3c8dee0b0e52854785472c37dc1/ONTOLOGIATFMGESTION.py#L18)):

`PREFIX onto: <ONTOLOGY PREFIX>`

Con todos estos cambios ya se puede usar el programa. Para ello se ejecutará el script de uso de la siguiente manera:

`python ONTOLOGIATFMUSO.py`

En la misma carpeta en la que se encuentre el programa veremos que se han creado dos nuevas carpetas: /graphs y /reports. En la primera encontraremos las gráficas generadas en formato PNG, y en la segunda tendremos los informes autogenerados de cada tarea de la ontología.

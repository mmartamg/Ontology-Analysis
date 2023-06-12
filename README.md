# Ontology-Analysis
---
Los requisitos necesarios para el uso del sistema son:
•	Protégé (versión 5.6.1)
•	Python 3
Las librerías de Python que se van a usar y que, por tanto, se deben tener instaladas en el sistema son:
•	Owlready2
•	math
•	matplotlib
•	numpy
•	os
•	MdUtils
•	md2pdf
•	datetime

Una vez se cuenta con dichos archivos, lo primero que se puede hacer es comprobar la ontología diseñada y los diferentes casos de estudio por medio de una herramienta como Protégé [29]. Gracias a esta herramienta se pueden abrir y visualizar los ficheros de OWL, para así comprobar las clases, relaciones, atributos e individuos creados.
Para poder analizar la ontología con el programa se debe definir la localización de la misma dentro de la función main() de ONTOLOGÍATFMUSO.py
onto = get_ontology("ONTOLOGY LOCATION").load()
Así como definir la localización en la que se guardará la ontología actualizada, para esto puede actualizarse el archivo o crearse uno nuevo:
onto.save(file = "NEW ONTOLOGY LOCATION", format = "rdfxml")
Después de esto, se debe definir el IRI de la ontología con la que se trabaja dentro de la función create_query(func) de ONTOLOGÍATFMGESTION.py:
PREFIX onto: <ONTOLOGY PREFIX>
Con todos estos cambios ya se puede usar el programa. Para ello se ejecutará el script de uso de la siguiente manera:
python ONTOLOGIATFMUSO.py
Una vez ejecutado encontraremos la ontología actualizada en la localización en la que se haya establecido, y podremos ver los cambios por medio de Protégé. 
En la misma carpeta en la que se encuentre el programa veremos que se han creado dos nuevas carpetas: /graphs y /reports. En la primera encontraremos las gráficas generadas en formato PNG, y en la segunda tendremos los informes autogenerados de cada tarea de la ontología.

# CTF Junior 2017

## Categorías

### Web

**Mecánica del ejercicio**:

1. No quedarnos con la información que vemos en el navegador:
Inspeccionar el código fuente de la página web.
Y la estructura de una petición/respuesta POST a un servidor.
2. Investigar el viaje de los datos hasta llegar al servidor: ¿qué URLs se visitan?
3. Comprender los cambios en las URLs (visibles y ocultos por redireccionamientos), y los efectos en nuestra computadora (que permiten identificar nuestra sesión).

**Keywords**: html, url, http, https, md5, cookie, scripting, https post request/response, https headers, https status code

**Herramientas**: python, web developer tools, wget, curl

### Ingeniería inversa

**Mecánica del ejercicio**:

1. Ejecutar binario. Probar con algunas entradas. Obtener información básica del ejecutable (file, string, readelf, objdump).
2. Desensamblar el código.
3. Identificar función principal y auxiliares.
4. Identificar función de lectura de stdin.
5. Identificar qué función imprime el mensaje de error y cuál el flag.
6. Identificar qué parte de la función principal valida (que sea un hash) el input y cuál lo verifica.
7. Debuggear. Forzar la ejecución hasta el bloque que realiza la verificación y entenderla.

**Keywords**: assembly, control-flow graph, convención de llamado a funciones, ABI.

**Herramientas**: debugger (gdb, ida, etc), disassembler (ida, oda, barf), graficadores del control de flujo (en inglés: control flow graph), file, strings, readelf, objdump.

[Introducción a los temas](https://github.com/fundacion-sadosky/ctf_junior_2017/tree/master/disasm)

### Criptografía

**Mecánica de los ejercicios**:

Todos los ejercicios se basan en "encripción" con xor con clave de tamaño fijo de un byte de longitud.

1. Identificar del modo de encripción/desencripción.
2. Detectar la posible clave utilizada.
3. Desencripción de los datos que puede derivar en la obtención del flag.

**Keywords**: xor, ECB, CBC, brute-force

**Herramientas**: python, file, bzip2

[Introducción a los temas](https://github.com/fundacion-sadosky/ctf_junior_2017/tree/master/crypto)

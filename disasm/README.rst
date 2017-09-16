****************************************
Analisis de binarios: Ingenieria reversa
****************************************

Esta es una breve introduccion de las herramientas basicas y la metodologia para resolver los challenges de la seccion de ingenieria inversa. Los flags en estos casos van a estar ocultos de distintas formas dentro de los binarios que se van a analizar.

Para reproducir el ejemplo mostrado es necesario descargar este repositorio que incluye los archivos necesarios.

.. code:: bash

	git clone https://github.com/fundacion-sadosky/ctf_junior_2017

Conocimientos previos
=====================

Durante esta guia se asume que el lector tiene un conocimiento basico de:

* Linux
* Manejo de consola
* Assembler x86
* Concepto de pilas y llamadas a función (más información en relación a estos temas en https://goo.gl/kr8DFs)


Interpretacion del archivo
==========================

Se toma como ejemplo el challenge mas sencillo de esta categoria, que corresponde al binario de ``jamfor`` (incluido en este repositorio). Utilizamos primero el comando ``file`` para explorar que tipo de archivo es:

.. code:: bash

	user@ubuntu-pc:~/ctf_junior_2017/disasm$ file jamfor 
	jamfor: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV)

Por lo que reporta parece ser un archivo ejecutable para el sistema operativo Linux (``SYSV``) y arquitectura Intel x86 de 32 bits. El formato de este archivo ejecutable es el ``ELF`` (https://es.wikipedia.org/wiki/Executable_and_Linkable_Format). Ahora que conocemos el formato del binario ejecutable utilizamos el comando ``readelf`` para tener más información.

Al correr el comando con los argumentos ``-h``, que muestra el header del archivo y ``-t``, que muestra las distintas secciones, podemos ver en el output (que en este ejemplo está editado) varias elementos de información relevante para el análisis.

.. code:: bash

	user@ubuntu-pc:~/ctf_junior_2017/disasm$ readelf -h -t jamfor
	ELF Header:
	  Class:                             ELF32
	  OS/ABI:                            UNIX - System V
	  Type:                              EXEC (Executable file)
	  Machine:                           Intel 80386
	  Entry point address:               0x8048350

	Section Headers:
	  [Nr] Name
	       Type            Addr     Off    Size   ES   Lk Inf Al
	       Flags

	  [ 2] .text
	       PROGBITS        080480b8 0000b8 00038b 00   0   0  1
	       [00000006]: ALLOC, EXEC
	  [ 3] .rodata
	       PROGBITS        08048444 000444 000099 00   0   0  4
	       [00000002]: ALLOC

El header del ELF confirma la información reportada por ``file``, además agrega que el punto de entrada (``Entry point address``) del ejecutable se encuentra en la instrucción con la dirección 0x8048350. Esta dirección es parte de la sección ``.text`` que almacena la mayoría del código que ejecuta el programa.

También se observa la seccion ``.rodata``, con datos de sólo lectura, esto es, los bytes que se encuentren (durante la ejecución del programa) dentro del rango de direcciones entre 0x08048444 y 0x08048444 + 0x99 (tamaño reportado por ``readelf``) no serán interpretados (durante la ejecución normal) como instrucciones, sino como datos, que serán referenciados por las instrucciones de la sección ``.text``. Es útil mantener esto en cuenta durante el posterior análisis del binario, para cuando se detecten direcciones pertenecientes a la sección ``.rodata``, podemos interpretar que esas instrucciones están (en alguna manera, directa o indirectamente) accediendo a datos.

Podemos ignorar el resto de las secciones del binario que lista el ``readelf``.


Desensamblaje: prologo y epílogo de una función
===============================================

Una opción para ver las instrucciones del binario es utilizar el comando ``objdump`` con el argumento ``-d`` para que desensamble (interprete los bytes como instrucciones e imprima sus nombres) la seccion ``.text``. Ademas utilizamos el argumento ``-M intel`` para que imprima las instrucciones en la sintaxis de intel en vez de la de AT&T (https://en.wikipedia.org/wiki/X86_assembly_language#Syntax) que consideramos menos amigable para el que se esta iniciando.

.. code:: bash

	user@ubuntu-pc:~/ctf_junior_2017/disasm$ objdump -d jamfor -M intel

	jamfor:     file format elf32-i386

	Disassembly of section .text:

	080480b8 <.text>:
	 80480b8:	55                   	push   ebp                       ;
	 80480b9:	89 e5                	mov    ebp,esp                   ; PROLOGO
	 80480bb:	83 ec 04             	sub    esp,0x4                   ;

	 80480be:	c7 45 fc 00 00 00 00 	mov    DWORD PTR [ebp-0x4],0x0
	 80480c5:	eb 04                	jmp    0x80480cb
	 80480c7:	83 45 fc 01          	add    DWORD PTR [ebp-0x4],0x1
	 80480cb:	8b 55 fc             	mov    edx,DWORD PTR [ebp-0x4]
	 80480ce:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]
	 80480d1:	01 d0                	add    eax,edx
	 80480d3:	0f b6 00             	movzx  eax,BYTE PTR [eax]
	 80480d6:	84 c0                	test   al,al
	 80480d8:	75 ed                	jne    0x80480c7

	 80480da:	8b 45 fc             	mov    eax,DWORD PTR [ebp-0x4]   ;
	 80480dd:	c9                   	leave                            ; EPILOGO
	 80480de:	c3                   	ret                              ;

	 [...]

El extracto anterior muestra sólo la primer funcion de las varias que podemos encontrar en la sección ``.text``. Es útil identificar la estructura basica de las funciones que se van a encontrar dentro de este tipo de binarios, ya que la misma se aplica a la mayoria de las funciones independientemente de cuál sea su funcionalidad/utilidad. Esto va a permitir concentrarnos en QUÉ hace la funcion en vez de CÓMO lo hace.

Lo primero que se puede identificar es el prólogo de la funcion (las primeras 3 instrucciones), su comienzo: su finalidad es ajustar la pila (reservando el espacio necesario para la funcion particular) y el registro EBP (``ebp`` en la notacion del ``objdump``) para que el mismo sirva como referencia fija a la pila, esto es, todos los accesos a la misma se van a realizar a traves de este registro, y por eso va a ser uno de los que mas se repita dentro del codigo. Su uso principal sera el de acceder a variables que se almacenaran en la pila.

La primera instrucción ``push ebp`` guarda el valor actual del registro EBP en la pila para "protegerlo" (y poder recuperarlo cuando termine la función actual), ya que vamos a pisar ese valor en la instruccion siguiente, ``mov ebp,esp``, con la dirección actual de la pila (registro ESP). El valor de EBP se mantendrá constante durante la ejecución de la función actual y asi tener una referencia fija a los contenidos de la pila (simplificando el código). Finalmente en la tercera función ajusta el ESP para reservar la memoria necesaria de la pila que utilizará esta función para almacenar variables locales (en este caso 4 bytes, ``sub esp,0x4``).

La contraparte del prólogo es el epílogo, el final de la función (en este caso las últimas 3 instrucciones), que se encarga de restaurar el contexto de ejecucion al estado anterior a la ejecucion de la función, dejando "ordenada" la pila. La instrucción en ``80480da`` mueve un valor al registro EAX (``mov eax,DWORD PTR [ebp-0x4]``) donde se almacena el valor de retorno de la función (de tener uno). La instrucción ``leave`` "revierte" el accionar de las primeras dos instrucciones de la función, que modificaron los registros EBP y ESP: equivale a dos instrucciones juntas, una que mueve el valor de EBP a ESP, restaurando el valor original de ESP ("devolviendo" la memoria reservada), y la segunda instrucción que hace un ``pop ebp`` recuperando el valor original de EBP, guardado en la pila al iniciar la función. Finalmente la instrucción ``ret`` hace que el flujo de ejecución retorne a la función padre, la que llamo a esta función en primer lugar.

Aunque el prólogo suele ser único para cada función puede suceder que la misma función contenga distintos epílogos dentro de su código, si, por ejemplo, durante la programación de la misma se le pusieron finales distintos con distintas partes del código.

Como se dijo antes, el registro EBP se utiliza normalmente como referencia para acceder a la pila, que almacena las variables locales de la funcion. En este ejemplo particular hay una sola variable de 4 bytes, para la que se reservó espacio en el prólogo de la función, y es accedida durante toda la función a través del registro EBP como ``[ebp-0x4]``, esto es, el contenido de memoria al que apunta EBP menos 4. (Se deben restar 4 bytes debido a que -por convención- la Pila crece hacia las direcciones de menor valor numérico). El tipo de variable no es explícito dentro del lenguaje de ensamblador, sino que se lo puede inferir tipicamente de la clase de uso que se le dé, e.g. si se le suman o restan numeros puede ser un entero, si su contenido se utiliza como una dirección de memoria puede ser un puntero, etc.


Llamadas a funciones: argumentos y valor de retorno
===================================================

Referencias útiles:

* https://en.wikibooks.org/wiki/X86_Disassembly/Functions_and_Stack_Frames

* https://en.wikipedia.org/wiki/X86_calling_conventions#cdecl

En x86 las llamadas a funciones se realizan con la instrucción ``call`` y los argumentos se pasan (en Linux) a través de la pila con la instruccion ``push``, con la salvedad de que el orden de los valores "pusheados" en la pila se corresponden de derecha a izquierda con la lista de argumentos de la funcion (de manera que el primer argumento quede en la dirección mas baja y el último en la dirección mas alta).

En el ejemplo a continuación, la función que se encuentra en la dirección 0x80482de es llamada con 3 argumentos. El primer push, corresponde al tercer argumento, y tiene el valor de la variable de la pila referenciada por ``[ebp-0xc]``. El segundo push, segundo argumento, tiene otro valor de la pila, ``[ebp-0x8]``. Finalmente el tercer push, primer argumento, a diferencia los otros argumentos, no tiene el valor de una variable de la pila sino su dirección, lo que suele corresponder al paso de un puntero como argumento. Las direcciones (y no los valores a los que éstas apuntan) suelen obtenerse con la instrucción ``lea``, que computa la dirección efectiva del operando de la instrucción, para el caso de ``lea eax,[ebp-0x6f]`` equivale al valor en EBP menos el numero ``0x6f``, pero no accede a esa dirección (a diferencia de las otras instrucciones ``mov`` y ``push``) sino que simplemente retorna la dirección en sí. Como se dijo antes, la instrucción ``lea`` es caraterística del uso de punteros.

.. code:: asm

	 80483dd:	8b 45 f4             	mov    eax,DWORD PTR [ebp-0xc]
	 80483e0:	50                   	push   eax
	 80483e1:	ff 75 f8             	push   DWORD PTR [ebp-0x8]
	 80483e4:	8d 45 91             	lea    eax,[ebp-0x6f]
	 80483e7:	83 c0 42             	add    eax,0x42
	 80483ea:	50                   	push   eax
	 80483eb:	e8 ee fe ff ff       	call   0x80482de
	 80483f0:	83 c4 0c             	add    esp,0xc

El valor de retorno de la función suele almacenarse en el registro EAX, el caso donde EAX no es accedido luego de la llamada a función suele significar que la funcion no tenia valor de retorno (``void``). Este es el caso de la función del ejemplo anterior, donde posiblemente el resultado de la función se guarda en la dirección (del puntero) pasada en el tercer argumento.

La ultima instrucción, que ajusta el registro ESP que delimita el fin de la pila se usa para "devolver" el espacio utilizado para almacenar todos los argumentos y puede ser ignorado normalmente, porque no afecta el uso de la pila durante el resto de la ejecución (las variables locales siguen en la misma posicion y siguen siendo referenciadas por el registro EBP que no cambia de valor).

Dentro de la función llamada, los argumentos pasados son accedidos a traves del registro EBP, el mismo que se utiliza para acceder a las variables locales, solo que en vez de tener una indexación negativa (e.g., ``mov eax,DWORD PTR [ebp-0xc]``) tienen valores positivos como en el ejemplo a continuación, donde ``[ebp+0x8]`` hace referencia al primer argumento, ``[ebp+0xc]`` al segundo (``[ebp+0x10]`` haria referencia a un tercero y asi sucesivamente sumando de a 4 bytes), recordando como se dijo antes, que debido al orden de los ``push`` (por convencion) el primer argumento esta en la dirección mas baja y el último en la dirección mas alta. El valor almacenado en ``[ebp+0x4]`` (salteado en esta enumeracion) corresponde a la dirección de retorno hacia la función padre (que llama a la actual), no suele ser visto porque es manejado en forma implícita por el ``call`` (que pone el valor de retorno en la pila antes de hacer el salto) y ``ret`` (que lo recupera de la pila para saber hacia donde saltar para volver a la función padre que la llamó).

.. code:: asm

	 80482de:	55                   	push   ebp
	 80482df:	89 e5                	mov    ebp,esp
	 80482e1:	83 ec 04             	sub    esp,0x4
	 80482e4:	8b 45 0c             	mov    eax,DWORD PTR [ebp+0xc]
	 80482e7:	01 c0                	add    eax,eax
	 80482e9:	89 45 fc             	mov    DWORD PTR [ebp-0x4],eax
	 80482ec:	8b 55 08             	mov    edx,DWORD PTR [ebp+0x8]


Llamadas a sistemas: interrupciones
===================================

En estos ejemplos se realizan varias llamadas al sistema operativo (SYSCALL), en especial para manejar la entrada y salida (I/O) con el usuario, que en una consola son básicamente leer de ``stdin`` y escribir a ``stdout``. En Linux/x86 estas llamadas a sistema se realizan mediante la interrupción 80 (https://en.wikibooks.org/wiki/X86_Assembly/Interfacing_with_Linux), utilizando los registros EBX, ECX, EDX y ESI para pasar los argumentos a la llamada. El número de la llamada, que determina que función se esta solicitando al sistema operativo, se guarda en EAX (https://syscalls.kernelgrok.com/).

.. code:: asm

	 80481c7:	55                   	push   ebp
	 80481c8:	89 e5                	mov    ebp,esp
	 80481ca:	83 ec 04             	sub    esp,0x4

	 80481cd:	c7 45 fc 44 84 04 08 	mov    DWORD PTR [ebp-0x4],0x8048444
	 80481d4:	b8 04 00 00 00       	mov    eax,0x4
	 80481d9:	bb 01 00 00 00       	mov    ebx,0x1
	 80481de:	8b 4d fc             	mov    ecx,DWORD PTR [ebp-0x4]
	 80481e1:	ba 22 00 00 00       	mov    edx,0x22
	 80481e6:	cd 80                	int    0x80                   ; SYSCALL 1: write

	 80481e8:	b8 01 00 00 00       	mov    eax,0x1
	 80481ed:	bb 00 00 00 00       	mov    ebx,0x0
	 80481f2:	cd 80                	int    0x80                   ; SYSCALL 2: exit

	 80481f4:	90                   	nop
	 80481f5:	c9                   	leave  
	 80481f6:	c3                   	ret    

En esta función de ejemplo hay dos llamadas al sistema (``int 0x80``). En la primera se llama a la función ``write`` (http://man7.org/linux/man-pages/man2/write.2.html) ajustando EAX a la SYSCALL numero 4 (``mov eax,0x4``). El valor del primer argumento ``int fd`` se guarda en EBX con el valor 1 (``mov ebx,0x1``) que corresponde a la salida por consola (``stdout``, http://man7.org/linux/man-pages/man3/stdin.3.html). El valor del segundo argumento ``const void *buf`` se guarda en ECX y almacena la dirección 0x8048444 que pertenece a la sección ``.rodata``. Esto signfica que se esta llamando a la SYSCALL encargada de enviar un mensaje por consola al usuario, de hecho, si investigamos mejor el binario ``jamfor`` con ``objdump`` agregando el parámetro ``-s``, para imprimir los bytes como texto, podemos ver el contenido de esa dirección.

.. code:: bash

	user@ubuntu-pc:~/ctf_junior_2017/disasm$ objdump -s jamfor -j .rodata # -j: solo la sección indicada

	jamfor:     file format elf32-i386

	Contents of section .rodata:
	 8048444 456c2070 6172616d 6574726f 20646164  El parametro dad
	 8048454 6f206e6f 20657320 636f7272 6563746f  o no es correcto

Entonces podemos resumir que el primer SYSCALL tiene como objetivo imprimir por pantalla el string "El parámetro dado no es correcto", que como se ve en el ejemplo provisto en el challenge, es la leyenda que aparece cuando se ingresa el texto equivocado al binario.

El segundo SYSCALL de la funcion de ejemplo es mas sencillo, utiliza la llamada numero 1 (``mov eax,0x1``) correspondiente a la funcion ``exit`` (http://man7.org/linux/man-pages/man2/exit.2.html) para terminar la ejecución del programa (luego de imprimir el mensaje de error mostrado antes).


Análisis dinámico
=================

Utilizamos el ``gdb`` para hacer el debug del binario, aunque también se recomienda la interfaz del Eclipse (frontend para el ``gdb``) si ya se tiene experiencia con la misma.

Antes de iniciar el ``gdb`` se recomienda instalar el GDB dashboard (https://github.com/cyrus-and/gdb-dashboard) que mejora su interfaz gráfica, incluido en este repositorio (con la opcion agregada para que use, como el ``objdump``, la sintaxis de intel).

.. code:: bash

	[ -f ~/.gdbinit ] && cp ~/.gdbinit ~/.gdbinit.back # Hace un backup de la configuracion actual del gdb
	cp ./.gdbinit ~ # Instala el .gdbinit para que lo encuentre el gdb al iniciar

Como el programa necesita una entrada desde ``stdin`` (e.g., ``echo "test" | ./jamfor``) se crea un archivo con un string de prueba para simular automáticamente la entrada de datos del usuario mientras ejecutamos el programa en gdb (evitando tener que ingresar el string manualmente en cada ejecucion).

.. code:: bash

	echo "user_input_string" > user_input.txt # Archivo incluido en el repo

Iniciamos el gdb con ``gdb jamfor``:

.. code:: bash

	user@ubuntu-pc:~/ctf_junior_2017/disasm$ gdb jamfor
	GNU gdb (Ubuntu 7.11.1-0ubuntu1~16.5) 7.11.1
	[...]
	Reading symbols from jamfor...(no debugging symbols found)...done.

En la última linea de inicio va a advertir que no hay informacion para hacer el debug (``no debugging symbols found``), los programas fueron compilados asi de forma premeditada para que el código fuente no este disponible al gdb, de manera de que sea necesario hacer un trabajo de ingeniería inversa, como en este ejemplo.

Si corremos el programa directamente con el string de prueba vemos como falla (con el string visto antes: "El párametro dado no es correcto") y termina la ejecución.

.. code:: bash

	>>> r < user_input.txt 

	El parametro dado no es correcto.
	[Inferior 1 (process 7985) exited normally]

Ahora vamos a insertar un breakpoint en la función encargada de imprimir el mensaje de error y terminar el programa, desensamblada antes, en la direccion 0x80481c7:


.. code:: bash

	>>> b *0x80481c7
	Breakpoint 1 at 0x80481c7

Volvemos a ejecutar el programa para detener la ejecución en el breakpoint ingresado y tratar de entender quien llama a esa función.

.. code:: bash

	>>> r < user_input.txt

		─── Stack ─────────
		[0] from 0x080481c7
		(no arguments)
		[1] from 0x0804842d
		(no arguments)
		[+]

En la sección del ``Stack`` del dashboard se ve la dirección de la función padre que llama a esta, o sea, la función padre en 0x0804842d (``[1]``) llama a la función actual en 0x080481c7 (``[0]``). Alternativamente esta información se puede ver directamente con el comando ``backtrace``. Buscando en la información del ``objdump`` la dirección 0x0804842d, desde donde se generó el call a la función actual, se ve que pertence a la función en la dirección 0x8048350 (esto se puede determinar en forma sencilla si se esta atento a los prólogos y epílogos que delimitan a las funciones, discutidos antes).

Ingresamos ahora un breakpoint en la función padre, 0x8048350, y volvemos a ejecutar el programa.

.. code:: bash

	>>> b *0x8048350
	Breakpoint 2 at 0x804842d
	>>> r < user_input.txt 

Esta función ya es mas grande y mas compleja que las anteriores asi que resulta útil visualizar su CFG (flujo de ejecución), incluido en este repo en ``jamfor_cfg/sub_8048350.svg``, para entender que camino lleva a la función que reporta el error (analizada antes) y que otro camino alternativo se puede recorrer (que tal vez nos de información del flag buscado).

Analizando el CFG en cuestión, yendo hacia atras se ve que la decisión de ir a la función de error depende de la dirección 0x8048415 (``je``), de que EAX sea igual a cero. El registro EAX a su vez tiene el valor de retorno de la función un par de instrucciones antes en ``804840b: call   0x8048113``. Viendo su CFG (``jamfor_cfg/sub_8048113.svg``) se puede observar que consiste principalmente de un ciclo (que tiene como inicio la dirección 0x8048126) y su condicion de corte se encuentra en la dirección 0x8048140, que comprueba que la variable local en ``[ebp-0x4]`` sea menor o igual a 0x1f (31). Esto aparenta ser un ciclo que recorre 32 valores, del 0 al 31. Dentro del cuerpo principal del ciclo, esta variable local ``[ebp-0x4]``, que por simplicidad vamos a denominar ``i`` (ya que parece ser el índice del ciclo), se utiliza para indexar memoria apuntada tanto por el primer como por el segundo argumento (``ARG_1``/``ARG_2``) y comparar sus valores.

.. code:: asm

	 8048113:	55                   	push   ebp
	 8048114:	89 e5                	mov    ebp,esp
	 8048116:	83 ec 04             	sub    esp,0x4
	 8048119:	c7 45 fc 00 00 00 00 	mov    DWORD PTR [ebp-0x4],0x0
	 8048120:	eb 04                	jmp    0x8048126
	
	 ; Inicio del cuerpo del ciclo
	 8048122:	83 45 fc 01          	add    DWORD PTR [ebp-0x4],0x1  ; i++

	 8048126:	8b 55 fc             	mov    edx,DWORD PTR [ebp-0x4]  ; EDX = i
	 8048129:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]  ; EAX = ARG_1
	 804812c:	01 d0                	add    eax,edx                  ; EAX = ARG_1 + i
	 804812e:	0f b6 10             	movzx  edx,BYTE PTR [eax]       ; EDX = [ARG_1 + i] 


	 8048131:	8b 4d fc             	mov    ecx,DWORD PTR [ebp-0x4]  ; ECX = i
	 8048134:	8b 45 0c             	mov    eax,DWORD PTR [ebp+0xc]  ; EAX = ARG_2
	 8048137:	01 c8                	add    eax,ecx                  ; EAX = ARG_2 + i
	 8048139:	0f b6 00             	movzx  eax,BYTE PTR [eax]       ; EAX = [EAX] = [ARG_2 + i]

	 804813c:	38 c2                	cmp    dl,al
	 804813e:	75 06                	jne    0x8048146                ; Break if EAX != EDX
	                                                                    ;        ([ARG_1 + i] != [ARG_2 + i])

	 8048140:	83 7d fc 1f          	cmp    DWORD PTR [ebp-0x4],0x1f
	 8048144:	7e dc                	jle    0x8048122                ; While i <= 32


Si probamos detener la ejecución justo antes de llamar a esta función de comparación (en la direccion 0x804840b) podemos inspeccionar cuales son sus argumentos.

Viendo la llamada a la funcion, el segundo argumento (1er ``push``) corresponde a la direccion de EBP menos ``0x6f`` y luego mas ``0x42``. Es importante recordar que ``lea`` no accede a los datos sino que solamente computa la dirección, y en la instrucción siguiente se le suma otro valor. Aunque parece un poco aparatosa la forma de generar una dirección haciendo dos computos de valores contrapuestos con signos distintos, esto obedece a que se hizo una compilación sin optimizacion (para facilitar la resolución del ejercicio). La dirección ``[ebp-0x6f]`` probablemente obedece a la dirección inicial de un array que es indexado luego con el índice ``0x42`` (e.g., ``string_array[0x42]``), lo que se tradujo en dos instrucciones assembler y no en una sola (modo optimizado). Es útil tener en cuenta esto porque hace mas predecible la estructura de codigo generada por el compilador, y siempre que se acceda a esa posición de memoria se lo hara con este par de instrucciones (como veremos luego) de la misma forma y con el mismo orden, para que sea fácilmente reconocible. El primer argumento (2do ``push``) es otra direccion a una variable local (``[ebp-0x90]``).

.. code:: asm

	 80483fd:	8d 45 91             	lea    eax,[ebp-0x6f]
	 8048400:	83 c0 42             	add    eax,0x42
	 8048403:	50                   	push   eax
	 8048404:	8d 85 70 ff ff ff    	lea    eax,[ebp-0x90]
	 804840a:	50                   	push   eax
	 804840b:	e8 03 fd ff ff       	call   0x8048113

.. code:: bash

	>>> b *0x804840b
	Breakpoint 1 at 0x804840b
	>>> r < user_input.txt 
	>>> x/s $ebp - 0x90
	0xffffce7c:	"user_input_string\n"
	>>> x/s $ebp - 0x6f + 0x42
	0xffffcedf:	"bf00bfb04e44899aa7a651cc2690e1b9"

El primer argumento es claramente el string ingresado por el usuario (que ingresamos a traves del archivo ``user_input.txt``) mientras que el segundo parece ser una cadena de 32 caracteres, aparentemente dígitos hexadecimales, como el formato del flag que estamos buscando. Investigamos un poco mas de donde se genera este segundo string, almacenado en ``[ebp-0x6f] + 0x42``.

Si seguimos viendo el CFG de la funcion padre (0x8048350), la primera referencia a esa variable es como argumento a otra funcion: 0x8048152.

.. code:: asm

	 8048392:	8d 45 91             	lea    eax,[ebp-0x6f]
	 8048395:	83 c0 42             	add    eax,0x42
	 8048398:	50                   	push   eax
	 8048399:	68 bc 84 04 08       	push   0x80484bc
	 804839e:	e8 af fd ff ff       	call   0x8048152

El segundo argumento (1er ``push``) es la direccion en cuestión (no su valor, porque se usa la instrucción ``lea``) y el primero (2do ``push``) es una dirección absoluta: 0x80484bc (en vez de una referencia relativa a la pila a traves de EBP), esto suele suceder para el acceso a memoria estática (global) en el programa. Si repasamos los encabezados del ``readelf`` ésta dirección pertenece a ``.rodata``, y usando ``objdump -s`` podemos ver los strings de esa sección del binario.

.. code:: bash

	user@ubuntu-pc:~/ctf_junior_2017/disasm$ objdump -s jamfor -j .rodata # -j: solo la sección indicada

	jamfor:     file format elf32-i386

	Contents of section .rodata:
	 [...]
	 80484b4 30646231 00000000 78787878 78787878  0db1....xxxxxxxx
	 80484c4 78787878 78787878 78787878 78787878  xxxxxxxxxxxxxxxx
	 80484d4 78787878 78787878 00                 xxxxxxxx.       

Este dirección parece contener otro string de 32 caracteres, pero estos son todos la letra ``x``.

Viendo el CFG de la función 0x8048152 aparece otra estructura similar a un ciclo, donde la condicion de corte es nuevamente una comparación con ``<= 31``.

.. code:: asm

	 804817a:	83 7d fc 1f          	cmp    DWORD PTR [ebp-0x4],0x1f ; Variable de iteracion "i"
	 804817e:	7e e1                	jle    0x8048161

El cuerpo principal del ciclo parece simplemente copiar los contenidos del primer argumento al segundo, o sea, copia la cadena de 32 chars a la variable ``[ebp-0x6f] + 0x42`` (dentro del contexto de la funcion 0x8048350).

.. code:: asm

	 8048161:	8b 55 fc             	mov    edx,DWORD PTR [ebp-0x4]  ; EDX = i
	 8048164:	8b 45 0c             	mov    eax,DWORD PTR [ebp+0xc]  ; EAX = ARG_2
	 8048167:	01 c2                	add    edx,eax                  ; EDX = ARG_2 + i

	 8048169:	8b 4d fc             	mov    ecx,DWORD PTR [ebp-0x4]  ; ECX = i
	 804816c:	8b 45 08             	mov    eax,DWORD PTR [ebp+0x8]  ; EAX = ARG_1
	 804816f:	01 c8                	add    eax,ecx                  ; EAX = ARG_1 + i

	 8048171:	0f b6 00             	movzx  eax,BYTE PTR [eax]       ; EAX = [EAX] = [ARG_1 + i]
	 8048174:	88 02                	mov    BYTE PTR [edx],al        ; [EDX] = [ARG_2 + i] = AL (byte) = [ARG_1 + i]

	 8048176:	83 45 fc 01          	add    DWORD PTR [ebp-0x4],0x1  ; i++

Lo que resulta de interés es que estos 32 caracteres, almacenados ahora en ``[ebp-0x6f] + 0x42``, son distintos a los que observamos al ejecutar gdb (antes de llamar a la función que determina si se imprime el error o no), o sea, dentro de la función 0x8048350 vemos que al prinicipio la variable local ``[ebp-0x6f] + 0x42``  tiene un string de 32 chars, pero luego, en el punto de evaluación de esta variable, la cadena cambio de valor, es necesario investigar que sucedió en el medio.

Retomando el CFG de la función 0x8048350, la otra referencia a la dirección ``[ebp-0x6f] + 0x42`` sucede dentro del ciclo principal del programa, como primer argumento (ultimo ``push ``) a la función 0x80482de.

.. code:: asm

	 80483d8:	31 d8                	xor    eax,ebx
	 80483da:	89 45 f4             	mov    DWORD PTR [ebp-0xc],eax
	 80483dd:	8b 45 f4             	mov    eax,DWORD PTR [ebp-0xc]
	 80483e0:	50                   	push   eax
	 80483e1:	ff 75 f8             	push   DWORD PTR [ebp-0x8]
	 80483e4:	8d 45 91             	lea    eax,[ebp-0x6f]
	 80483e7:	83 c0 42             	add    eax,0x42
	 80483ea:	50                   	push   eax
	 80483eb:	e8 ee fe ff ff       	call   0x80482de


A su vez la función 0x80482de, al ver su CGF (``jamfor_cfg/sub_80482de.svg``), realiza varias operaciones matematicas sucesivas sobre los mismos datos (la secuencia shift/and/add), lo que parecería indicar que es una función criptográfica (tal vez un hash por ejemplo) y reforzaría la hipótesis de que el string inicial de 32 chars que se observo pueda ser el flag buscado.

.. code:: asm

	 8048305:	8b 55 10             	mov    edx,DWORD PTR [ebp+0x10]
	 8048308:	c1 ea 04             	shr    edx,0x4
	 804830b:	83 e2 0f             	and    edx,0xf
	 804830e:	83 c2 57             	add    edx,0x57
	 8048311:	eb 0c                	jmp    0x804831f

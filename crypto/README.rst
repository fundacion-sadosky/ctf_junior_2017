*********************************************
Introduccion a los challenges de criptografia
*********************************************

Esta es una breve introduccion de los conocimientos basicos necesarios para resolver los challenges de la seccion de criptografia. Los flags en estos casos van a estar ocultos de distintas formas a traves de mecanismos criptograficos (encripciones). El objetivo va a ser descubrir tanto la clave de encripcion como el mecanismo utilizado para realizar la encripcion de manera de poder llegar eventualmente al flag oculto.

Para reproducir el ejemplo mostrado es necesario descargar este repositorio que incluye los archivos necesarios.

.. code:: bash

	git clone https://github.com/fundacion-sadosky/ctf_junior_2017

O alternativamente, se puede descargar como zip desde: https://github.com/fundacion-sadosky/ctf_junior_2017/archive/master.zip


Definicion
==========

Por **encripcion** (tambien llamado cirfrado) entendemos tomar una serie de bits (ya sea de un archivo, de un mensaje que viaja por internet, etc) esconder (ocultar, opacar, etc) para que solo un grupo selecto de personas (y/o maquinas) puedan conocerlo. Estas personas van a contar con una clave que les va permitir desencriptar (decodificar, desocultar, etc) el texto encriptado para volver a abrirlo normalmente.

A la serie de bits original a ocultar se la denomina **texto plano**, aunque no quiere decir que sea necesariamente un texto humano de lectura, puede ser cualquier tipo de informacion interpretable por humano o maquina.

El proceso de encriptacion, aunque intuitivamente se lo asocia con el de ocultar la informacion, no debe ser interpretado como un ocultamiento fisico, en el sentido de que no se esconde ni se hace desaparecer ni se almacena en algun lugar recondito, sino que se la transforma en un formato que no puede ser interpretado como la informacion original por nadie que no tenga la clave. Aunque la informacion sigue al alcance de todos (en el archivo, en el mensaje que viaja por el aire en una red de wifi) tiene una forma aparentemente aleatoria, sin "sentido", que la hace "inutil" sin la clave.

A la serie de bits que resulta de aplica la encriptacion al texto plano para hacerla inaccesible se la denomina **texto cifrado**.

El proceso que define la encripcion (y tambien la desencripcion) es la **funcion de encripcion**, una serie de operaciones matematicas, utilizada (para transformar el texto de plano a cifrado), que es publicamente conocida, y la **clave de encripcion**, que es la segunda entrada (junto con el texto plano) a la funcion de encripcion, la cual es secreta.

La **desencripcion** es la funcion inversa que parte de un texto cifrado y una clave y devuelve el texto plano original que fue encriptado con esa misma clave. El tipo de encripcion que vamos a estudiar es la **encripcion simetrica** donde se utiliza la misma funcion matematica para la encripcion y la desencripcion (al igual que se utiliza la misma clave por supuesto), lo que implica a su vez que tanto el texto plano como el cifrado van a tener la misma longitud. Aunque conceptualmente vamos a diferenciar entre encripcion y desencripcion, la funcion matematica (y su implementacion), como tambien el mecanismo que la utiliza es exactamente igual para la encripcion como para la desencripcion, y la diferncia entre texto plano y cifrado es unicamente relativa al formato (patron) que el usuario espera del mismo.


Encripcion con XOR
==================

En el primer challenge de la seccion de criptografica, ``xor_cero``, que vamos a utilizar como ejemplo en esta introduccion, se utiliza como funcion de encripcion simplemente la operacion logica XOR (https://es.wikipedia.org/wiki/Puerta_XOR). En el procedimiento de encripcion (y desencripcion) se va a tomar de a 1 byte a la vez del texto plano de entrada y se lo va a combinar (a traves de la XOR) con una clave de 1 byte de largo para generar (a su vez) 1 byte de texto cifrado. Esto se repite byte por byte para todo el texto plano y el resultado sera el texto cifrado (del mismo largo).

Como ejemplo se incluye, en el mismo directorio donde esta este documento, el script en python ``example.py``, que toma como entrada el archivo de texto ``secreto.txt`` y lo encripta con distintas claves.

.. code:: bash

	user@ubuntu-pc:~/ctf_junior_2017/crypto$ cat secreto.txt 

	Shhhh este es un secreto en texto plano ;) hay que protegerlo!!

	user@ubuntu-pc:~/ctf_junior_2017/crypto$ python example.py

	Clave: 0x00 (76.19%). Encriptado: Shhhh este es un secreto en texto plano ;) hay que protegerlo!!
	Clave: 0x01 (73.02%). Encriptado: Riiii!drud!dr!to!rdbsdun!do!udyun!qm`on!:(!i`x!ptd!qsnudfdsmn  
	Clave: 0x02 (76.19%). Encriptado: Qjjjj"gqvg"gq"wl"qgapgvm"gl"vgzvm"rnclm"9+"jc{"swg"rpmvgegpnm##
	[...]
	Clave: 0x4d (38.10%). Encriptado: .%%%%m(>9(m(>m8#m>(.?(9"m(#m9(59"m=!,#"mvdm%,4m<8(m=?"9(*(?!"ll
	Clave: 0x4e (26.98%). Encriptado: .&&&&n+=:+n+=n; n=+-<+:!n+ n:+6:!n>"/ !nugn&/7n?;+n><!:+)+<"!oo
	Clave: 0x4f (26.98%). Encriptado: .''''o*<;*o*<o:!o<*,=*; o*!o;*7; o?#.! otfo'.6o>:*o?= ;*(*=# nn
	Clave: 0x50 (53.97%). Encriptado: .8888p5#$5p5#p%>p#53"5$?p5>p$5($?p <1>?pkyp81)p!%5p "?$575"<?qq
	Clave: 0x51 (53.97%). Encriptado: .9999q4"%4q4"q$?q"42#4%>q4?q%4)%>q!=0?>qjxq90(q $4q!#>%464#=>pp
	Clave: 0x52 (44.44%). Encriptado: .::::r7!&7r7!r'<r!71 7&=r7<r&7*&=r">3<=ri{r:3+r#'7r" =&757 >=ss
	[...]


Sobre el texto plano original del archivo (``este es un secreto en texto plano...``) se avanza byte a byte (caracter a caracter, letra a letra) haciendo una XOR entre el byte del texto y el byte de la clave (un numero entre 0 y 255, los valores posibles de 8 bits = 1 byte) y se devuelve el texto cifrado (producto de cifrar cada letra por separado). Esto se repite para todas las claves posibles. Como se observa en la primera linea, el texto original quedo sin modificaciones dado que se lo encripto con la clave cero, que para la operacion XOR significa dejar el valor original.

(La operacion XOR entre dos bits se la puede interpretar como un bit de "entrada" y otro de "flip" que determina si se devuelve el bit original o su inversa, si el bit "flip" esta en cero el bit de "entrada" queda igual, si el bit de "flip" esta en 1 se devuelve el bit de "entrada" invertido.)

El numero entre parentesis representa el porcentaje de bytes (letras) del string resultante del texto cifrado que son caracteres alfanumericos, esto nos sirve como medida (aproximada) de que tan "oculto" quedo nuesto mensaje de texto plano (ver mas adelante para un analisis mas detallado).

Para otros valores (mayores a cero) de la clave de encripcion, se puede ver como el texto original cambia en forma dramatica, de manera que ya no es inteligible a simple vista (por un humano, aunque no quiere decir que la encripcion sea perfecta o que no se pueda obtener ninguna informacion del texto cifrado).

(Valores mas grandes de la clave, que tienen mas bits en 1, generan mayor inversion de los bits de entrada del texto plano, lo que resulta en strings de texto cifrado cada vez mas irreconocibles y mas parecidas a "basura" o valores aleatorios).


Encripcion por bloques
======================

El tipo de encripcion anterior se denomina encripcion por bloques (https://es.wikipedia.org/wiki/Cifrado_por_bloques), donde se separa el texto plano de entrada en bloques y se lo encripta por partes, a cada bloque por separado, y luego se vuelve a juntar todos los bloques de texto cifrado en un solo elemento, el cual es la salida de toda la operacion de encripcion. Este es el tipo de encripcion que va a aparecer en los challenges de esta categoria.

Particularmente para el challenge de ``xor_cero`` (ejemplo anterior) se aplico su variante mas sencilla, ECB (https://es.wikipedia.org/wiki/Cifrado_por_bloques#Electronic_Code-Book_.28ECB.29, https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Electronic_Codebook_.28ECB.29
), donde a cada uno de esos bloques se lo encripta con la misma funcion, en el ejemplo, la operacion XOR (aunque pueden elegirse otras, la funcion de encripcion no depende del modo de encripcion, sino que se elije aparte) y siempre se utiliza la misma clave, en el ejemplo, siempre se hacia XOR con el mismo valor para todos los caracteres del string para una encripcion particular. Esto significa que si dos bloques de entrada son iguales, sus respectivos bloques encriptados tambien seran iguales, lo que puede verificarse facilmente en los textos cifrados mostrados antes, donde las primeras letras, de la 2 a la 5, son siempre iguales para cualquier clave de encripcion utilizada, porque siempre se esta encriptando a la misma letra (bloque de entrada), ``h``, repetida 4 veces, con la misma clave.

Entonces, el challenge de ``xor_cero`` puede pensarse como el caso mas simple del cifrado en bloque, donde cada bloque tiene un largo de 1 byte y la clave tambien tiene largo de 1 byte, con la funcion de encripcion de XOR. En casos reales de aplicacion, como por ejemplo en el estandar de encripcion de industria AES (https://en.wikipedia.org/wiki/Advanced_Encryption_Standard), el tamaño del bloque son 128 bits (16 bytes) y las claves pueden tener largos desde 128 bits (16 bytes) a 256 bits (32 bytes), ademas, la funcion de encripcion es mucho mas compleja que una simple operacion de XOR.


Reconocimiento del texto plano desencriptado
============================================

Al desencriptar el texto cifrado se vuelve al texto plano original, pero surge la pregunta, como saber si el texto desencriptado es realmente el texto plano original? No hay una respuesta que aplique para todos los casos porque depende mucho del tipo de informacion que se esta encriptando.

En el caso mas sencillo, si el texto plano (que no necesariamente es texto, puede ser cualquier cadena de bits) es un texto humano en español, simplemente puede verificarse de que el texto plano recuperado pueda leerse y entenderse, que tenga letras del alfabeto y sea coherente.

Pero si por ejemplo, el texto plano original es simplemente una cadena aleatoria de bits sin ningun patron o estructura definida, como puede saberse, luego de realizar la desencripcion, que el resultado de la misma es efectivamente el texto plano original o hubo un error en el proceso de desencripcion o se utilizo una clave erronea para desencriptarlo? La respuesta a este segundo caso es que es imposible estar seguros, porque por definicion del ejemplo, el texto plano creado no tiene ningun patron reconocible (ni para un humano ni para una maquina), asi que sin conocer a priori cual fue el texto plano original, no podemos saber si el texto plano desencriptado es efectivamente el original, si la desencripcion fue "valida".

Este ultimo es el caso mas extremo (porque normalmente la informacion que se encripta tiene un patron reconocible) pero sirve para delimitar los casos mas extremos entre una situacion donde es obvia que recuperamos el texto plano original (porque lo podemos leer a simple vista) y el otro donde no es posible certificar si la desencripcion nos llevo al texto original o no.

En el caso del ejemplo anterior se utilizo un indicador aproximado que fue la proporcion de los caracteres alfanumericos en los strings (registrados entre parentesis a la derecha de la clave de encripcion). Este puede ser un indicador aceptable de que la desencripcion funciono correctamente, aunque se podria hacer en forma manual con una simple inspeccion, tiene la ventaja de que permite automatizar el proceso de deteccion. De todas formas hay que resaltar de que es solo un aproximado, de hecho, en la lista mostrada antes, hay textos cifrados que tienen un porcentaje muy cercano al del texto plano original, lo que da el indicio de que desencripciones errardas (e.g., con la clave equivocada) pueden dar tambien porcentajes bastante altos (generando falsos positivos).


Resolucion de ``xor_cero``: metodo de fuerza bruta
==================================================

Todo lo anterior puede dar indicios de una posible resolucion del primer challenge ``xor_cero``, donde nos dan una cadena de bits que en principio no sabemos que formato tienen. Al descargar el archivo que contiene la cadena de bits y aplicar el comando ``file`` para tratar de obtener alguna informacion, el comando simplemente reporta el tipo generico ``data``, que suele significar que no pudo reconocer un patron conocido, comparese con lo que repota ``file`` al aplicarlo al archivo de ejemplo ``secreto.txt``, donde lo identifica claramente como un archivo de texto.

.. code:: bash

	user@ubuntu-pc:~/ctf_junior_2017/crypto$ file xor_cero 
	xor_cero: data
	user@ubuntu-pc:~/ctf_junior_2017/crypto$ file secreto.txt 
	secreto.txt: ASCII text, with no line terminators

Sin poder determinar el tipo de datos, podemos asumir que es un texto cifrado, ya que una de las propiedades del texto cifrado es aparentar "no ser nada en particular" (aleatorio, sin un formato definido). Dentro del contexto de este challenge vamos a suponer que el modo de encripcion es en bloques, en el modo ECB, con la funcion de encripcion XOR (por supuesto que en casos de uso reales de encripcion el mecanismo es mucho mas complejo).

El problema es que la clave de encripcion no esta disponible, no se sabe que valor particular fue el que se aplico, junto con la XOR, a cada byte del mensaje de texto plano original. Lo ventajoso de este caso en particular es que dado que la clave es simplemente 1 byte (8 bits), hay solo (como se menciono antes) 256 claves posibles que se pueden aplicar. Entonces simplemente puede probarse en forma programatica todas las combinaciones posibles y estudiar los textos desencriptados resultantes. Como se discutio antes, el uso de una clave erronea probablemente resulte en un texto plano con poco "sentido", mientras que el texto plano original (producto de aplicar la clave correcta entre la 256 posibles) tendra algun patron reconocible como, por ejemplo, un alto porcentaje de caracteres alfanumericos.

Comparese este caso de ejemplo contra el uso real de encripcion en las paginas HTTPS (GMail, Facebook, Twitter, etc.), donde la informacion (nuestras claves privadas de acceso) viajan en forma encriptada con el estandar AES de 128 bits de clave, lo que representa un universo posible de 2**128 claves distintas a probar para poder "romper" la encripcion (contra 2**8 = 256 claves posibles del ejemplo). Notese que la dificultad aumenta, no en forma lineal, sino en forma exponencial, la clave de 128 bits no es 20 veces mas segura que la de 8, sino un numero tan grande de veces que hasta resulta dificil ponerlo en palabras.

Queda para el lector investigar mas a fondo el codigo de ``example.py`` para entender un poco mejor el mecanismo de encripcion (y desencripcion) utilizado, para ver como puede aplicarse a la resolucion del challenge de ``xor_cero``. Por supuesto que no es necesario utilizar ese codigo particular para la resolucion, ni tampoco Python, pero queda a disposicion como una ayuda para orientar la posible solucion.

Tener en cuenta ademas que el codigo que se utilice para este challenge probablemente pueda reutilizarse en parte para los otros challenges de criptografia, asi que es recomendable diseñar una solucion en forma modular (organizando el codigo en distintas funciones y/o clases para distintos propositos) de manera de poder volver a emplear en el futuro. 


Encripcion por bloques: CBC
===========================

La variante ECB de la encripcion por bloques tiene una falla fundamental, independiente de la funcion de encripcion en si que se utilice (XOR, AES, etc): su predecible repeticion, esto es, que para un mismo bloque de entrada y una misma clave siempre se va a tener como resultado el mismo bloque de texto cifrado. Aunque puede parecer un detalle menor es una falla que puede entregar una gran informacion para atacar la encripcion.

Tomando el mismo ejemplo anterior de la encripcion con XOR, se pudo observar claramente que para la misma letra original de texto plano, una clave de encripcion siempre generaba el mismo byte de texto cifrado, independientemente de cual sea ese byte. Entonces, si se sabe que el texto original es un texto humano del lenguaje español, podriamos identificar claramente donde estan las vocales en el texto original simplemente buscando los caracteres que mas se repitan en el texto cifrado, independientemente de cual sea ese caracter (o sea, independientemente de cual fuera la clave utilizada). Una vez identificadas las vocales, por ejemplo la E (que es la letra mas utilizada del diccionario) y su correspondiente caracter en el texto cifrado, simplemente se busca el valor que hace que la XOR convierta (invirtiendo bits determinados) de la E al caracter cifrado, y esa sera la clave de encripcion, que nos permita desencriptar todo el texto cifrado. Esto es lo que se conoce como un analisis de frecuencias (https://es.wikipedia.org/wiki/An%C3%A1lisis_de_frecuencias) y aunque se describio de una manera muy burda se puede llevar a cabo con extraordinaria precision, no solo para texto humano sino para cualquier tipo de datos con un patron reconocible.

Hay una imagen en wikipedia (https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Electronic_Codebook_.28ECB.29) que ilustra esto de manera muy elegante, tomando como texto plano una imagen del pinguino de Linux (a la izquierda) y encriptandola con el modo ECB (en el centro) y el modo CBC (derecha), que es otra variante de la encripcion por bloques (que vamos a discutir a continuacion) sin esta falla. Aunque las dos encripciones transforman la imagen a otro formato distinto del texto plano, los patrones de la figura son claramente distinguibles en la encripcion ECB, mientras que en la CBC resultan totalmente aleatorios (a simple vista), mucho mejor "escondidos" (opacados).

Todo este analisis aplica no solo para el ejemplo anterior de encripcion con bloques y claves de 1 byte de longitud y la funcion de encripcion de XOR, sino que la falla es propia del modo ECB y sucede para cualquier longitud de bloques/claves (aunque bloques mas grandes pudean mitigar un poco el problema).

Algunos de los challenges posteriores al ``xor_cero`` utilizaran el modo CBC de encripcion, o variantes del mismo, por lo que resulta util entender un poco mas como funciona.

La variante CBC (https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Cipher_Block_Chaining_.28CBC.29) consiste en 
conectar de alguna manera la encripcion de cada bloque con el resultado de la encripcion del bloque anterior, de manera de que aunque siempre se aplique la misma funcion de encripcion (XOR, AES, etc) con la misma clave, el resultado nunca (idealmente) sera el mismo incluso si el bloque de entrada es el mismo, dado que la encripcion esta "encadenada" y cada bloque encriptado depende no solo de la encripcion del bloque actual sino de todos los bloques anteriores, de su "historial".

Aunque no se va a describir en detalle el modo CBC si es importante notar un detalle, de que "historial" va a depender el bloque inicial? Aunque parece un detalle menor es un problema que lleva a una situacion similar a la de ECB, aunque solo para el primer bloque de encripcion (e.g., la primera letra). La solucion fue ingresar un valor aleatorio denominado IV (vector de inicializacion) que simula este "historial" inexistente para el primer bloque. La consecuencia de esto es que hay una "doble clave" en el modo CBC de encripcion, no solo esta la clave propiamente dicha de la funcion de encripcion usada, sino tambien es necesario conocer el valor del IV, que se puede decir que funciona como una "segunda clave", porque si no se conoce este valor, incluso sabiendo la clave principal, la desencripcion va a fallar porque el IV erroneo que se utilice va a generar un efecto en cadena que haga que todas las posteriores desencripciones de los bloques (que dependen del valor inicial) tambien fallen.

La manera de "mezclar" la encripcion del bloque actual con la del anterior, generando este efecto de "cadena", es de, en vez de utilizar directamente el bloque de texto plano como entrada a la funcion de encripcion, se "mezcla" este bloque de texto plano con el texto cifrado del bloque anterior, utilizando una operacion de XOR (que no debe confundirse con la operacion XOR que se estuvo utilizando como funcion de encripcion en el ejemplo anterior, pero que podria haber sido reemplazada con la funcion AES o cualquier otra).

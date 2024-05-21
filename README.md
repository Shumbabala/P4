PAV - P4: reconocimiento y verificación del locutor
===================================================

Obtenga su copia del repositorio de la práctica accediendo a [Práctica 4](https://github.com/albino-pav/P4)
y pulsando sobre el botón `Fork` situado en la esquina superior derecha. A continuación, siga las
instrucciones de la [Práctica 2](https://github.com/albino-pav/P2) para crear una rama con el apellido de
los integrantes del grupo de prácticas, dar de alta al resto de integrantes como colaboradores del proyecto
y crear la copias locales del repositorio.

También debe descomprimir, en el directorio `PAV/P4`, el fichero [db_8mu.tgz](https://atenea.upc.edu/mod/resource/view.php?id=3654387?forcedownload=1)
con la base de datos oral que se utilizará en la parte experimental de la práctica.

Como entrega deberá realizar un *pull request* con el contenido de su copia del repositorio. Recuerde
que los ficheros entregados deberán estar en condiciones de ser ejecutados con sólo ejecutar:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~.sh
  make release
  run_spkid mfcc train test classerr verify verifyerr
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Recuerde que, además de los trabajos indicados en esta parte básica, también deberá realizar un proyecto
de ampliación, del cual deberá subir una memoria explicativa a Atenea y los ficheros correspondientes al
repositorio de la práctica.

A modo de memoria de la parte básica, complete, en este mismo documento y usando el formato *markdown*, los
ejercicios indicados.

## Ejercicios.

### SPTK, Sox y los scripts de extracción de características.

- Analice el script `wav2lp.sh` y explique la misión de los distintos comandos involucrados en el *pipeline*
  principal (`sox`, `$X2X`, `$FRAME`, `$WINDOW` y `$LPC`). Explique el significado de cada una de las 
  opciones empleadas y de sus valores.

  En total hay el empleo de 5 comandos distintos, tal y como nos dice este enunciado, cada uno con opciones o argumentos distintos, así que vamos a desglosarlo todo por completo para poder entenderlo bien. En concreto solo hay un comando que es separado del programa principal de procesado de la señal (`SPTK`) que es el primero (`sox`):

  Veamos rápidamente el pipeline de comandos que se va a tratar:

  ```shell
  # Main command for feature extration
  sox $inputfile -t raw -e signed -b 16 - | $X2X +sf | $FRAME -l 240 -p 80 | $WINDOW -l 240 -L 240 |
	$LPC -l 240 -m $lpc_order > $base.lp || exit 1
  ```

  donde las variables tienen la siguiente pre-declaración en el mismo script, claro:

  ```shell
  X2X="x2x"
  FRAME="frame"
  WINDOW="window"
  LPC="lpc"
  ```

  * `sox`

    * Usamos `sox` para convertir el fichero de audio en formato *raw* con codificación de *signed integer* también definiendo la cantidad de bits usados en la codificación (de *signed integer*) por cada muestra (16). La "raya" final **-** significa que queremos redireccionar la salida del programa para otro sitio que no sea el típico stdout.

  * `x2x`

    * Ahora de entrada tenemos las muestras de audio en formato *raw* codificados como *signed integer* con 16 bits (2 bytes) por lo tanto ahora queremos transformar estos datos en tipos *float* (4 bytes). Esto lo indicamos mediante el argumento de `+sf`, donde `+` significa que estamos especificando el formato de las muestras de entrada, seguido por el format en sí (tipo short que es de 2 bytes, es decir, 16 bits), seguido por `f`, es decir, el formato en el que queremos convertir estos "shorts", que es en formato float (4 bytes cada uno). A continuación vemos un ejemplo de uso del mismo manual de referencia del software **SPTK** que nos dió una mejor idea del significado de estos argumentos:

    ![ejemplo uso SPTK x2x command](img/x2x_man_example.png)

  * `frame`
    * Este comando de nuevo es otro de la librería del **SPTK**. Su función es la de ingerir como entrada un seguido de muestras (el señal) y las convierte en tramas de longitud dada por la opción `-l` (en nuestro caso es 240 muestras) y de periodicidad dada por la otra opción `-p` (en nuestro caso es 80). Esto quiere decir que de toda la secuencia de muestras de señal de entrada (los floats de salida del comando **x2x**) se enventanan, inicialmente, 240 muestras, se envian como un grupo conjunto de datos, luego la ventana se desplaza por `-p`, es decir 80 en nuestro caso, y así sucesivamente, la ventana se va desplazando. Esto quiere decir que ventanas consecutivas tendran 240 - 80 muestras iguales, debido al solapamiento entre dichas tramas/ventanas.

    Tampoco olvidar que dichos números los podemos traduciar a su equivalente "analógico", ya que sí sabemos que estamos trabajando con frecuencia de muestreo de 8 kHz (periodo T = 0,125 us), tenemos tramas de duración 240 * 0,125 = **30 ms** con desplazamientos de 80 * 0,125 us = **10 ms**.

    A continuación vemos un ejemplo de uso de este comando, extraído directamente del manual de referencia oficial, donde la señal de entrada tiene **T** muestras, y generamos tramas de longitud **L** con periodicidad **P** (solapamiento de **L-P** muestras):

    ![ejemplo uso SPTK frame command](img/frame_man_example.png)

  * `window`

    *  Este comando se usa para filtrar las tramas obtenidas con el comando anterior. Teniendo en cuenta que ahora tenemos multiples tramas de longitud **L**, y sabiendo que la ventana de filtrado por defecto es la **Blackman**, multiplicamos cada trama (de longitud indicaca por la opción `-l`, que es 240) por una ventada de dicho tipo de la misma longitud (indicado por el valor de la opción `-L`, que es 240 otra vez). Si jamás ubiese distintos valores de `-l` o `-L`, se aplicaria padding sin problema alguno.

    Una vez este procesado se ha aplicado, llegamos al último comando del pipeline (o penúltimo, si consideras la redirección a fichero modificado como paso esencial).

  * `lpc`

    * En el manual de referencia, se dice que este comando realiza análisis **LPC** mediante el algoritmo de optimización de computación `Levinson-Durbin`. Tenemos indicado dos opciones, la primera, `-l`, indica la longitud de cada trama de entrada (que volvemos a poner a 240) y la segunda opción, `-m`, indica el orden del filtro LPC. El valor de esta opción es decidido por el mismo usuario, pasando el valor como primer argumento del script de llamada

    ```shell
    lpc_order=$1
    ```
    Finalmente la ejecución finaliza, si todo ha ido bien, escribiendo dichos valores de los coeficientes de LP (junto con el valor de la ganancia de predicción).

- Explique el procedimiento seguido para obtener un fichero de formato *fmatrix* a partir de los ficheros de
  salida de SPTK (líneas 45 a 51 del script `wav2lp.sh`).

  Ya se han tratado las líneas 45-46 en la pregunta anterior, por lo tanto ahora vamos a discutir las líneas 50-51, donde escribimos y realizamos el "esqueleto" del fichero fmatrix (que se acaba construyendo en las últimos líneas posteriores).

  ```shell
  # Our array files need a header with the number of cols and rows:
  ncol=$((lpc_order+1)) # lpc p =>  (gain a1 a2 ... ap) 
  nrow=`$X2X +fa < $base.lp | wc -l | perl -ne 'print $_/'$ncol', "\n";'`
  ```

  Estos comandos shell simplemente cogen toda la información del fichero `$base.lp`, convierte esta información (que está en formato de float (4 bytes) a carácteres ASCII). A continuación se cuentan la cantidad de líneas producidas por el comando anterior `$X2X`. La invocación final a `perl` simplemte itera sobre el input que se le dió (en este caso es el numero de filas) y divide dicha cantidad de filas por el numero de columnas y así tenemos declaradas las variables de `ncols` y `nrows`, que luego usaremos en las últimas lineas del script para generara la cabecera de este fichero `fmatrix`.

  * ¿Por qué es más conveniente el formato *fmatrix* que el SPTK?

  Usamos este formato modificado *fmatrix* en vez de *SPTK* porque es un formato más sencillo de usar e inteligible.

- Escriba el *pipeline* principal usado para calcular los coeficientes cepstrales de predicción lineal
  (LPCC) en su fichero <code>scripts/wav2lpcc.sh</code>:

  En dicho nuevo fichero, solamente hemos añadido unos cuantos detallitos adicionales, para tener en cuenta un nuevo argumento que el usuario debe proporcionar de entrada, que es el orden del cepstrum a computar (que luego se pasará al argumento `-M` del nuevo comando de SPTK). También hemos añadido una línea para hacer la declaración del nuevo comando que hace llamada a la función `lpc2c` de la librería (pasándole los argumentos necesarios) y finalmente acoplando dicho comando al pipeline principal. 

  A continuación se enseña la parte principal del código añadido (con diferencia del <code>scripts/wav2lp.sh</code>), aunque para ver todos los detalles puede consultar directamente dicho fichero en la carpeta de `scripts/`, por supuesto:

  ```shell
  #new lpcc command declaraction
  lpcc_command = "$LPCC -m $lpc_order -M $lpcc_order"

  # Main command for feature extration
  sox $inputfile -t raw -e signed -b 16 - | $X2X +sf | $FRAME -l 240 -p 80 | $WINDOW -l 240 -L 240 |
	$LPC -l 240 -m $lpc_order | lpcc_command > $base.lp || exit 1
  ```

  Aquí no quitamos la orden de computación de los coeficientes LP ya que deben ser usados para computar los LPCC posteriores, cosa que en el apartado a continuación no es así.

- Escriba el *pipeline* principal usado para calcular los coeficientes cepstrales en escala Mel (MFCC) en su
  fichero <code>scripts/wav2mfcc.sh</code>:

  Igual que en el apartado anterior, procedemos a enseñar sólo el código de declaración de la nueva invocación y su integración en el pipeline principal. La resta del código se puede encontrar en dicho nuevo fichero *.sh*:

  ```shell
  #new mfcc command declaraction
  mfcc_command = "$MFCC -l 240 -s 8 -m $mfcc_order -n $mel_filter_bank_order"

  # Main command for feature extration
  sox $inputfile -t raw -e signed -b 16 - | $X2X +sf | $FRAME -l 240 -p 80 | $WINDOW -l 240 -L 240 |
	mfcc_command > $base.lp || exit 1
  ```

  Hemos borrado el comando de computación de los LPC ya que el comando `mfcc` requiere de entrada los datos/muestras de audio (que en nuestro caso han sido ya enventanadas). `-l = 240` porque este es el tamaño de los ventanas de entrada, `-s 8` porque la frecuencia de muestreo es de 8 kHz y las demás opcines son entradas por el usuario. Existen muchas otras opciones pero se dejan o en estado de *FALSE* (por defecto) o con sus valores por defecto, si las opciones son de tipo numérico, como por ejemplo `-a` que representa el coeficiente de preemfasi (default = 0.97). 

### Extracción de características.

- Inserte una imagen mostrando la dependencia entre los coeficientes 2 y 3 de las tres parametrizaciones
  para todas las señales de un locutor.
  
  + Indique **todas** las órdenes necesarias para obtener las gráficas a partir de las señales 
    parametrizadas.

    Hemos de tener en cuenta que por ahora solo nos piden usar como ejemplo las señales de un único locutor, no de toda la database. Para hacer la ejecución más rápida, hemos modificado la parte del script `run_spkid.sh` responsable por procesar el argumento cuando solo queremos computar los *feats* como por ejemplo los *lpc, lpcc o mfcc*, en concreto el último *elif* del código:

    ```shell
    # If the command is not recognize, check if it is the name
    # of a feature and a compute_$FEAT function exists.
    elif [[ "$(type -t compute_$cmd)" = function ]]; then
        FEAT=$cmd
        #compute_$FEAT $db_devel $lists/class/all.train $lists/class/all.test

        #solo las señales de un locutor
        compute_$FEAT $db_devel $lists/class/SES000.train # 15 wavs in total (so 15 output .lp files)
    ```

    De esta manera en lugar de ejecutar sobre la database entera, solo ejecutamos sobre las grabaciones de un locutor, en concreto el locutor **SES000**.

    Ahora solo falta invocar a `run_spkid $FEAT` donde `$FEAT` puede coger uno de los siguientes 3 valores: `lp, lpcc o mfcc` y a partir de ahí tendremos un directorio que en nuestra configuración se llama `work/` donde dentro tendremos los ficheros de salida con los coeficientes solicitados. Los ficheros con los coeficientes *lp* estaran en el directorio `work/lp/`, los coeficientes *lpcc* en el directorio `work/lpcc/` y así sucesivamente.

    Una vez tenemos los ficheros con los coeficientes computados (en este caso tendremos 15 ficheros .lp ya que nuestro locutor elegido tiene 15 ficheros de grabaciones de audio), hemos de usar el comando `fmatrix_show` dentro de un pipeline que nos extraerá concretamente los coeficientes número 4 y 5 (realmente estamos hablando del coeficiente quinto y sexto debido a que el indexado comienza en el 0) y estos valores los metemos dentro de un nuevo fichero llamado `lp_2_3.txt` (para el caso de los coeficientes `lp`). La dos letras iniciales es la parte que varia en función de si estamos trabajando con otro tipos de coeficientes. A continuación mostramos los pasos en código y el output que se debe ir siguiendo para hacer bien este proceso:

    ```shell
    shumbabala@Gerards-MacBook-Air P4 % run_spkid lp
    Fri May 10 11:35:24 CEST 2024: lp ---
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S01.wav work/lp/BLOCK00/SES000/SA000S01.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S02.wav work/lp/BLOCK00/SES000/SA000S02.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S05.wav work/lp/BLOCK00/SES000/SA000S05.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S06.wav work/lp/BLOCK00/SES000/SA000S06.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S07.wav work/lp/BLOCK00/SES000/SA000S07.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S08.wav work/lp/BLOCK00/SES000/SA000S08.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S10.wav work/lp/BLOCK00/SES000/SA000S10.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S15.wav work/lp/BLOCK00/SES000/SA000S15.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S16.wav work/lp/BLOCK00/SES000/SA000S16.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S17.wav work/lp/BLOCK00/SES000/SA000S17.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S20.wav work/lp/BLOCK00/SES000/SA000S20.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S21.wav work/lp/BLOCK00/SES000/SA000S21.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S23.wav work/lp/BLOCK00/SES000/SA000S23.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S25.wav work/lp/BLOCK00/SES000/SA000S25.lp
    wav2lp 8 spk_8mu/speecon/BLOCK00/SES000/SA000S29.wav work/lp/BLOCK00/SES000/SA000S29.lp
    Fri May 10 11:35:24 CEST 2024
    ```
    Ahora ejecutamos el fmatrix_show pipeline:

    ```shell
    shumbabala@Gerards-MacBook-Air P4 % fmatrix_show work/lp/BLOCK00/SES000/*.lp |
    egrep '^\[' | cut -f4,5 > lp_2_3.txt
    ```

    El fichero `lp_2_3.txt` tiene el siguiente aspecto (solo mostramos unas cuantas filas):

    ```shell
    1.7994	-1.33765
    1.05924	-0.326611
    1.06361	-0.106409
    1.05197	0.0156104
    1.13152	-0.415513
    0.949314	-0.235506
    0.961886	-0.0863551
    ```

    Repites el procedimiento para los demás 2 tipos de coeficientes y tendrás 3 ficheros con los coeficientes .txt. No olvidar que hemos usado el valor por defecto de 8 coeficients para los **LP**, 10 coeficientes para los **LPCC** y 10 también para los **MFCC**. Usamos ahora un programa `Python` para que nos grafique estas coordenadas. El fichero es el llamado `coordinate_grapher.py`, allí puede encontrar su código. Trabajo hecho.
 
  + ¿Cuál de ellas le parece que contiene más información?

- Usando el programa <code>pearson</code>, obtenga los coeficientes de correlación normalizada entre los
  parámetros 2 y 3 para un locutor, y rellene la tabla siguiente con los valores obtenidos.

  |                        | LP   | LPCC | MFCC |
  |------------------------|:----:|:----:|:----:|
  | &rho;<sub>x</sub>[2,3] |      |      |      |
  
  + Compare los resultados de <code>pearson</code> con los obtenidos gráficamente.
  
- Según la teoría, ¿qué parámetros considera adecuados para el cálculo de los coeficientes LPCC y MFCC?

### Entrenamiento y visualización de los GMM.

Complete el código necesario para entrenar modelos GMM.

- Inserte una gráfica que muestre la función de densidad de probabilidad modelada por el GMM de un locutor
  para sus dos primeros coeficientes de MFCC.

- Inserte una gráfica que permita comparar los modelos y poblaciones de dos locutores distintos (la gŕafica
  de la página 20 del enunciado puede servirle de referencia del resultado deseado). Analice la capacidad
  del modelado GMM para diferenciar las señales de uno y otro.

### Reconocimiento del locutor.

Complete el código necesario para realizar reconociminto del locutor y optimice sus parámetros.

- Inserte una tabla con la tasa de error obtenida en el reconocimiento de los locutores de la base de datos
  SPEECON usando su mejor sistema de reconocimiento para los parámetros LP, LPCC y MFCC.

### Verificación del locutor.

Complete el código necesario para realizar verificación del locutor y optimice sus parámetros.

- Inserte una tabla con el *score* obtenido con su mejor sistema de verificación del locutor en la tarea
  de verificación de SPEECON. La tabla debe incluir el umbral óptimo, el número de falsas alarmas y de
  pérdidas, y el score obtenido usando la parametrización que mejor resultado le hubiera dado en la tarea
  de reconocimiento.
 
### Test final

- Adjunte, en el repositorio de la práctica, los ficheros `class_test.log` y `verif_test.log` 
  correspondientes a la evaluación *ciega* final.

### Trabajo de ampliación.

- Recuerde enviar a Atenea un fichero en formato zip o tgz con la memoria (en formato PDF) con el trabajo 
  realizado como ampliación, así como los ficheros `class_ampl.log` y/o `verif_ampl.log`, obtenidos como 
  resultado del mismo.

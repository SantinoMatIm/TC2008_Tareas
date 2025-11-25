/*
 * Generador de modelo 3D OBJ para edificio tipo cono truncado
 *
 * Uso:
 *   node edificio.js <lados> <altura> <radioBase> <radioCima>
 *
 * Parámetros:
 *   lados: número entero entre 3 y 36 (por defecto: 8)
 *   altura: altura del edificio, flotante positivo (por defecto: 6.0)
 *   radioBase: radio del círculo en la base, flotante positivo (por defecto: 1.0)
 *   radioCima: radio del círculo en la cima, flotante positivo (por defecto: 0.8)
 */

'use strict';

const fs = require('fs');

// Configuración por defecto
const VALORES_DEFECTO = {
    lados: 8,
    altura: 6.0,
    radioBase: 1.0,
    radioCima: 0.8
};

// Restricciones de validación
const RESTRICCIONES = {
    minLados: 3,
    maxLados: 36
};

// Procesar argumentos de línea de comandos
function procesarArgumentos() {
    const argumentos = process.argv.slice(2);

    const config = {
        lados: VALORES_DEFECTO.lados,
        altura: VALORES_DEFECTO.altura,
        radioBase: VALORES_DEFECTO.radioBase,
        radioCima: VALORES_DEFECTO.radioCima
    };

    // Leer argumentos posicionales
    if (argumentos.length >= 1) {
        config.lados = parseInt(argumentos[0], 10);
    }
    if (argumentos.length >= 2) {
        config.altura = parseFloat(argumentos[1]);
    }
    if (argumentos.length >= 3) {
        config.radioBase = parseFloat(argumentos[2]);
    }
    if (argumentos.length >= 4) {
        config.radioCima = parseFloat(argumentos[3]);
    }

    // Validar configuración
    validarConfiguracion(config);

    // Generar nombre de archivo de salida
    const l = config.lados;
    const a = config.altura;
    const rb = config.radioBase;
    const rc = config.radioCima;
    config.archivoSalida = `edificio_${l}_${a}_${rb}_${rc}.obj`;

    return config;
}

// Validar parámetros de entrada
function validarConfiguracion(config) {
    // Validar número de lados
    if (isNaN(config.lados) || config.lados < RESTRICCIONES.minLados) {
        config.lados = RESTRICCIONES.minLados;
        console.warn(`Advertencia: número de lados ajustado a ${RESTRICCIONES.minLados}`);
    }
    if (config.lados > RESTRICCIONES.maxLados) {
        config.lados = RESTRICCIONES.maxLados;
        console.warn(`Advertencia: número de lados ajustado a ${RESTRICCIONES.maxLados}`);
    }

    // Validar altura
    if (isNaN(config.altura) || config.altura <= 0) {
        console.error('Error: la altura debe ser mayor que 0');
        process.exit(1);
    }

    // Validar radios
    if (isNaN(config.radioBase) || config.radioBase <= 0) {
        console.error('Error: el radio de la base debe ser mayor que 0');
        process.exit(1);
    }
    if (isNaN(config.radioCima) || config.radioCima <= 0) {
        console.error('Error: el radio de la cima debe ser mayor que 0');
        process.exit(1);
    }
}

// Generar perfil de radios a lo largo de la altura del edificio
function generarPerfil(config) {
    // Crear perfil con múltiples segmentos para formas más interesantes
    const rb = config.radioBase;
    const rc = config.radioCima;
    const h = config.altura;

    // Calcular número de segmentos según la altura
    // Más altura requiere más segmentos para mejor detalle
    const numSegmentos = Math.max(3, Math.min(Math.floor(h / 2), 8));

    const perfil = [];

    for (let i = 0; i < numSegmentos; i++) {
        const factor = i / (numSegmentos - 1);  // Factor de interpolación [0, 1]

        let radio;

        if (i === 0) {
            // Primer segmento siempre usa el radio de la base
            radio = rb;
        } else if (i === numSegmentos - 1) {
            // Último segmento siempre usa el radio de la cima
            radio = rc;
        } else {
            // Segmentos intermedios: interpolación lineal base + variación
            const radioBase = rb + (rc - rb) * factor;

            // Factor de abultamiento para crear formas más interesantes
            const factorAbultamiento = 0.3;

            // Variación sinusoidal para crear forma con abultamiento en el medio
            // sin(π*factor) alcanza su máximo en el medio (factor = 0.5)
            const variacion = Math.sin(Math.PI * factor) * factorAbultamiento * Math.max(rb, rc);

            radio = radioBase + variacion;
        }

        perfil.push(radio);
    }

    return perfil;
}

// Generar anillos de vértices alrededor del edificio
function generarAnillos(config, perfil) {
    const vertices = [];
    const numAnillos = perfil.length;
    const numLados = config.lados;
    const altura = config.altura;

    for (let anillo = 0; anillo < numAnillos; anillo++) {
        const y = (anillo / (numAnillos - 1)) * altura;
        const radio = perfil[anillo];

        for (let lado = 0; lado < numLados; lado++) {
            const angulo = (lado / numLados) * 2.0 * Math.PI;
            const x = radio * Math.cos(angulo);
            const z = radio * Math.sin(angulo);

            vertices.push({ x: x, y: y, z: z });
        }
    }

    return vertices;
}

// Calcular normales laterales por sector usando cálculo de derivadas
function calcularNormalesSector(numLados, radio0, radio1, alturaSegmento) {
    const normales = [];
    const pasoAngular = 2.0 * Math.PI / numLados;

    // Radio promedio y derivada del radio respecto a la altura
    const radioMedio = (radio0 + radio1) / 2.0;
    const derivadaRadio = (radio1 - radio0) / alturaSegmento;

    for (let i = 0; i < numLados; i++) {
        // Ángulo central del sector
        const theta = (i + 0.5) * pasoAngular;

        // Derivadas parciales de la superficie paramétrica p(theta, y)
        // Derivada respecto a theta: p_theta = (-r*sin(theta), 0, r*cos(theta))
        const dpt_x = -radioMedio * Math.sin(theta);
        const dpt_y = 0.0;
        const dpt_z = radioMedio * Math.cos(theta);

        // Derivada respecto a y: p_y = (r'*cos(theta), 1, r'*sin(theta))
        const dpy_x = derivadaRadio * Math.cos(theta);
        const dpy_y = 1.0;
        const dpy_z = derivadaRadio * Math.sin(theta);

        // Normal = producto cruz p_theta × p_y
        let nx = dpt_y * dpy_z - dpt_z * dpy_y;
        let ny = dpt_z * dpy_x - dpt_x * dpy_z;
        let nz = dpt_x * dpy_y - dpt_y * dpy_x;

        // Normalizar el vector
        const magnitud = Math.sqrt(nx * nx + ny * ny + nz * nz);
        nx /= magnitud;
        ny /= magnitud;
        nz /= magnitud;

        // Asegurar que la componente Y sea positiva (normal apunta hacia afuera)
        if (ny < 0) {
            nx = -nx;
            ny = -ny;
            nz = -nz;
        }

        normales.push({ x: nx, y: ny, z: nz });
    }

    return normales;
}

// Construir caras laterales del edificio
function construirCarasLaterales(config, perfil) {
    const caras = [];
    const numAnillos = perfil.length;
    const numLados = config.lados;

    for (let anillo = 0; anillo < numAnillos - 1; anillo++) {
        for (let lado = 0; lado < numLados; lado++) {
            const siguienteLado = (lado + 1) % numLados;

            // Índices de vértices (basados en 1 para formato OBJ)
            const v0 = anillo * numLados + lado + 1;
            const v1 = anillo * numLados + siguienteLado + 1;
            const v2 = (anillo + 1) * numLados + siguienteLado + 1;
            const v3 = (anillo + 1) * numLados + lado + 1;

            // Dos triángulos por cara cuadrilátera, sentido CCW visto desde fuera
            // Triángulo inferior
            caras.push({
                vertices: [v0, v1, v2],
                normales: [v0, v1, v2]
            });

            // Triángulo superior
            caras.push({
                vertices: [v0, v2, v3],
                normales: [v0, v2, v3]
            });
        }
    }

    return caras;
}

// Construir tapas superior e inferior del edificio
function construirTapas(config, perfil, vertices) {
    const tapas = {
        inferior: [],
        superior: []
    };

    const numLados = config.lados;
    const numAnillos = perfil.length;

    // Tapa inferior (y = 0)
    // Centro en el origen
    const indiceCentroInferior = vertices.length + 1;

    for (let lado = 0; lado < numLados; lado++) {
        const siguienteLado = (lado + 1) % numLados;

        // Índices de vértices en el primer anillo
        const v0 = lado + 1;
        const v1 = siguienteLado + 1;

        // Abanico desde el centro, CCW visto desde abajo (normal hacia -Y)
        tapas.inferior.push({
            vertices: [indiceCentroInferior, v1, v0]
        });
    }

    // Tapa superior (y = altura)
    const indiceCentroSuperior = vertices.length + 2;
    const inicioAnilloSuperior = (numAnillos - 1) * numLados;

    for (let lado = 0; lado < numLados; lado++) {
        const siguienteLado = (lado + 1) % numLados;

        // Índices de vértices en el último anillo
        const v0 = inicioAnilloSuperior + lado + 1;
        const v1 = inicioAnilloSuperior + siguienteLado + 1;

        // Abanico desde el centro, CCW visto desde arriba (normal hacia +Y)
        tapas.superior.push({
            vertices: [indiceCentroSuperior, v0, v1]
        });
    }

    return tapas;
}

// Escribir archivo OBJ con el modelo 3D
function escribirOBJ(config, vertices, normales, carasLaterales, tapas, perfil) {
    const numLados = config.lados;
    const altura = config.altura;
    const numAnillos = perfil.length;

    // Calcular conteos para el encabezado
    // 2 centros + vértices de todos los anillos
    const numVertices = 2 + numLados * numAnillos;
    // 2 normales de tapas + 2 laterales por sector por segmento
    const numNormales = 2 + numLados * (numAnillos - 1) * 2;
    // 2 tapas + 2 triángulos laterales por sector por segmento
    const numCaras = numLados * 2 + numLados * (numAnillos - 1) * 2;

    let contenidoOBJ = '';

    // Encabezado con información del archivo
    contenidoOBJ += `# Archivo OBJ: ${config.archivoSalida}\n`;
    contenidoOBJ += `# ${numVertices} vértices\n`;
    contenidoOBJ += `# ${numNormales} normales\n`;
    contenidoOBJ += `# ${numCaras} caras\n`;

    // Escribir vértices: primero centro inferior, luego todos los anillos, finalmente centro superior
    // Centro inferior (índice 1)
    contenidoOBJ += `v ${(0.0).toFixed(4)} ${(0.0).toFixed(4)} ${(0.0).toFixed(4)}\n`;

    // Vértices de todos los anillos en orden: anillo 0, anillo 1, ..., anillo N-1
    for (let anillo = 0; anillo < numAnillos; anillo++) {
        for (let lado = 0; lado < numLados; lado++) {
            const v = vertices[anillo * numLados + lado];
            contenidoOBJ += `v ${v.x.toFixed(4)} ${v.y.toFixed(4)} ${v.z.toFixed(4)}\n`;
        }
    }

    // Centro superior (último índice)
    contenidoOBJ += `v ${(0.0).toFixed(4)} ${altura.toFixed(4)} ${(0.0).toFixed(4)}\n`;

    // Escribir normales
    // Normal de tapa inferior (apunta hacia abajo, -Y)
    contenidoOBJ += `vn ${(0.0).toFixed(4)} ${(-1.0).toFixed(4)} ${(0.0).toFixed(4)}\n`;

    // Normal de tapa superior (apunta hacia arriba, +Y)
    contenidoOBJ += `vn ${(0.0).toFixed(4)} ${(1.0).toFixed(4)} ${(0.0).toFixed(4)}\n`;

    // Normales laterales: para cada segmento vertical, calcular normales por sector
    for (let seg = 0; seg < numAnillos - 1; seg++) {
        const r0 = perfil[seg];
        const r1 = perfil[seg + 1];
        const alturaSeg = altura / (numAnillos - 1);
        const normalesSeg = calcularNormalesSector(numLados, r0, r1, alturaSeg);

        for (let i = 0; i < numLados; i++) {
            const n = normalesSeg[i];
            // Duplicar cada normal (para los dos triángulos del cuadrilátero)
            contenidoOBJ += `vn ${n.x.toFixed(4)} ${n.y.toFixed(4)} ${n.z.toFixed(4)}\n`;
            contenidoOBJ += `vn ${n.x.toFixed(4)} ${n.y.toFixed(4)} ${n.z.toFixed(4)}\n`;
        }
    }

    // Escribir caras
    const centroInferior = 1;
    const centroSuperior = numVertices;

    // Tapa inferior: conectar centro inferior con primer anillo
    for (let lado = 0; lado < numLados; lado++) {
        const siguienteLado = (lado + 1) % numLados;
        const v0 = 2 + lado;
        const v1 = 2 + siguienteLado;
        // CCW desde abajo (normal hacia abajo)
        contenidoOBJ += `f ${v1}//1 ${centroInferior}//1 ${v0}//1\n`;
    }

    // Caras laterales: para cada segmento vertical
    for (let seg = 0; seg < numAnillos - 1; seg++) {
        for (let lado = 0; lado < numLados; lado++) {
            const siguienteLado = (lado + 1) % numLados;

            // Índices de vértices para este cuadrilátero
            const inicioAnillo0 = 2 + seg * numLados;
            const inicioAnillo1 = 2 + (seg + 1) * numLados;

            const v0 = inicioAnillo0 + lado;
            const v1 = inicioAnillo0 + siguienteLado;
            const v2 = inicioAnillo1 + siguienteLado;
            const v3 = inicioAnillo1 + lado;

            // Índices de normales para este segmento y sector
            const baseNormal = 3 + seg * numLados * 2 + lado * 2;
            const n1 = baseNormal;
            const n2 = baseNormal + 1;

            // Dos triángulos por cuadrilátero
            // Triángulo inferior: v0, v1, v2
            contenidoOBJ += `f ${v2}//${n1} ${v1}//${n1} ${v0}//${n1}\n`;

            // Triángulo superior: v0, v2, v3
            contenidoOBJ += `f ${v3}//${n2} ${v2}//${n2} ${v0}//${n2}\n`;
        }
    }

    // Tapa superior: conectar último anillo con centro superior
    const inicioUltimoAnillo = 2 + (numAnillos - 1) * numLados;
    for (let lado = 0; lado < numLados; lado++) {
        const siguienteLado = (lado + 1) % numLados;
        const v0 = inicioUltimoAnillo + lado;
        const v1 = inicioUltimoAnillo + siguienteLado;
        // CCW desde arriba (normal hacia arriba)
        contenidoOBJ += `f ${v0}//2 ${centroSuperior}//2 ${v1}//2\n`;
    }

    // Escribir archivo
    try {
        fs.writeFileSync(config.archivoSalida, contenidoOBJ);
        console.log(`Archivo generado exitosamente: ${config.archivoSalida}`);
    } catch (error) {
        console.error(`Error al escribir archivo: ${error.message}`);
        process.exit(1);
    }
}

// Función principal
function main() {
    const config = procesarArgumentos();

    console.log('Generando edificio con los siguientes parámetros:');
    console.log(`  Número de lados: ${config.lados}`);
    console.log(`  Altura: ${config.altura}`);
    console.log(`  Radio de la base: ${config.radioBase}`);
    console.log(`  Radio de la cima: ${config.radioCima}`);

    // Construir perfil de radios
    const perfil = generarPerfil(config);
    console.log(`  Número de anillos: ${perfil.length}`);

    // Generar geometría del edificio
    const vertices = generarAnillos(config, perfil);
    const r0 = perfil[0];
    const r1 = perfil[perfil.length - 1];
    const normales = calcularNormalesSector(config.lados, r0, r1, config.altura);
    const carasLaterales = construirCarasLaterales(config, perfil);
    const tapas = construirTapas(config, perfil, vertices);

    const numAnillos = perfil.length;
    const numVertices = 2 + config.lados * numAnillos;
    const numNormales = 2 + config.lados * (numAnillos - 1) * 2;
    const numCaras = config.lados * 2 + config.lados * (numAnillos - 1) * 2;

    console.log(`  Total de vértices: ${numVertices}`);
    console.log(`  Total de normales: ${numNormales}`);
    console.log(`  Total de caras: ${numCaras}`);

    // Escribir archivo OBJ
    escribirOBJ(config, vertices, normales, carasLaterales, tapas, perfil);
}

// Ejecutar programa principal
main();


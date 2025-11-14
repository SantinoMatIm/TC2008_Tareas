/*
 * Santino Matias Im
 * 2025 - 11 - 14
 * Script para dibujar una cara feliz en 2D con transformaciones
 * La cara rota alrededor de un pivote configurable
 *
 * 
 */

'use strict';

import * as twgl from 'twgl-base.js';
import { M3 } from '../2d-lib.js';
import GUI from '../lil-gui.js';

// Definición de los shaders usando GLSL 3.00
const vsGLSL = `#version 300 es
in vec2 a_position;
in vec4 a_color;

uniform vec2 u_resolution;
uniform mat3 u_transforms;

out vec4 v_color;

void main() {
    // Multiplicamos la matriz por el vector extendido con 1 para mantener el tamaño correcto
    vec2 position = (u_transforms * vec3(a_position, 1)).xy;

    // Normalizamos el espacio de pixeles a 0.0 - 1.0
    vec2 zeroToOne = position / u_resolution;

    // Convertimos de 0->1 a 0->2
    vec2 zeroToTwo = zeroToOne * 2.0;

    // Ajuste final de 0->2 a -1->1 (clip space)
    vec2 clipSpace = zeroToTwo - 1.0;

    // Invertimos el eje Y para alinear con WebGL
    gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
    
    v_color = a_color;
}
`;

const fsGLSL = `#version 300 es
precision highp float;

in vec4 v_color;
out vec4 outColor;

void main() {
    outColor = v_color;
}
`;


// Geometría del pivote (pequeña cruz para referencia visual)
function createPivot() {
    const size = 10;
    const thickness = 2;
    
    const positions = [
        // Línea vertical
        -thickness, -size,
        thickness, -size,
        thickness, size,
        -thickness, size,
        
        // Línea horizontal
        -size, -thickness,
        size, -thickness,
        size, thickness,
        -size, thickness
    ];
    
    const colors = [
        // Ambas líneas en rojo para destacar el pivote
        1, 0, 0, 1,
        1, 0, 0, 1,
        1, 0, 0, 1,
        1, 0, 0, 1,
        1, 0, 0, 1,
        1, 0, 0, 1,
        1, 0, 0, 1,
        1, 0, 0, 1
    ];
    
    const indices = [
        0, 1, 2,
        0, 2, 3,
        4, 5, 6,
        4, 6, 7
    ];
    
    return {
        a_position: {
            numComponents: 2,
            data: positions
        },
        a_color: {
            numComponents: 4,
            data: colors
        },
        indices: {
            numComponents: 3,
            data: indices
        }
    };
}


// Geometría de la cara: círculos, arcos y detalles decorativos
function createFace() {
    const positions = [];
    const colors = [];
    const indices = [];
    
    // Contorno de la cara (círculo principal)
    const faceRadius = 85;
    const faceSegments = 60;
    const faceCenter = { x: 0, y: 0 };
    
    const faceStartIndex = 0;
    positions.push(faceCenter.x, faceCenter.y);
    colors.push(1, 0.95, 0.55, 1); // Amarillo cálido
    
    for (let i = 0; i <= faceSegments; i++) {
        const angle = (i / faceSegments) * Math.PI * 2;
        const x = faceCenter.x + Math.cos(angle) * faceRadius;
        const y = faceCenter.y + Math.sin(angle) * faceRadius;
        positions.push(x, y);
        colors.push(1, 0.95, 0.55, 1);
    }
    
    for (let i = 1; i <= faceSegments; i++) {
        indices.push(0, i, i + 1);
    }
    
    // Mejillas rosadas para darle un toque distinto
    const cheekRadius = 12;
    const cheekSegments = 20;
    const cheekOffsetY = 15;
    const cheekColor = [1, 0.7, 0.75, 1];
    
    const addCheek = (centerX) => {
        const start = positions.length / 2;
        positions.push(centerX, cheekOffsetY);
        colors.push(...cheekColor);
        for (let i = 0; i <= cheekSegments; i++) {
            const angle = (i / cheekSegments) * Math.PI * 2;
            const x = centerX + Math.cos(angle) * cheekRadius;
            const y = cheekOffsetY + Math.sin(angle) * cheekRadius;
            positions.push(x, y);
            colors.push(...cheekColor);
        }
        for (let i = 0; i < cheekSegments; i++) {
            indices.push(start, start + i + 1, start + i + 2);
        }
    };
    
    addCheek(-35);
    addCheek(35);
    
    // Ojo izquierdo ligeramente ovalado
    const leftEyeRadius = 9;
    const leftEyeCenter = { x: -22, y: -18 };
    const leftEyeStartIndex = positions.length / 2;
    const eyeSegments = 20;
    
    positions.push(leftEyeCenter.x, leftEyeCenter.y);
    colors.push(0.2, 0.2, 0.25, 1); // Gris oscuro
    
    for (let i = 0; i <= eyeSegments; i++) {
        const angle = (i / eyeSegments) * Math.PI * 2;
        const x = leftEyeCenter.x + Math.cos(angle) * leftEyeRadius;
        const y = leftEyeCenter.y + Math.sin(angle) * (leftEyeRadius * 1.2);
        positions.push(x, y);
        colors.push(0.2, 0.2, 0.25, 1);
    }
    
    for (let i = 0; i < eyeSegments; i++) {
        indices.push(leftEyeStartIndex, leftEyeStartIndex + i + 1, leftEyeStartIndex + i + 2);
    }
    
    // Ojo derecho
    const rightEyeCenter = { x: 22, y: -18 };
    const rightEyeStartIndex = positions.length / 2;
    
    positions.push(rightEyeCenter.x, rightEyeCenter.y);
    colors.push(0.2, 0.2, 0.25, 1);
    
    for (let i = 0; i <= eyeSegments; i++) {
        const angle = (i / eyeSegments) * Math.PI * 2;
        const x = rightEyeCenter.x + Math.cos(angle) * leftEyeRadius;
        const y = rightEyeCenter.y + Math.sin(angle) * (leftEyeRadius * 1.2);
        positions.push(x, y);
        colors.push(0.2, 0.2, 0.25, 1);
    }
    
    for (let i = 0; i < eyeSegments; i++) {
        indices.push(rightEyeStartIndex, rightEyeStartIndex + i + 1, rightEyeStartIndex + i + 2);
    }
    
    // Nariz triangular sencilla
    const noseWidth = 12;
    const noseHeight = 18;
    const noseStartIndex = positions.length / 2;
    const noseTopY = -5;
    positions.push(0, noseTopY);
    positions.push(-noseWidth / 2, noseTopY + noseHeight);
    positions.push(noseWidth / 2, noseTopY + noseHeight);
    colors.push(0.95, 0.7, 0.55, 1, 0.95, 0.7, 0.55, 1, 0.95, 0.7, 0.55, 1);
    indices.push(noseStartIndex, noseStartIndex + 1, noseStartIndex + 2);
    
    // Sonrisa: arco más grueso y desplazado hacia abajo
    const smileRadius = 52;
    const smileSegments = 34;
    const smileThickness = 8;
    const smileStartIndex = positions.length / 2;
    
    for (let i = 0; i <= smileSegments; i++) {
        const t = i / smileSegments;
        const angle = Math.PI * 0.15 + Math.PI * 0.7 * t;
        const x = Math.cos(angle) * smileRadius;
        const y = Math.sin(angle) * smileRadius + 18;
        positions.push(x, y);
        colors.push(0.1, 0.1, 0.1, 1);
    }
    
    for (let i = 0; i <= smileSegments; i++) {
        const t = i / smileSegments;
        const angle = Math.PI * 0.15 + Math.PI * 0.7 * t;
        const x = Math.cos(angle) * (smileRadius - smileThickness);
        const y = Math.sin(angle) * (smileRadius - smileThickness) + 18;
        positions.push(x, y);
        colors.push(0.1, 0.1, 0.1, 1);
    }
    
    for (let i = 0; i < smileSegments; i++) {
        const base = smileStartIndex;
        indices.push(
            base + i, base + i + 1, base + smileSegments + 1 + i,
            base + i + 1, base + smileSegments + 2 + i, base + smileSegments + 1 + i
        );
    }
    
    return {
        a_position: {
            numComponents: 2,
            data: positions
        },
        a_color: {
            numComponents: 4,
            data: colors
        },
        indices: {
            numComponents: 3,
            data: indices
        }
    };
}

// Lógica de renderizado: despejar pantalla, aplicar transformaciones y dibujar
function drawScene(gl, faceVAO, pivotVAO, programInfo, faceBufferInfo, pivotBufferInfo, params) {
    twgl.resizeCanvasToDisplaySize(gl.canvas);

    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);
    gl.clearColor(0.88, 0.9, 0.95, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);

    gl.useProgram(programInfo.program);

    // Pivote con transformación independiente
    let pivotTransform = M3.identity();
    pivotTransform = M3.multiply(M3.translation([params.pivotX, params.pivotY]), pivotTransform);

    const pivotUniforms = {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: pivotTransform
    };

    twgl.setUniforms(programInfo, pivotUniforms);
    gl.bindVertexArray(pivotVAO);
    twgl.drawBufferInfo(gl, pivotBufferInfo);

    // Estrategia: mover la cara alrededor del pivote y aplicar transformaciones locales
    const facePos = [params.faceTranslateX, params.faceTranslateY];
    const pivotPos = [params.pivotX, params.pivotY];
    const angle = params.faceRotation * Math.PI / 180;

    const vx = facePos[0] - pivotPos[0];
    const vy = facePos[1] - pivotPos[1];

    const c = Math.cos(angle);
    const s = Math.sin(angle);
    const rx = vx * c - vy * s;
    const ry = vx * s + vy * c;

    const faceWorldX = pivotPos[0] + rx;
    const faceWorldY = pivotPos[1] + ry;

    let faceTransform = M3.identity();
    faceTransform = M3.multiply(M3.scale([params.faceScaleX, params.faceScaleY]), faceTransform);
    faceTransform = M3.multiply(M3.rotation(angle), faceTransform);
    faceTransform = M3.multiply(M3.translation([faceWorldX, faceWorldY]), faceTransform);

    const faceUniforms = {
        u_resolution: [gl.canvas.width, gl.canvas.height],
        u_transforms: faceTransform
    };

    twgl.setUniforms(programInfo, faceUniforms);
    gl.bindVertexArray(faceVAO);
    twgl.drawBufferInfo(gl, faceBufferInfo);
}


// Configura WebGL, los buffers y la UI con lil-gui
function main() {
    const canvas = document.querySelector('canvas');
    const gl = canvas.getContext('webgl2');

    const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

    // Construimos las geometrías de los objetos
    const faceArrays = createFace();
    const pivotArrays = createPivot();

    // Generamos la información de buffers
    const faceBufferInfo = twgl.createBufferInfoFromArrays(gl, faceArrays);
    const pivotBufferInfo = twgl.createBufferInfoFromArrays(gl, pivotArrays);

    // Creamos VAOs para dibujar más rápidamente
    const faceVAO = twgl.createVAOFromBufferInfo(gl, programInfo, faceBufferInfo);
    const pivotVAO = twgl.createVAOFromBufferInfo(gl, programInfo, pivotBufferInfo);

    // Parámetros controlables
    const params = {
        pivotX: 400,
        pivotY: 300,
        
        faceTranslateX: 500,
        faceTranslateY: 350,
        faceRotation: 0,
        faceScaleX: 1.0,
        faceScaleY: 1.0
    };

    // Interfaz gráfica
    const gui = new GUI();
    
    const pivotFolder = gui.addFolder('Posición del pivote');
    pivotFolder.add(params, 'pivotX', 0, 800).name('Pivote X').onChange(() => render());
    pivotFolder.add(params, 'pivotY', 0, 600).name('Pivote Y').onChange(() => render());
    pivotFolder.open();
    
    const faceFolder = gui.addFolder('Transformaciones de la cara');
    faceFolder.add(params, 'faceTranslateX', 0, 800).name('Posición mundial X').onChange(() => render());
    faceFolder.add(params, 'faceTranslateY', 0, 600).name('Posición mundial Y').onChange(() => render());
    faceFolder.add(params, 'faceRotation', 0, 360).name('Rotación (°)').onChange(() => render());
    faceFolder.add(params, 'faceScaleX', 0.1, 3.0).name('Escala X').onChange(() => render());
    faceFolder.add(params, 'faceScaleY', 0.1, 3.0).name('Escala Y').onChange(() => render());
    faceFolder.open();

    function render() {
        drawScene(gl, faceVAO, pivotVAO, programInfo, faceBufferInfo, pivotBufferInfo, params);
    }

    render();
}

main();
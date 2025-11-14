/*
 * Pequeño envoltorio para cargar TWGL desde un CDN y reutilizarlo localmente.
 * Se exporta tanto el namespace completo como el default para que otros módulos
 * puedan importar con la sintaxis que prefieran.
 */
import * as twgl from 'https://cdn.skypack.dev/twgl.js';

export default twgl;
export * from 'https://cdn.skypack.dev/twgl.js';


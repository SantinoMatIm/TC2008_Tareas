/*
 * Wrapper mínimo para cargar lil-gui desde CDN y exponerlo como módulo local.
 */
import GUI from 'https://cdn.skypack.dev/lil-gui';

export default GUI;
export * from 'https://cdn.skypack.dev/lil-gui';


precision mediump float;
varying float f;
varying vec2 t2;
varying vec3 t3;
varying mat2 m;
void main() { gl_FragColor = vec4(t3 * f, t2.x) + vec4(m[0], m[1]); }

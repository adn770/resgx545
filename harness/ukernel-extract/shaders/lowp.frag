precision lowp float;
varying vec4 col;
uniform vec4 u0;
void main() { gl_FragColor = col * u0 + col; }

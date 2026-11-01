attribute vec4 pos;
uniform vec4 u0;
varying vec4 col;
void main() { gl_Position = pos; col = sin(pos * u0) + normalize(pos); }

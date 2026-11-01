attribute vec4 pos;
uniform int n;
uniform vec4 u0;
varying vec4 col;
void main() { vec4 a = pos; for (int i = 0; i < 32; i++) { if (i >= n) break; a = a * u0 + pos; } gl_Position = pos; col = a; }

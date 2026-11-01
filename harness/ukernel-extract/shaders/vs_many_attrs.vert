attribute vec4 pos;
attribute vec4 a1;
attribute vec4 a2;
attribute vec4 a3;
attribute vec4 a4;
attribute vec4 a5;
attribute vec4 a6;
attribute vec4 a7;
varying vec4 col;
void main() { gl_Position = pos; col = a1 + a2 * a3 + a4 * a5 + a6 * a7; }

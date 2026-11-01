attribute vec4 pos;
attribute vec4 extra;
varying vec4 col;
void main() { gl_Position = pos + extra * 0.0; col = extra; }

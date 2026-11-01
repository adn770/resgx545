attribute vec4 pos;
uniform float uf;
varying vec4 col;
void main() { gl_Position = pos; if (pos.x > uf) col = pos; else col = -pos; }

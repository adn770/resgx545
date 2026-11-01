attribute vec4 pos;
uniform mat4 tm;
varying vec4 col;
void main() { gl_Position = pos; col = tm * vec4(pos.xy * 0.5 + 0.5, 0.0, 1.0); }

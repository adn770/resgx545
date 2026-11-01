attribute vec4 pos;
uniform mat4 mv;
uniform float density;
varying vec4 col;
void main() { vec4 e = mv * pos; gl_Position = pos; col = vec4(exp(-density * length(e.xyz))); }

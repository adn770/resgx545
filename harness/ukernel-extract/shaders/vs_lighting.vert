attribute vec4 pos;
attribute vec3 normal;
uniform mat4 mvp;
uniform mat3 nmat;
uniform vec3 ldir;
uniform vec4 diffuse;
varying vec4 col;
void main() { gl_Position = mvp * pos; vec3 n = normalize(nmat * normal); col = diffuse * max(dot(n, ldir), 0.0); }

attribute vec4 pos;
varying float f;
varying vec2 t2;
varying vec3 t3;
varying mat2 m;
void main() { gl_Position = pos; f = pos.x; t2 = pos.xy; t3 = pos.xyz; m = mat2(pos.x, pos.y, pos.z, pos.w); }

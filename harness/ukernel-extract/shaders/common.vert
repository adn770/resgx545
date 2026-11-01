attribute vec4 pos;
varying vec2 uv;
varying vec4 col;
varying vec3 nrm;
void main() {
    gl_Position = pos;
    uv = pos.xy * 0.5 + 0.5;
    col = pos * 0.5 + 0.5;
    nrm = normalize(vec3(pos.xy, 1.0));
}

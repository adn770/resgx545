+++
id = "Q039"
question = "where is a user clip plane's state held between jobs, what resets it, and when do the vertex's distance dwords decide a plane?"
unit = "mte"
kind = "hw"
value = "medium"
phase = 10
evidence = ["E198", "E280", "E418"]
terms = ["OUTSEL.PLANES"]
+++

fdpc's clip result for plane N outlives the job that set it (E280): after a job whose fdpc puts
every vertex outside plane N, later jobs with the plane enabled and no fdpc are removed until an
fdpc puts the vertices inside again, for planes 0, 1 and 2, in two runs. With the state inside, the
distance dwords o4 and o5 at -1 or +1 remove nothing, for plane 0, plane 1 alone, and planes 0 and
1; no run varies a distance dword under plane 2 with its state inside. So the question of which
dword plane 1 alone reads (E198) had no answer in those terms: plane 1 alone drew in one session and
was removed in another, while its held state differed.

What is open: where the state is held (the MTE, the USE, per vertex or per plane), what resets it
(a fresh boot, a reset after a hang, a job with fdpc on another plane), and why E198 saw o4 at -1
remove plane 0's triangle between two jobs without fdpc.

To settle it: plane 0 with o4 at -1 and +1 right after a GPU reset (a fenced hang), before any
fdpc; then the state set by fdpc and each candidate reset tried in turn, a job reading the plane
after each.

Narrowed in 11.15 (E418, two runs of three sequences): a GPU reset after a hang does not clear plane
0's held result. With the result outside the next jobs without fdpc stayed removed before and after
a hang (2 of 2), with it inside they drew before and after it, the distance dwords at -1 and +1
changing nothing (2 of 2), and an fdpc with the vertices inside cleared the outside result (2 of 2).
After a boot and the day's many resets the first sequence found the result outside. Still open:
where the state is held and what clears it besides an fdpc (a firmware reload, a power cycle), and
planes 1 and 2. Status: narrowed, not answered.

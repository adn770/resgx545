+++
id = "Q022"
question = "why do about 30 percent of the pixels keep the previous case's value in the vertex-colour iteration cases, in both runs?"
unit = "pds"
phase = 7
evidence = ["E133", "E392"]
terms = ["DOUTI0.ATTR_SOURCE", "DOUTI0.SHADEMODEL", "DOUTU1.WAIT_ITER"]
+++

Answered (E392): the stale group does not occur on this stack: in the order 0, 1, 2, 2, 1, 0 three
times every one of the 1062 triangle pixels took its case's vertex colour in each of the 18 jobs,
and no pixel equalled the previous job's.

What is left: what made E133's two runs (an earlier kernel) keep about 300 pixels of the previous
case.

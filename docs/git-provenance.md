# Git Provenance

This release does **not** backfill a fake commit history.

The archived project snapshot used to build this release did not preserve the original incremental `.git` history, so reconstructing “baseline → bug fix → ablation” commits after the fact would be dishonest. The Evidence Layer therefore uses raw experiment outputs, source files, claim contracts, and a research decision log as the provenance available in this artifact.

For a public repository, history should begin from the first real publication/import commit and continue incrementally from there. Recommended future commit boundaries are real actions, not retroactive storytelling:

1. import verified research release
2. add a new external benchmark adapter/run
3. add raw eval output without changing claims
4. diagnose a reproduced failure
5. modify the method in response to that failure
6. add ablation + statistical check
7. update manuscript only after evidence changes

The rule is simple: **never manufacture commits to make the project look older or more iterative than the recorded development actually was.**

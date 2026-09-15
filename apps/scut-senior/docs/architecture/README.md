# SCUT_CSWeaver Architecture Diagram

`scut-csweaver-architecture-en-v2.png` is the English, implementation-aligned
architecture overview as of 13 September 2026. It shows the four-layer system,
the P1 retrieval changes (batched vector encoding, read-only matrix snapshots,
and optional protected RRF), and the P2 in-process runtime boundaries.

The diagram describes current code structure. `protected_rrf_v1` remains an
opt-in ranking strategy; the default ranking remains `lexical_first_v1` until
the planned quality evaluation has evidence to support a default change.

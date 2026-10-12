# Sources: every claim to its public URL

All URLs were checked with unauthenticated requests on 2026-10-12 (HTTP 200; two transient 503s from github.com were re-checked and returned 200). Quotes are verbatim from the source.

## Site-level statements

| Claim | URL |
|---|---|
| Open (Apache-2.0) specification and verifiers; install and run command; 'No unaffiliated party has reproduced it yet'; machine table | https://github.com/Aefinity-AI/cis2-spec/blob/main/README.md |
| Pinned digests | https://github.com/Aefinity-AI/cis2-spec/blob/main/EXPECTED_DIGESTS.md |
| Spec v0.3b | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/CIS2_SPEC_v0.3b.md |
| Conformance vectors dataset | https://huggingface.co/datasets/aefinityAIINC/cis2-conformance |
| Standing challenge, no outside reproduction or divergence reported | https://github.com/Aefinity-AI/cis2-spec/blob/main/HALL-OF-DIVERGENCE.md |
| CIS-2 description on the live site ('AI inference you can check, not just trust', limits, GitHub and Hugging Face profiles) | https://aefinityai.com |
| ALICE: bare-metal BitNet b1.58 engine on UEFI, Microsoft model credit and MIT licence | https://github.com/Aefinity-AI/alice-aegis |
| RANGER: public research notes on low-bit quantisation | https://github.com/Aefinity-AI/ranger |
| Ledger README, ledger, verifier, OpenTimestamps proof file | https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md; https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/LEDGER.tsv; https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/verify_ledger.py; https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/LEDGER.tsv.ots |
| Contribution rules and errata policy | https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md; https://github.com/Aefinity-AI/cis2-spec/blob/main/CHANGELOG.md |
| Mission and aspiration text | Our own statement; not a factual claim, no source. |

## Per-lab claims

### 1. CIS-2: the same AI output, bit for bit, on different machines (`cis2-cross-machine-digest`)

| Claim | Verbatim quote | URL |
|---|---|---|
| A free Lightning AI cloud Studio (Xeon Platinum 8488C, CPU not owned by us) matched all four pinned digests using the narrower scripts/self_check.sh, not the 9-check selfcheck.sh. Driven by the maintainer. | `**Result: PASS — all four digests match the pinned test vector.**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-25-LIGHTNING-STUDIO-SELFCHECK.md |
| The README's documented expected selfcheck.sh output (shown with an i5-5200U fingerprint, the box1 AVX2 row) ends in 9 passed, 0 failed. This is shown as expected output; the machine table separately lists box1 with its log not published. | `== SUMMARY: 9 passed, 0 failed ==` | https://github.com/Aefinity-AI/cis2-spec/blob/main/README.md |
| The aarch64 Android phone reproduced the pinned digests through a different code path; the self-check script itself was not run on it. | ``selfcheck.sh` not run on the device; the pinned §13.1 digests were reproduced on it through the KV-cache `verify3/` path` | https://github.com/Aefinity-AI/cis2-spec/blob/main/README.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/README.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/EXPECTED_DIGESTS.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/CIS2_SPEC_v0.3b.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-25-LIGHTNING-STUDIO-SELFCHECK.md, https://huggingface.co/datasets/aefinityAIINC/cis2-conformance

### 2. An NVIDIA GPU reproduces the CPU reference digest (Tesla P100) (`gpu-p100-reproduces-cpu`)

| Claim | Verbatim quote | URL |
|---|---|---|
| All four vectors matched the CPU digests on the GPU. Only the 16-token sequential vector is the normative v0.3b vector; the other three are informative, and the two tree-order vectors belong to a v0.4 candidate that is not normative. | `**Status: PASS. Run of 2026-09-08 12:07 UTC, NVIDIA Tesla P100-PCIE-16GB (sm_60, Pascal), CUDA 12.8.**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/GPU_RESULT.md |
| Two earlier GPU runs were false positives (the binary was really built for the CPU) and are withdrawn. | `Earlier attempts v6 and v7 were **false positives** and are withdrawn` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/GPU_RESULT.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/GPU_RESULT.md, https://huggingface.co/datasets/aefinityAIINC/cis2-conformance/blob/main/GPU_RESULT.md

### 3. Batching and precision on a Tesla T4: which shortcuts change the digest (`t4-batching-precision`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Row-batched fp32 matched the batch-1 reference exactly at every batch size, on host and GPU. | `fp32-seq matched the batch=1 reference exactly at batch sizes 1, 4, and 8 (0/576 diffs each), on both the host build and the T4 CUDA build.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-19-GPU-BATCHED-FP32-DETERMINISM.md |
| Grouped fp32 and int8 changed the result at every batch size tested, as the report predicted before the run (455/576 and 576/576 differing elements respectively). | `fp32-grouped and int8 mismatched at every batch size tested (455/576 and 576/576 diffs respectively)` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-19-GPU-BATCHED-FP32-DETERMINISM.md |
| Host and CUDA builds agreed on all 10 configurations. | `Host and CUDA builds produced bit-identical digests for every one of the 10` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-19-GPU-BATCHED-FP32-DETERMINISM.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-19-GPU-BATCHED-FP32-DETERMINISM.md

### 4. Clean-room reimplementations: one mismatch (from a memo), one match (from spec v0.1), one partial that exposed a spec error (`cleanroom-reimplementations`)

| Claim | Verbatim quote | URL |
|---|---|---|
| First Rust attempt (E15e, built from a design memo, not the spec) did not match: inv_freq digest and the full witness digest differed. The token ids and argmax digest matched. | `## Verdict: MISMATCH, but an informative one` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15e_CLEANROOM_RESULT.md |
| Second Rust attempt (E15g, spec v0.1 only) matched all four digests and all 16 token ids on x86_64 and aarch64 on its first CI run. The CI run is private. | `**Status: MATCH. Full bit-for-bit conformance on first CI run, no fixes needed.**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15g_CLEANROOM_V2_RESULT.md |
| The E15g implementer read only the v0.1 spec text for algorithm content. It also read build and CI scaffolding files, which are logged. | `implemented reading **only**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15g_CLEANROOM_V2_RESULT.md |
| C11 attempt (E15j, spec v0.2) matched 3 of 4 digests on all four cells (x86_64 and aarch64, gcc and clang). Only the witness digest CIS2_REF differed. The 16 token ids matched. | `Result: PARTIAL conformance — 3 of 4 digests match bit-for-bit, cross-ISA/cross-compiler-identical` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15j_CLEANROOM_C_RESULT.md |
| The cause was the order of the five items in the witness chain, not the forward pass. Per-tensor digests (about 124 per run, decode steps 0 and 1 only) matched. | `root cause found — witness-chain item ORDER, not the forward pass` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15k_DIVERGENCE_LOCALIZATION.md |
| The C code had copied the item order from the spec's written prose, which disagreed with the reference. This is classed as a spec defect. | `copied verbatim from `docs/CIS2_SPEC_v0.2.md` §12.1's written prose` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15k_DIVERGENCE_LOCALIZATION.md |
| After we corrected the spec and the C code, all four C cells reproduced the pinned CIS2_REF. We corrected the spec ourselves after seeing the mismatch, so this is a post-fix match. | `E15j is now a full 4/4-digest, cross-language (Rust vs from-spec-text-only C11), cross-ISA (x86_64/aarch64), cross-compiler (gcc/clang) conformance PASS` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15k_DIVERGENCE_LOCALIZATION.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15e_CLEANROOM_RESULT.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15g_CLEANROOM_V2_RESULT.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15j_CLEANROOM_C_RESULT.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15k_DIVERGENCE_LOCALIZATION.md

### 5. Sin/cos accuracy for RoPE against a pre-registered 2 ULP bar (v0.2, v0.3, v0.3b) (`sincos-prereg-2ulp`)

| Claim | Verbatim quote | URL |
|---|---|---|
| The pre-registration was written before implementation. | `**Status: pre-registered before implementation.**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_PREREG.md |
| v0.2 (f32-only reduction, Taylor polynomial) had errors up to 115198 ULP for sin and up to 163969 ULP for cos, in the local oracle run. | `\| v0.2 (f32-only reduce, Taylor) \| up to 115198 \| 1.30e-2 \| up to 163969 \| 1.36e-2 \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_RESULT.md |
| v0.3 (f64-staged reduction only) cut the error by roughly 55 to 70 times, with a max of 2813.5 raw ULP, and still missed the 2 ULP bar. The doc attributes the residual to the unchanged Taylor polynomial. | `"<=2 ULP" bar is NOT met` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_RESULT.md |
| v0.3b (octant reduction plus separate minimax polynomials) reached a maximum of 1.5 ULP for sin and cos on both models and met the bar, in the local harness run. | `\| **v0.3b (octant reduce, minimax)** \| **1.5** \| **1.2e-7** \| **1.5** \| **1.2e-7** \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_RESULT.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_RESULT.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_PREREG.md

### 6. One flipped bit in the weights: which checks notice? (`bitflip-weights`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Experiment 2 (295 trials): of 247 trials where the output changed, the text-replay column (A) missed 182. In the source's Experiment 2 definitions, A is 'inference ran to completion without erroring'. | `\| text/argmax replay (A) \| 182 / 247 \| [0.679, 0.788] \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md |
| Experiment 2: the top-k / receipt-style check (B) missed 82 of the same 247. In Experiment 2 B means the receipt verifier accepted the run, not top-5 replay. | `\| top-k / receipt-style check (B) \| 82 / 247 \| [0.276, 0.393] \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md |
| The witness digest row is 0 of 247. The document says this is exact by construction, since a digest miss and a C-fail are the same event. | `\| CIS witness digest (C) \| 0 / 247 \| [0.000, 0.015] \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md |
| Experiment 1 (50 trials): text replay passed 3 corruptions that the digest caught (trials 16, 25, 47). Top-5 replay also failed on all 3, so its miss count was 0 at this sample size. | `\| A pass AND C fail (text replay misses a corruption the digest catches) \| 3 \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md |
| Null result: 43 flips (37 of 70 SCALE_FFN and 6 of 35 TRIT_FFN trials) left the witness digest identical to the clean baseline. The digest by design stays silent on these, and a byte-level check would flag them. | `A byte-level integrity check would flag these 43 cases; the CIS digest, by design, does not, because it attests to computation, not storage.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md |
| The write-up corrected its own original report after the independent recount: trial 47 was a bit-7 flip from the random set, not one of the 5 dedicated high-bit control trials. | `Correction from the independent recount: the original report used trial 47 as "the" high-bit example;` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md, https://github.com/Aefinity-AI/alice-aegis/commit/14ef1a1, https://github.com/Aefinity-AI/alice-aegis/commit/1567ee1

### 7. Realistic edits to the embedding table, including one hidden row (`embedding-edits`)

| Claim | Verbatim quote | URL |
|---|---|---|
| For a single edited embedding row that none of the test prompts read (8 random rows x 5 prompts = 40 trials), text replay and the top-5 check each detected 0 of 40; the witness digest detected 40 of 40. | `When the row is not exercised by the test prompts, A and B miss it completely (0/40 each in (b')).` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md |
| Control with 8 rows the prompts do read (40 trials): the top-5 check detected 21 of 40 (52.5%, Wilson 37.5-67.1%); text replay detected 11 of 40 (27.5%). Even when rows are read, detection is only partial. | `\| B (top-5 logit-index check) \| 21/40 \| 52.5% \| 37.5–67.1% \| 0/40 (0.0%) \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md |
| 1% magnitude pruning of the whole table (20 prompts): text replay detected 18 of 20 (90.0%, Wilson 69.9-97.2%); the top-5 check and witness digest detected 20 of 20. | `\| A (text replay) \| 18/20 \| 90.0% \| 69.9–97.2% \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md |
| In the classes that were run, the witness digest detected every trial. Here 'detected' means the digest differs from baseline; the document reports no false-positive test for it. | `The witness digest (C) is the only detector of the three that caught every trial in every class tested here` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md |
| UNABLE: substituting a different same-shape checkpoint was found infeasible and not run (no independently trained checkpoint with matching shape was available). | `### (c) Different same-shape checkpoint — found infeasible` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md

### 8. Receipt-verified agent evaluation, and the hole we found in our own verifier (`receipt-verified-eval`)

| Claim | Verbatim quote | URL |
|---|---|---|
| All 60 receipts verified. | `\| Receipt verification \| 60/60 PASS \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md |
| Task score on receipt-verified outputs. | `\| Score (receipt-verified outputs, arg_match AND output_match) \| 45/60 \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md |
| v1 caught 3 of 4 tampers; after context binding, v2 caught all 4. | `Overall: v1 = 57/60 PASS, **3/4 tampers caught**. v2 = 56/60 PASS, **4/4 tampers caught**.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md |
| The v1 miss: a valid receipt filed under another item's name (lookup_hit_01) verified like a genuine one. | `**PASS (not caught)**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md, https://github.com/Aefinity-AI/alice-aegis/commit/13ed3c47ae5a

### 9. Ordinary logging versus replay-based receipts on one-field edits (`logging-vs-receipts`)

| Claim | Verbatim quote | URL |
|---|---|---|
| A changed internal token id (one id, step 0) was invisible in the ordinary display, but replay named the step and the field. | `(verifier line: step 0 divergence: toks-match=false tool-match=true in-match=true out-match=true decode-chain-match=true)` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/RECEIPT-VS-LOGGING.md |
| An altered tool output ('20' changed to '21') was rejected at step 0 by replay. In the ordinary display this change was visible as printed text, but nothing in the log format flagged it as wrong. | `(verifier line: step 0 divergence: toks-match=true tool-match=true in-match=true out-match=false decode-chain-match=true)` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/RECEIPT-VS-LOGGING.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/RECEIPT-VS-LOGGING.md

### 10. What receipts cost on a real agent episode (`receipt-overhead`)

| Claim | Verbatim quote | URL |
|---|---|---|
| On box1, the 3-step episode with receipts took 44.74 s wall-clock. A plain single-pass 72-token decode of the same prompt took 17.84 s (2.51x). The receipt is 1,599 bytes. Local verification took 40.08 s and passed. The source calls 2.51x an upper bound on receipt cost, not a clean measurement of the receipt code, because the episode loop also re-prefills at every step and the plain decode does not. | `\| box1 (aefinity-box) \| 44.74s wall (`agent_trace gen`, K=3 N=24) \| 17.84s wall (`cis_decode`, N=72, same prompt) \| 1599 bytes \| 40.08s wall, PASS (local, direct) \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md |
| On box2, the daemon returned ALLOW (PASS) about 12 min 13 s after submission. This figure is bounded by polling at 20 s intervals and is not a precise wall-clock time. An earlier run of the same scenario shape through the same daemon took about 7.5 min. | `~12m13s submit-to-ALLOW` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md |
| On box1, a separate 2026-09-23 re-run of the same command (45.94 s elapsed) had a peak resident set size of 1,309,996 KB. Its energy was 369.45 J, measured on the CPU package only (RAPL package-0), over a window of about 46 s. The source says to read this as a lower bound on whole-system energy. | `\| box1 (aefinity-box) \| 1,309,996 KB \| 369.45 J (RAPL package-0 only, ~46s window) \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md |
| The box2 timing was not controlled for other queue activity. The daemon serializes all verify work through one worker, so the source reports the two box2 timings as observed rather than as a single figure. | `no attempt was made to control for other daemon-queue activity` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md

### 11. Continuous validation: does a one-byte corruption get caught, and what hides it? (`continuous-validation`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Two baseline runs matched. | `**Phase 1 result: PASS** — two hand-started runs, about 6.5 minutes apart on one host, produced matching digests (n=2, same host, same day).` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md |
| A one-byte weight change was stopped by the sha256 hash pin in the verifier before the forward pass ran. | `CIS2_VERIFY3 FATAL: model.safetensors sha256 mismatch,` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md |
| Negative finding: the self-check's fetch step detects the mismatch but re-downloads the pinned weights, so the monitor (which wraps the self-check) would likely log PASS and mask the corruption. This was inferred from the earlier self-check run on the corrupted file; the monitor itself was not run on corrupted weights. | `repairs corrupted weights silently and would likely log PASS, masking the corruption in monitor mode` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md |
| The monitor's FAIL path was never exercised. | `The monitor script was not run against corrupted weights, so its FAIL path was not exercised in this experiment.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md |
| A flaw in our own monitor script was disclosed: the logged 'digest_hint' was really a test-binary name suffix (script since changed to parse the witness digest line, or print unknown). | `is not a model or output digest. It is the suffix of the cargo test binary name` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md

### 12. Training checkpoints across CPUs and instruction sets (`training-checkpoints-cross-isa`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Default PyTorch: the printed losses were identical, but every checkpoint hash differed between the two CPUs from step 50. Same-machine reruns matched on each host. The source calls the cause (different vectorized kernel path) 'consistent with', not demonstrated. | `**MISMATCH.** The four printed loss scalars are bit-identical (same Python `repr()` at every checkpoint on both hosts), but all four checkpoint sha256 digests differ, starting at the first recorded checkpoint (step 50).` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-24-CROSS-ISA-TRAINING-RECEIPT.md |
| Pinned PyTorch (kernel dispatch and thread count pinned) gave byte-identical checkpoints on the same two x86_64 machines; the source says this is not a cross-ISA result. | `**MATCH — cross-machine, not cross-ISA.**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-24-CROSS-ISA-TRAINING-RECEIPT.md |
| The fixed-order C trainer gave identical checkpoint hashes on all five hosts, including one aarch64 phone; a second clean build on one x86_64 host and the phone reproduced the same digests. | `All four checkpoint sha256 digests are identical across all five hosts: three x86_64 machines without AVX2, one x86_64 machine with AVX2/FMA, and one aarch64 machine — a cross-ISA result.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-24-CROSS-ISA-TRAINING-RECEIPT.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-24-CROSS-ISA-TRAINING-RECEIPT.md

### 13. E22: which spec rules does the test vector actually exercise? (`e22-necessity-matrix`)

| Claim | Verbatim quote | URL |
|---|---|---|
| 12 of 16 mutations moved the digest, 3 did not, 1 was declared skipped (M07, skipped by the leg). | `**12 of 16 mutations moved the digest. 3 did not. 1 was declared skipped.**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md |
| The argmax tie-break rule (M15, section 11) is not exercised by this vector because no tie occurs in any of its 16 argmaxes over a 49152-wide fp32 logit vector. The source says the clause is correct and necessary in general and that the vector never reaches the branch. | `**M15** \| **§11 argmax tie-break** \| **SAME** \| **not exercised**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md |
| Correction by the authors: the M16 row (attention scale via pinned rsqrt) was a vacuous mutation, because it substituted the function for its own body, so it tested nothing. The first published explanation (head_dim = 64 is a perfect square) was withdrawn as a rationalisation. | `**VACUOUS MUTATION — see correction below**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md |
| A rule that can be broken without effect on the digest is untested by this vector, not redundant. This is a statement about the conformance suite, not the spec. | `A clause that can be broken with no observable effect is not thereby redundant` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md |
| Unmutated builds reproduced the baseline digest at four optimisation levels (O0, O1, O3, Os). Scope is this compiler on this host only. | `-O0 / -O1 / -O3 / -Os   →  d82743059d…  SAME` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md

### 14. E24: the spec never says which Unicode version defines a letter (`e24-unicode-gap`)

| Claim | Verbatim quote | URL |
|---|---|---|
| The LETTER table grew by 622 codepoints between Unicode 15.0.0 and 15.1.0 (CJK Unified Ideographs Extension I). The NUMBER and WHITESPACE tables did not change. | `\| LETTER \| `\p{L}`, `char::is_alphabetic` \| 136,104 cp \| 136,726 cp \| **+622: U+2EBF0..U+2EE5D** \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E24_UNICODE_VERSION_GAP.md |
| Spec v0.3b names no Unicode version for the pre-tokenizer's property classes. | `Neither the clause nor any other part of the document names a Unicode version.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E24_UNICODE_VERSION_GAP.md |
| Bounded: this is a finding, not a reproduction failure, and no published digest moves. | `**Status:** finding, bounded. Not a reproduction failure. No published digest moves.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E24_UNICODE_VERSION_GAP.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E24_UNICODE_VERSION_GAP.md

### 15. E25: the RMSNorm multiply order matters, and our spec sentence saying otherwise was false (`e25-rmsnorm-order`)

| Claim | Verbatim quote | URL |
|---|---|---|
| The spec's earlier claim that no divergence had been observed was wrong. | `That sentence is false as of 2026-09-09.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md |
| 34.60% of RMSNorm elements in one 16-token decode differ between the two orders (SmolLM2-135M). | `231,014 of 667,584 RMSNorm elements — 34.60% — distinguish the two orders in a single 16-token decode.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md |
| The alternate order moved the witness digest. | `CENSUS witness_digest_moved=true` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md |
| In the same run, the generated tokens did not change (for this 16-token vector only). | `CENSUS argmax_digest_moved=false` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/CHANGELOG.md

### 16. E26: sin/cos at very long contexts — the sampled answer was wrong (`e26-trig-range`)

| Claim | Verbatim quote | URL |
|---|---|---|
| The first, sampled answer was wrong. | `The first answer was wrong, and the way it was wrong is the point` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md |
| The sample never landed on the hard cases. | `4096 samples out of 8,388,608 per binade simply never landed near a zero of` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md |
| Exhaustive sweep below 2^16, measured in ULP of the result: sin 66, cos 2283 (large near zeros of sin and cos). The sampled sweep had reported at most 1 ULP (one 2-ULP cos) over [2^0, 2^16). Over the full [0, 2^20) sweep the ULP maxima are sin 2283, cos 2617. | `TRIG-X EXHAUSTIVE \|x\|<2^16 max\|ulp\| sin=66 (at 4.4767695e3)  cos=2283 (at 5.2516434e4)` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md |
| The full sweep covered 1,233,125,376 arguments. | `Every f32 in `[0, 2^20)` — **1,233,125,376 arguments**, subnormals included:` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md |
| Measured as absolute error, the worst case over [0, 2^20) is 9.4218e-8, which is 0.790 ULP-of-unity. | `over the entire range is **0.790 ULP-of-unity**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md

### 17. E27: exp, ln and SiLU on every float32 input, and a defect in our spec (`e27-exp-ln-range`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Every one of the 3,257,925,634 arguments where both the pinned exp and the oracle are finite is within one ULP (max relative error 1.1921e-7 = 2^-23), measured against a float64 oracle. | `Every one of the 3,257,925,634 arguments for which both `exp_pinned` and the oracle are finite is within **one ULP**.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E27_EXP_LN_RANGE.md |
| Defect in our own spec: the high guard (x > 88.0 returns +Infinity) clips 94,743 arguments (0x42B00001 to 0x42B17217) whose true exp is finite and representable in f32. Behaviour is pinned as normative and unchanged; an erratum was filed. | `§6.2's high guard clips 94,743 values below the representable range` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E27_EXP_LN_RANGE.md |
| exp and ln were monotone over the whole finite domain (zero violations), an oracle-free check. | `exp monotone: violations=0` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E27_EXP_LN_RANGE.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E27_EXP_LN_RANGE.md

### 18. E28, E36, E37: every internal activation compared against an independent implementation (`layer-oracle-e28-e36-e37`)

| Claim | Verbatim quote | URL |
|---|---|---|
| E28: 13,452 intermediate tensors (one prompt, 19 positions, two models: SmolLM2-135M and Qwen2.5-0.5B) compared; worst relative L2 disagreement 9.9e-5, on one tensor of one model (Qwen). This is a single-prompt maximum, not a bound for the model. | `Worst disagreement: **9.9e-5** relative` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E28_LAYER_ORACLE.md |
| E36 corrected our own published worst case: over six SmolLM2-135M prompt cells (80,565 tensors) the worst was 3.406e-05, 1.53 times the 2.228e-05 E28 published from its single SmolLM2 prompt. | `worst case is **3.406e-05**, 1.53x the` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E36_ORACLE_PROMPT_SWEEP.md |
| E37: six Qwen2.5-0.5B cells add 64,260 tensors; with E36 that is 144,825 tensors across two architectures. On Qwen, E28's 9.923e-05 turned out to be the six-cell maximum (rel_rms rose to 2.883e-03); the earlier layer-ratio bounds were per-prompt and were corrected (erratum E-9). | `Taken with E36 this is 144,825 tensors across two` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E37_QWEN_ORACLE_SWEEP.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E28_LAYER_ORACLE.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E36_ORACLE_PROMPT_SWEEP.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E37_QWEN_ORACLE_SWEEP.md

### 19. E29: does the compiler's optimiser change the bits? (`e29-optimizer-invariance`)

| Claim | Verbatim quote | URL |
|---|---|---|
| On the x86_64 builds tested, the optimiser vectorised the code (hundreds of AVX2 instructions) and the dumped intermediates did not change. | `turns out to be **no**: the optimizer may vectorize, and does, and the bits do not move.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E29_OPTIMIZER_INVARIANCE.md |
| Ten distinct x86_64 binaries (opt-level 0,1,2,3,s x generic/native) on SmolLM2-135M produced one identical 51,750,154-byte dump, with zero FMA instructions. | `**Ten distinct binaries. One dump.**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E29_OPTIMIZER_INVARIANCE.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E29_OPTIMIZER_INVARIANCE.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E39_FTZ_IS_NOT_WHERE_WE_SAID.md

### 20. E35 to E40: does the flush-to-zero rule ever matter? (after two wrong explanations) (`ftz-reach-e35-e40`)

| Claim | Verbatim quote | URL |
|---|---|---|
| E35: zero of 21,248,280 exp evaluations reached the band it studied (a band later shown not to be where the flush rule acts). | `Zero of 21,248,280 `exp_pinned` evaluations across six prompts` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E35_DENORMAL_REACH.md |
| E38's wider sweep found 2 arguments in that band on one long decode (Qwen2.5-0.5B, 256 tokens); the digest did not move. | `with **2** of that cell's 22,626,240 arguments inside` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E35_DENORMAL_REACH.md |
| E39: the mechanism we had given in four places was wrong; the conclusions survive, the reason did not. | `the mechanism claim in E29, E35, E38 and erratum E-10 is wrong` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E39_FTZ_IS_NOT_WHERE_WE_SAID.md |
| The claim that a denormal arises in a real decode was withdrawn. | `is **withdrawn**.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/CHANGELOG.md |
| E40 classified 562,531,070,920 intermediates across both pinned checkpoints; none was subnormal. | `**562,531,070,920** classified` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E40_MATVEC_RMSNORM_REACH.md |
| No weight operand in either model is subnormal. | `**0 of 628,547,776 weight operands across both §0 models are subnormal**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E40_MATVEC_RMSNORM_REACH.md |
| Conclusion: on the normative vector the rule does not affect the digest. | `On the normative vector, §1.3's FTZ/DAZ is not digest-relevant.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E40_MATVEC_RMSNORM_REACH.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E35_DENORMAL_REACH.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E38_REACH_SWEEP.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E39_FTZ_IS_NOT_WHERE_WE_SAID.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E40_MATVEC_RMSNORM_REACH.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/CHANGELOG.md

### 21. E41: the spec pins how text becomes tokens, but not how tokens become text (`e41-detokenization-gap`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Two conforming implementations can disagree on a receipt's text. | `two conforming implementations can disagree about what a receipt says while agreeing on every digest in it.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md |
| 313 of SmolLM2's 49,152 vocabulary entries are not valid UTF-8 on their own. | `**313** of SmolLM2's 49,152 vocab entries are not valid UTF-8 alone (0.64 %)` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md |
| 271 of Qwen's 151,936 output indices map to no string in the tokenizer files. | `**271** of Qwen's 151,936 logit indices are in neither `model.vocab` nor `added_tokens`` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md |
| All 17 of SmolLM2's special tokens decode to text that re-encodes to different ids, so a rendered control token cannot be told from text spelling it. | `**17** of 17 SmolLM2 `added_tokens` decode to text that re-encodes to *different* ids` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md

### 22. ev-1: a 160-item mini evaluation on the pinned 135M model (`ev1-mini-eval`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Truthfulness: 3 of 60 passed (0.05), by verbatim-substring heuristic. | `\| `truthfulness` \| 60 \| 3 \| 0.05 \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md |
| Refusal probes: 10 of 20 passed (0.5). The source says this sits at chance and was not broken out further. | `\| `refusal` \| 20 \| 10 \| 0.5 \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md |
| Tool-use proxy (arithmetic completion, not tool-call format): 5 of 60 passed. | `\| `tool_use` \| 60 \| 5 \| 0.0833... \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md |
| Self-consistency: 20 of 20 items produced identical run1/run2 digests within the same process on one host. A separate cross-process rerun log exists. No second-host verify was run. | `\| `self_consistency` \| 20 \| 20 \| 1.0 \|` | https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md |
| The committed summary.json matches the four category numbers above. | `"truthfulness": {       "n_items": 60,       "n_pass": 3,` | https://github.com/Aefinity-AI/cis2-spec/blob/main/eval/results/summary.json |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/eval/results/summary.json

### 23. Our test standard and the public experiment ledger (`test-standard-ledger`)

| Claim | Verbatim quote | URL |
|---|---|---|
| The ledger covers 84 registered experiments, 65 with a verdict; 161 of 233 lines are backfill. | `At the time of this export the ledger holds 233 lines. They cover 84 registered experiments, and 65 of them have a verdict line. 161 of the 233 lines are marked backfill.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md |
| The ledger states what it cannot prove. | `It cannot show when an experiment ran. A lab could run an experiment in private, look at the result, and then publish a pass mark.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md |
| The start rule is a promise the page itself cannot check. | `That rule is a promise. This page cannot check it.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md |
| Provenance on every number, or the number is removed. | `A number with no provenance gets removed rather than trusted.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md |
| Pinned digests do not move silently. | `The rule is that goldens do not move silently: if an erratum changes a pinned digest, the change, the cause and the new value all land in the same commit as the version bump.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md |
| No unqualified superlatives. | `**No unqualified superlatives.**` | https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md |
| A mismatch is a result. | `Open the PR whether your digests match or not. A mismatch is a result.` | https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/LEDGER.tsv, https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/verify_ledger.py, https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/CHANGELOG.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_PREREG.md

### 24. Open challenge: the Hall of Divergence (`hall-of-divergence`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Every listed reproduction is our own run (two internal rows, 2026-09-22, own machines: Intel i5-5200U with AVX2 and Intel Celeron N4020 scalar, each 9 passed / 0 failed). No third-party reproduction is listed. | `The two rows above are internal Aefinity AI runs, not third-party reproductions` | https://github.com/Aefinity-AI/cis2-spec/blob/main/HALL-OF-DIVERGENCE.md |
| No divergence has been reported as of this check (2026-10-12). | `*No divergence reported yet.*` | https://github.com/Aefinity-AI/cis2-spec/blob/main/HALL-OF-DIVERGENCE.md |

Other public pages for this lab: https://github.com/Aefinity-AI/cis2-spec/blob/main/HALL-OF-DIVERGENCE.md, https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md

### 25. RANGER mock run: low-bit quantization ideas tested on synthetic tensors (`ranger-mock-run`)

| Claim | Verbatim quote | URL |
|---|---|---|
| On synthetic tensors, bits saved per width doubling came out at -0.60 against a predicted -0.50 (the file labels this a pass; it came only after the author rebuilt a first test that was not computing the target). | `**−0.60 bits per 2× width** (predicted −0.50)` | https://github.com/Aefinity-AI/ranger/blob/main/research/experiments/RESULTS.md |
| Falsified sub-hypothesis: on synthetic tensors, rotation helps at 4-bit (1.23x) but is slightly worse than plain per-token quantization at 3- and 2-bit (0.92x). | `wins at **W4A4 (1.23×)** but is slightly *worse* than plain per-token quant at W3A3 and W2A2 (0.92×)` | https://github.com/Aefinity-AI/ranger/blob/main/research/experiments/RESULTS.md |
| In the first combined test, rotation smeared the super-weights, so protecting the top rotated weights in sparse form failed. The fix was to split them off before rotating. | `rotation delocalizes the super-weights` | https://github.com/Aefinity-AI/ranger/blob/main/research/experiments/RESULTS.md |

Other public pages for this lab: https://github.com/Aefinity-AI/ranger/blob/main/research/experiments/RESULTS.md

### 26. RANGER Phase 1: the quantization ideas on real models (SmolLM2-135M, Qwen3-0.6B) (`ranger-phase1`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Our earlier E7 null result was retracted as an artifact of how it was built; nothing about super-weight protection can be concluded from E7. | `E7's null result was an artifact by construction — retract it.` | https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md |
| On SmolLM2-135M (fp32), 4-bit per-token activation quantization collapses perplexity from 16.14 to 13,773; a folded rotation sandwich recovers 92.3% of the log-PPL collapse, leaving PPL at 27.11 (still above the 16.14 baseline). On Qwen3-0.6B the recovery was 92.5% (34.23 to 146,845 collapse). Fake-quant is an upper bound on deployable A4. | `A4 per-token quantization collapses PPL 16.14 → 13,773; a per-linear folded rotation sandwich recovers **92.3%** of the log-PPL collapse (→ 27.11)` | https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md |
| Refuted: the 'skip the rotation' upgrade. Static exemption of 8 census channels recovered only 59.1% at 135M (25% with activation-measured channels at 0.6B; the census-derived set did nothing on Qwen) versus 92%+ for rotation. | `Pillar 1's "skip the rotation" upgrade is refuted` | https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md |
| Null at 135M: no super-weight lever over an honest g=128 4-bit baseline, and MSE clipping hurts there (24.896 to 26.917). The 'rescues 0.38 of clip damage' sub-result was refuted as noise on a disjoint slice (-0.015). At 0.6B, clipping helps (48.06 to 41.82) and the coordinate increment is small but real (+0.45, then +0.24). | `At 135M there is no exploitable super-weight lever over an honest W4 baseline — and MSE-clipping actively hurts.` | https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md |
| Across models, the overlap between the weight census and activation-outlier channels fell from 6/10 (SmolLM2-135M) to 2/10 (Qwen3-0.6B); the census still found the single top channel on both. | `Census→activation overlap collapses: 6/10 → 2/10.` | https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md |

Other public pages for this lab: https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md

### 27. Retraction: our benchmark laptop was running at about one fifth speed (`retraction-prochot`)

| Claim | Verbatim quote | URL |
|---|---|---|
| The CPU was clamped to ratio 5 of a requested 27, with PROCHOT asserted while the thermal sensor read cool. | `was clamped to core ratio 5 out of a requested 27.` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md |
| Every earlier number from that box (before 2026-07-29) was taken at roughly a fifth of nominal clock, and was retracted. | `Every performance number we took on that box before 2026-07-29 was measured on a CPU` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md |
| After the fix, cur_ratio went from 5 to 25 on 3 of 3 cold boots (one machine). | `Reproduced on 3/3 cold boots.` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md |
| Wall-time ratio across the two same-day builds was 3.861x, below the 5.000x the ratio change implies; output was byte-identical. Not reported as a speedup. | `We are deliberately **not** reporting this as a speedup.` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md |
| Published as a retraction. | `this post is a retraction, not a speedup` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md |
| Limitation of the before/after: no clear-only arm. | `No clear-only arm.` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md |

Other public pages for this lab: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md

### 28. A compiler setting silently deleted our vector instructions (`soft-float-avx2`)

| Claim | Verbatim quote | URL |
|---|---|---|
| Hand-written AVX2 kernels compiled to zero vector instructions; the binary ran 217 to 258 times slower than the hard-float rebuild (soft-float 1.65-1.67e9 vs hard-float 6.48-7.59e6 ticks/token). | `Our hand-written AVX2 kernels compiled to zero vector instructions, and the resulting binary ran 217–258× slower than it should have.` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_uefi-soft-float-deletes-your-avx2.md |
| Instruction census of the shipped (preserved, bit-identical) soft-float binary: no xmm, ymm or vfmadd instructions. | `census: xmm=0 ymm=0 vfmadd=0` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_uefi-soft-float-deletes-your-avx2.md |

Other public pages for this lab: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_uefi-soft-float-deletes-your-avx2.md

### 29. What does an operating system cost? A pre-registered result we held back (`os-cost-held-back`)

> Site note (2026-10-12): this lab is shown as **Held back**. Under our pre-registered rule no numbers or result direction from this comparison are published until the mechanism is understood.

### 30. The '16% slower' lookup-table kernel claim, retracted (`lut-kernel-retraction`)

| Claim | Verbatim quote | URL |
|---|---|---|
| The earlier '16% slower' claim does not reproduce: the pshufb arm was bimodal (8.2 vs ~11.2 GMAC/s effective, a 36% swing) while the f32 arm moved only 4.7%. In the faster mode pshufb was 1.19-1.21x faster than the f32 matvec kernel; in run 1 it lost at 1.09x, so the ordering flips between runs. | `"16% SLOWER" is NOT REPRODUCIBLE.` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/hardware_logs/lut_mpgemm_ab_findings_2026-07-30.md |
| The decision to reject the kernel still stands, on different grounds. The memory-traffic ratio is derived arithmetic (1.670x per token), not a measurement. The derivation uses prior-log figures to reach a projected ~28% slower decode in the bandwidth-bound regime. | `The rejection verdict STANDS, on memory-traffic grounds, not kernel throughput.` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/hardware_logs/lut_mpgemm_ab_findings_2026-07-30.md |

Other public pages for this lab: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/hardware_logs/lut_mpgemm_ab_findings_2026-07-30.md

### 31. Audit of our own removed code: benchmark lines that measured nothing (`fabricated-metrics-audit`)

| Claim | Verbatim quote | URL |
|---|---|---|
| The printed benchmark lines in the removed crate were fixed string literals, not measurements. | `All are `println!` calls with **no format arguments** — string literals asserting measurements that were never taken.` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/EVIDENCE_fabricated_metrics.md |

Other public pages for this lab: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/EVIDENCE_fabricated_metrics.md

### 32. E-S1: how far can a ternary 2B model be compressed without loss? (`es1-trit-census`)

| Claim | Verbatim quote | URL |
|---|---|---|
| The best of the lossless coders tested (zstd -19 on packed bytes) reached 1.532 bits per weight, 399,113,010 bytes, against 2.000 bits per weight for the engine's current packing. | `\| **zstd -19 on packed bytes** \| **1.532** \| **399,113,010** \|` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/experiments/ES1_TRIT_CENSUS_RESULTS.md |
| The round trip was byte-exact on every tensor, with 0 mismatches. | `Byte-exact round-trip on every tensor: **0 mismatches**.` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/experiments/ES1_TRIT_CENSUS_RESULTS.md |
| The trits are near-uniform, so the weights compress only a little. | `Pretrained ternary weights do not compress much` | https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/experiments/ES1_TRIT_CENSUS_RESULTS.md |

Other public pages for this lab: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/experiments/ES1_TRIT_CENSUS_RESULTS.md

### 33. Claims from the literature that failed when we ran them (`refuted-literature-claims`)

| Claim | Verbatim quote | URL |
|---|---|---|
| A stock Hugging Face transformers recipe (AutoBitLinear, online_quant=False) for training soft prompts on the Falcon-E checkpoint gave outputs wrong by about 300 times on one real layer (layer-0 q_proj), as measured by us on our target box. | `so the stock recipe's outputs are wrong by weight_scale^2 (~301.9x measured on real layer-0 q_proj)` | https://github.com/Aefinity-AI/alice-aegis/blob/main/program/model-lab/refuted_claims.md |
| The claim that stock onebitllms runs on a free Kaggle/Colab T4 in 2-5 hours is marked REFUTED in our notes. The basis is a documented hardware requirement (Triton >=3.3 needs compute capability 8.0+, and the T4 is sm_75). We did not run it on a T4. The notes say the path may survive only in an unverified older-library environment. | `Triton >=3.3 (bundled with torch >=2.7) requires NVIDIA CC 8.0+ and dropped Turing` | https://github.com/Aefinity-AI/alice-aegis/blob/main/program/model-lab/refuted_claims.md |

Other public pages for this lab: https://github.com/Aefinity-AI/alice-aegis/blob/main/program/model-lab/refuted_claims.md


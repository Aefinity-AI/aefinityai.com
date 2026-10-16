# Aefinity AI: site copy

Generated 2026-10-12 from public sources only. Every result below is quoted from a page reachable without authentication; see SOURCES.md. Every result was run by us, with no unaffiliated reproduction.

## Mission

We are not another AI platform or cloud service. We take the hard questions AI raises about the future of humanity, and we study, experiment and test as rigorously as we can. Our aim is for humankind to reap the benefits of AI: building toward a brighter future, separating evidence from myth and hype, and staying grounded in the work of finding the AI solutions the world still needs.

**Aspiration.** We hope to earn trust as a conformance-program operator that leads by example: honest about every result, and every result repeatable. This is an aspiration, not a claim.

## How to read this site

- Every result is **run by us**. No unaffiliated party has reproduced any of it yet.
- Every number comes with its public source and a short verbatim quote.
- Failures, nulls, retractions and corrections of our own work are listed with the successes.
- Outcome labels are ours: **positive** = Positive (the check worked as expected, within the stated scope); **mixed** = Mixed (some parts held, some did not, or we corrected ourselves); **negative** = Negative (the claim or approach failed, or we retracted it); **null** = Null (no effect found, or nothing yet to report); **held** = Held back (a pre-registered rule withholds the result until its cause is understood).
- Most labs use small open models (SmolLM2-135M, Qwen2.5-0.5B, a pruned BitNet-2B) on a few machines we own. Read each lab's scope before drawing conclusions.

## The hard questions

### 1. Can two different computers produce the exact same AI output, bit for bit?

Labs: [CIS-2: the same AI output, bit for bit, on different machines](#lab-cis2-cross-machine-digest); [E29: does the compiler's optimiser change the bits?](#lab-e29-optimizer-invariance); [Training checkpoints across CPUs and instruction sets](#lab-training-checkpoints-cross-isa)

**What we found so far.** In our own runs, yes, for one narrow case: fp32 greedy decoding of one small model (SmolLM2-135M, 16 tokens), once the arithmetic is pinned in a written specification. The same digest came out on AVX2 and scalar x86 machines, an aarch64 phone and a free cloud CPU. Ten differently optimised x86_64 builds produced one identical dump. For training, default PyTorch gave different checkpoints on two CPUs even though the printed losses were identical, while a fixed-order C trainer gave identical checkpoints on five hosts including a phone, at toy scale (13,088 parameters).

**Still open.** Whether anyone outside our lab gets the same result; larger models; production precisions such as bf16; sampling, batching and quantisation. We have not tested those.

### 2. Does the same hold on graphics cards and under the usual speed shortcuts?

Labs: [An NVIDIA GPU reproduces the CPU reference digest (Tesla P100)](#lab-gpu-p100-reproduces-cpu); [Batching and precision on a Tesla T4: which shortcuts change the digest](#lab-t4-batching-precision)

**What we found so far.** On one Tesla P100, an independent CUDA implementation matched the CPU digests, after two earlier GPU runs turned out to be false positives (the binary had really been built for the CPU) and were withdrawn. On a Tesla T4, one matrix multiply gave identical results with row-batched fp32 at batch sizes 1, 4 and 8, while grouped fp32 and int8 changed the result at every batch size, as predicted before the run.

**Still open.** Other GPU generations, tensor cores, whole-model batching beyond row-batched fp32, multi-GPU serving, and performance. The CUDA code is not public.

### 3. If someone changes a model's weights without telling you, how would you know?

Labs: [One flipped bit in the weights: which checks notice?](#lab-bitflip-weights); [Realistic edits to the embedding table, including one hidden row](#lab-embedding-edits); [Continuous validation: does a one-byte corruption get caught, and what hides it?](#lab-continuous-validation)

**What we found so far.** Re-reading the output is a weak detector. In one run of 295 bit-flip trials, among the 247 where the output changed, a replay-style column missed 182 and a receipt-style check missed 82. An edited embedding row that no test prompt read was missed 40 of 40 times by text replay and by a top-5 check, while a check over the full computation caught all 40. A one-byte file corruption was stopped by a hash gate, but our own self-check would likely have repaired the file and hidden the corruption from a monitor. Also, 43 flips changed nothing in the computation, which a computation-level check by design does not flag.

**Still open.** Adversaries who optimise their tampering; other prompts, models and tensors; a scheduled, multi-host monitoring deployment.

### 4. Can you trust a record of what an AI agent did, and what does it cost?

Labs: [Receipt-verified agent evaluation, and the hole we found in our own verifier](#lab-receipt-verified-eval); [Ordinary logging versus replay-based receipts on one-field edits](#lab-logging-vs-receipts); [What receipts cost on a real agent episode](#lab-receipt-overhead)

**What we found so far.** A receipt that is replayed against pinned artifacts can catch edits an ordinary log display does not flag. Trying to break our own verifier found a hole: a genuine receipt filed under the wrong test item verified like a real one. Binding each receipt to its item closed that case. Receipts are not free: on one old laptop the episode with receipts took 2.51 times as long as a plain decode (the source calls that an upper bound), and verification took 40 seconds there and minutes on a weaker machine.

**Still open.** Whether the fix holds against tampering that was not hand-picked; cost on other hardware and at scale.

### 5. Can someone who has never seen our code rebuild the same bits from the written description alone?

Labs: [Clean-room reimplementations: one mismatch (from a memo), one match (from spec v0.1), one partial that exposed a spec error](#lab-cleanroom-reimplementations); [E24: the spec never says which Unicode version defines a letter](#lab-e24-unicode-gap); [E41: the spec pins how text becomes tokens, but not how tokens become text](#lab-e41-detokenization-gap)

**What we found so far.** Partly. A Rust version written from an internal memo did not match. A Rust version written from spec v0.1 matched all digests on its first CI run. A C version written from spec v0.2 matched three of four digests, and the mismatch led us to a defect in our own spec: the written order of the witness chain disagreed with the reference. We then found two more gaps by reading our spec critically: it names no Unicode version for letters, and it pins text to tokens but not tokens to text.

**Still open.** Independent humans doing the same; every one of these implementers was an AI coding agent run by one operator inside our organisation.

### 6. How do we know our own tests test anything?

Labs: [E22: which spec rules does the test vector actually exercise?](#lab-e22-necessity-matrix); [E26: sin/cos at very long contexts — the sampled answer was wrong](#lab-e26-trig-range); [E27: exp, ln and SiLU on every float32 input, and a defect in our spec](#lab-e27-exp-ln-range); [E28, E36, E37: every internal activation compared against an independent implementation](#lab-layer-oracle-e28-e36-e37); [E35 to E40: does the flush-to-zero rule ever matter? (after two wrong explanations)](#lab-ftz-reach-e35-e40); [Sin/cos accuracy for RoPE against a pre-registered 2 ULP bar (v0.2, v0.3, v0.3b)](#lab-sincos-prereg-2ulp); [E25: the RMSNorm multiply order matters, and our spec sentence saying otherwise was false](#lab-e25-rmsnorm-order)

**What we found so far.** We broke our spec's rules one at a time: the official test noticed 12 of 16 breaks, and not the tie-break or the denormal-flush pin. Sampled accuracy checks gave comfortable wrong answers (at most 1 ULP) where exhaustive sweeps found much larger ULP errors near zeros of sin and cos. Exhaustive testing of exp found a real defect in a safety guard in our spec. A pre-registered 2 ULP bar was missed by our first fix and met by a second. We also retracted two wrong explanations of why the flush-to-zero rule never mattered.

**Still open.** Whether the test vector exercises every rule; the untriggered rules are protected only by separate self-tests.

### 7. How can an outsider tell that a lab did not tune results after the fact, or quietly drop failures?

Labs: [Our test standard and the public experiment ledger](#lab-test-standard-ledger); [Open challenge: the Hall of Divergence](#lab-hall-of-divergence)

**What we found so far.** They cannot tell completely, and our own ledger page says so. We publish pass marks before runs, a hash-chained public ledger of the private register, numbered errata and a rule that mismatches count as results. The ledger cannot show when an experiment ran. As of 2026-10-12 nobody outside the lab has reproduced or broken our results, and the public Hall of Divergence says so plainly.

**Still open.** An outside audit of whether our practice always matched our statement.

### 8. Do speed numbers survive scrutiny?

Labs: [Retraction: our benchmark laptop was running at about one fifth speed](#lab-retraction-prochot); [A compiler setting silently deleted our vector instructions](#lab-soft-float-avx2); [What does an operating system cost? A pre-registered result we held back](#lab-os-cost-held-back); [The '16% slower' lookup-table kernel claim, retracted](#lab-lut-kernel-retraction); [Audit of our own removed code: benchmark lines that measured nothing](#lab-fabricated-metrics-audit)

**What we found so far.** Ours did not, at first. Our benchmark laptop was clamped to about a fifth of its clock, so every earlier number from it was retracted. A compiler setting removed all vector instructions and the binary ran 217 to 258 times slower. A pre-registered comparison of a no-OS build against a minimal Linux was held back after a surprising first result; we found one contributing cause in our own build (soft-float), and the question remains open. A '16% slower' claim copied from a source comment did not reproduce. An early version of our software printed benchmark lines that were fixed strings.

**Still open.** A clean, controlled speed comparison across machines. We make no general speed claim; the speed figures on this site are single measurements on named machines.

### 9. Do published tricks for shrinking AI models actually work?

Labs: [RANGER mock run: low-bit quantization ideas tested on synthetic tensors](#lab-ranger-mock-run); [RANGER Phase 1: the quantization ideas on real models (SmolLM2-135M, Qwen3-0.6B)](#lab-ranger-phase1); [E-S1: how far can a ternary 2B model be compressed without loss?](#lab-es1-trit-census); [Claims from the literature that failed when we ran them](#lab-refuted-literature-claims)

**What we found so far.** Some, within narrow limits. On two real small models, a rotation recovered 92.3% and 92.5% of the 4-bit activation collapse, though perplexity stayed above the baseline. A shortcut that skips the rotation was refuted, a super-weight lever was null at 135M parameters, and one of our own earlier null results was retracted. Lossless coding of a ternary 2B model reached 1.532 bits per weight, about 4% below ideal packing. A stock soft-prompt recipe gave outputs wrong by about 300 times on one layer when we ran it.

**Still open.** Models above about 0.6B parameters, quantisation-aware training, and deployable int4 kernels.

### 10. Can a tiny model be evaluated in a way anyone can repeat exactly, and what does it score?

Labs: [ev-1: a 160-item mini evaluation on the pinned 135M model](#lab-ev1-mini-eval)

**What we found so far.** The 160-item evaluation repeated exactly on one machine (20 of 20 self-consistency items). The model scored poorly, which was expected from a 135M base model with simple heuristics: 3 of 60 on truthfulness, 5 of 60 on a tool-use proxy and 10 of 20 on refusal probes, which the source says is chance. The point was repeatability, not accuracy.

**Still open.** Cross-host verification of the evaluation, and anything about larger or instruction-tuned models.

## Open questions we have not tested yet

No results here. These are questions our own limits sections point at. Nothing below has been measured.

- **Does bit-exact reproduction survive production serving?** The spec covers fp32 greedy decoding on small open models, mostly CPU. bf16 and GPU serving, sampling, batching and larger models are outside it today. We have not tested them.
- **Do receipt checks hold against someone who optimises the tampering?** Our tampering tests used hand-picked and harness-chosen edits. We have not tested an adversary who knows the verifier.
- **Will anyone outside our lab reproduce the results, or break them?** Not yet known. No unaffiliated reproduction is recorded. The Hall of Divergence is the standing invitation.
- **Does reproducible output say anything about whether an answer is correct, safe or fair?** We have not tested this. Reproducibility shows that two machines computed the same thing, not that the thing is good.
- **Which other rules in the spec does the test vector never exercise?** We tested 16 single-rule mutations. We have not mapped the rest.

## The labs

| # | Lab | Date | Outcome |
|---|---|---|---|
| 1 | [CIS-2: the same AI output, bit for bit, on different machines](#lab-cis2-cross-machine-digest) | 2026-09-25 | positive |
| 2 | [An NVIDIA GPU reproduces the CPU reference digest (Tesla P100)](#lab-gpu-p100-reproduces-cpu) | 2026-09-08 | positive |
| 3 | [Batching and precision on a Tesla T4: which shortcuts change the digest](#lab-t4-batching-precision) | 2026-09-19 | positive |
| 4 | [Clean-room reimplementations: one mismatch (from a memo), one match (from spec v0.1), one partial that exposed a spec error](#lab-cleanroom-reimplementations) | 2026-08-28 | mixed |
| 5 | [Sin/cos accuracy for RoPE against a pre-registered 2 ULP bar (v0.2, v0.3, v0.3b)](#lab-sincos-prereg-2ulp) | 2026-08-29 | mixed |
| 6 | [One flipped bit in the weights: which checks notice?](#lab-bitflip-weights) | 2026-09-13 | positive |
| 7 | [Realistic edits to the embedding table, including one hidden row](#lab-embedding-edits) | 2026-09-17 | positive |
| 8 | [Receipt-verified agent evaluation, and the hole we found in our own verifier](#lab-receipt-verified-eval) | 2026-09-13 | mixed |
| 9 | [Ordinary logging versus replay-based receipts on one-field edits](#lab-logging-vs-receipts) | 2026-09-22 | positive |
| 10 | [What receipts cost on a real agent episode](#lab-receipt-overhead) | 2026-09-22 | mixed |
| 11 | [Continuous validation: does a one-byte corruption get caught, and what hides it?](#lab-continuous-validation) | 2026-09-27 | mixed |
| 12 | [Training checkpoints across CPUs and instruction sets](#lab-training-checkpoints-cross-isa) | 2026-09-24 | mixed |
| 13 | [E22: which spec rules does the test vector actually exercise?](#lab-e22-necessity-matrix) | 2026-09-09 | mixed |
| 14 | [E24: the spec never says which Unicode version defines a letter](#lab-e24-unicode-gap) | 2026-09-09 | mixed |
| 15 | [E25: the RMSNorm multiply order matters, and our spec sentence saying otherwise was false](#lab-e25-rmsnorm-order) | 2026-09-09 | positive |
| 16 | [E26: sin/cos at very long contexts — the sampled answer was wrong](#lab-e26-trig-range) | 2026-09-09 | mixed |
| 17 | [E27: exp, ln and SiLU on every float32 input, and a defect in our spec](#lab-e27-exp-ln-range) | 2026-09-09 | mixed |
| 18 | [E28, E36, E37: every internal activation compared against an independent implementation](#lab-layer-oracle-e28-e36-e37) | 2026-09-09 | positive |
| 19 | [E29: does the compiler's optimiser change the bits?](#lab-e29-optimizer-invariance) | undated in source | positive |
| 20 | [E35 to E40: does the flush-to-zero rule ever matter? (after two wrong explanations)](#lab-ftz-reach-e35-e40) | 2026-09-09 | null |
| 21 | [E41: the spec pins how text becomes tokens, but not how tokens become text](#lab-e41-detokenization-gap) | 2026-09-10 | negative |
| 22 | [ev-1: a 160-item mini evaluation on the pinned 135M model](#lab-ev1-mini-eval) | 2026-09-23 | mixed |
| 23 | [Our test standard and the public experiment ledger](#lab-test-standard-ledger) | 2026-10-12 | mixed |
| 24 | [Open challenge: the Hall of Divergence](#lab-hall-of-divergence) | 2026-09-22 | null |
| 25 | [RANGER mock run: low-bit quantization ideas tested on synthetic tensors](#lab-ranger-mock-run) | 2026-07-14 | mixed |
| 26 | [RANGER Phase 1: the quantization ideas on real models (SmolLM2-135M, Qwen3-0.6B)](#lab-ranger-phase1) | undated in source | mixed |
| 27 | [Retraction: our benchmark laptop was running at about one fifth speed](#lab-retraction-prochot) | 2026-08-05 | negative |
| 28 | [A compiler setting silently deleted our vector instructions](#lab-soft-float-avx2) | 2026-08-05 | negative |
| 29 | [What does an operating system cost? A pre-registered result we held back](#lab-os-cost-held-back) | 2026-08-01 | held |
| 30 | [The '16% slower' lookup-table kernel claim, retracted](#lab-lut-kernel-retraction) | 2026-07-30 | negative |
| 31 | [Audit of our own removed code: benchmark lines that measured nothing](#lab-fabricated-metrics-audit) | 2026-07-10 | negative |
| 32 | [E-S1: how far can a ternary 2B model be compressed without loss?](#lab-es1-trit-census) | 2026-09-04 | null |
| 33 | [Claims from the literature that failed when we ran them](#lab-refuted-literature-claims) | undated in source | negative |

<a id="lab-cis2-cross-machine-digest"></a>

### CIS-2: the same AI output, bit for bit, on different machines

*Date: 2026-09-25 | Outcome: Positive (the check worked as expected, within the stated scope) | Run by us; no unaffiliated reproduction.*

**Question.** Can two different computers produce the exact same AI output, bit for bit, from a written specification?

**Why it matters.** If an AI's output can differ depending on which computer ran it, nobody can audit a result by re-running it. A written specification that makes the bits identical would turn 'trust us' into 'run it yourself'.

**Method, step by step.**

1. Write the arithmetic down: the order in which numbers are added, no fused multiply-add, how tiny numbers are flushed, the sin/cos polynomials and the position table.
2. Pick one pinned test: the SmolLM2-135M model, the prompt 'Once upon a time', 16 greedy tokens, fp32.
3. Hash the full output scores (the logits) into a SHA-256 chain. That digest is the receipt.
4. Run the self-check on different machines and compare the digests with the pinned ones in EXPECTED_DIGESTS.md.

**Method as recorded.** Spec v0.3b pins the arithmetic (reduction order, no FMA, FTZ/DAZ, pinned polynomials, RoPE table); a SHA-256 witness chain over the full logits is the receipt. Public conformance vectors on Hugging Face. Pinned vector: SmolLM2-135M, prompt 'Once upon a time', 16 greedy tokens, fp32. The 9-check selfcheck.sh was run by the maintainer on own x86_64 machines (AVX2 and scalar; README machine table). On a free Lightning AI Studio (Xeon Platinum 8488C, 4 vCPU, AVX-512 flags, gcc 13.3.0, Ubuntu 24.04) only the narrower scripts/self_check.sh (four digests) was run, not selfcheck.sh. An aarch64 Android phone reproduced the pinned digests through the KV-cache verify3 path, not the self-check script. Run by us.

**Results (exact, sourced).**

- A free Lightning AI cloud Studio (Xeon Platinum 8488C, CPU not owned by us) matched all four pinned digests using the narrower scripts/self_check.sh, not the 9-check selfcheck.sh. Driven by the maintainer.
  - Source quote: `**Result: PASS — all four digests match the pinned test vector.**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-25-LIGHTNING-STUDIO-SELFCHECK.md
- The README's documented expected selfcheck.sh output (shown with an i5-5200U fingerprint, the box1 AVX2 row) ends in 9 passed, 0 failed. This is shown as expected output; the machine table separately lists box1 with its log not published.
  - Source quote: `== SUMMARY: 9 passed, 0 failed ==`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/README.md
- The aarch64 Android phone reproduced the pinned digests through a different code path; the self-check script itself was not run on it.
  - Source quote: ``selfcheck.sh` not run on the device; the pinned §13.1 digests were reproduced on it through the KV-cache `verify3/` path`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/README.md

**What it does NOT show.** That the model is right, safe or fair; that anything outside fp32 greedy decoding on one small model reproduces; or that an outside party gets the same result.

**Scope and caveats, as recorded.**

- Run by us on every machine, including the cloud workspace; the README says: No unaffiliated party has reproduced it yet.
- One model (SmolLM2-135M), one prompt, 16 tokens, fp32 greedy decoding only (no sampling, batching or quantization), mostly CPU; production bf16/GPU serving is outside the spec today.
- Full logs for most machine-table rows are published as 'log not published'.
- The Lightning run used scripts/self_check.sh (four digests), not the 9-check selfcheck.sh; the 9-passed line is the README's expected-output block (i5-5200U fingerprint), not a separately published log.
- The Lightning Studio is a free tier workspace, not a rented one; no timing numbers reported.
- One machine-table host (penguin) had weights copied over the LAN because its resolver could not reach the Hugging Face CDN; the pinned sha256 of all three artifacts was still verified.
- Shows the bits reproduce; says nothing about whether the model is correct, safe or fair.
- Conformance-suite internals are not public; only the vectors and spec are.

**Outcome.** Positive (the check worked as expected, within the stated scope).

**What we learned.** With the arithmetic pinned in writing, one fp32 digest reproduced across AVX2 and scalar x86, an aarch64 phone and an AVX-512-capable cloud CPU (generic build, self-check only), in our own runs. Until an outsider runs it, the claim stays 'reproduced by us'.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/README.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/EXPECTED_DIGESTS.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/CIS2_SPEC_v0.3b.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-25-LIGHTNING-STUDIO-SELFCHECK.md
- https://huggingface.co/datasets/aefinityAIINC/cis2-conformance

Reproduce the headline check with the command the repository README gives:

```
git clone https://github.com/Aefinity-AI/cis2-spec && cd cis2-spec && ./selfcheck.sh
```

The README also lists a narrower local script, `scripts/self_check.sh`, run after the same `git clone`. The README says it needs a Rust toolchain (`cargo`) and network access to download the pinned SmolLM2-135M weights.

<a id="lab-gpu-p100-reproduces-cpu"></a>

### An NVIDIA GPU reproduces the CPU reference digest (Tesla P100)

*Date: 2026-09-08 | Outcome: Positive (the check worked as expected, within the stated scope) | Run by us; no unaffiliated reproduction.*

**Question.** Does the same AI output come out bit for bit on a graphics card, not just on other CPUs?

**Why it matters.** Most AI runs on graphics cards. A reproducibility claim that only holds on CPUs would not cover where the work is done.

**Method, step by step.**

1. Write an independent CUDA implementation of the same spec.
2. Run the four test vectors on a Kaggle Tesla P100 with the internet disabled.
3. Compare the GPU digests with the CPU digests.
4. Check, by sampling GPU occupancy and inspecting the compiled code, that the work really ran on the GPU.

**Method as recorded.** An independent CUDA implementation of spec v0.3b on a Kaggle Tesla P100 (sm_60, CUDA 12.8, internet disabled), SmolLM2-135M, four vectors (16 and 128 tokens, sequential and a candidate tree order). Run by us. The CUDA source and run recipe are not published.

**Results (exact, sourced).**

- All four vectors matched the CPU digests on the GPU. Only the 16-token sequential vector is the normative v0.3b vector; the other three are informative, and the two tree-order vectors belong to a v0.4 candidate that is not normative.
  - Source quote: `**Status: PASS. Run of 2026-09-08 12:07 UTC, NVIDIA Tesla P100-PCIE-16GB (sm_60, Pascal), CUDA 12.8.**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/GPU_RESULT.md
- Two earlier GPU runs were false positives (the binary was really built for the CPU) and are withdrawn.
  - Source quote: `Earlier attempts v6 and v7 were **false positives** and are withdrawn`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/GPU_RESULT.md

**What it does NOT show.** Anything about speed, newer GPU generations, tensor cores, batching or multiple GPUs; and the CUDA source is not public, so outsiders cannot rerun our port.

**Scope and caveats, as recorded.**

- One GPU generation (Pascal), one driver and compiler, one model (SmolLM2-135M), one prompt, horizon up to 128 tokens.
- Correctness only: no performance or timing claim; no tensor-core, batched, multi-stream or multi-GPU paths; nothing about Ampere, Hopper or Blackwell.
- The CUDA port is not published, so outsiders cannot rerun it from the repo. The source says anyone can write their own CUDA implementation from the spec and compare against the published digest.
- Do not cite the withdrawn v6 or v7 runs; the claim rests only on the corrected v8 run. An earlier v5 run (2026-09-06) matched the same digests but did not establish device execution, and v8 closed that gap.
- Only the 16-token sequential vector is normative; the other three are informative and the tree order is a v0.4 candidate, not part of v0.3b.
- Device execution evidence is occupancy sampling (nvidia-smi, 10 and 11 samples) plus SASS inspection, not a performance measurement.
- Run by us; no unaffiliated reproduction.

**Outcome.** Positive (the check worked as expected, within the stated scope).

**What we learned.** Our own early GPU runs passed for the wrong reason. A re-run caught it, and the claim now rests only on the corrected run.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/GPU_RESULT.md
- https://huggingface.co/datasets/aefinityAIINC/cis2-conformance/blob/main/GPU_RESULT.md

Read the result page (links above). Our CUDA source is not published. The source says anyone can write their own CUDA implementation from the public spec and compare it against the published digest.

<a id="lab-t4-batching-precision"></a>

### Batching and precision on a Tesla T4: which shortcuts change the digest

*Date: 2026-09-19 | Outcome: Positive (the check worked as expected, within the stated scope) | Run by us; no unaffiliated reproduction.*

**Question.** Do common GPU speed shortcuts, like batching requests or switching to int8, quietly change the answer?

**Why it matters.** Batching requests and lower precision are the usual ways to make serving cheaper. If they silently change answers, a receipt must be able to tell.

**Method, step by step.**

1. Take one matrix multiply from the reference model (layer 0, q_proj).
2. Compute it on a Tesla T4 and on a CPU build in three ways: row-batched fp32, grouped fp32 and int8, at batch sizes 1, 4 and 8.
3. Count how many of the 576 output values differ from the batch-1 CPU result.
4. Compare host and GPU digests for all 10 configurations.

**Method as recorded.** One matmul (q_proj, layer 0, hidden size 576) of the reference model on a Kaggle Tesla T4 (sm_75) and a host CPU build (g++; CUDA build via nvcc for sm_75): row-batched fp32, grouped fp32 and int8 at batch sizes 1, 4 and 8, plus a batch-1 host control (10 configurations). Diffs are counted over 576 output elements against the batch-1 CPU reference. Run by us; driver source and recipe not published. No timing figures are reported.

**Results (exact, sourced).**

- Row-batched fp32 matched the batch-1 reference exactly at every batch size, on host and GPU.
  - Source quote: `fp32-seq matched the batch=1 reference exactly at batch sizes 1, 4, and 8 (0/576 diffs each), on both the host build and the T4 CUDA build.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-19-GPU-BATCHED-FP32-DETERMINISM.md
- Grouped fp32 and int8 changed the result at every batch size tested, as the report predicted before the run (455/576 and 576/576 differing elements respectively).
  - Source quote: `fp32-grouped and int8 mismatched at every batch size tested (455/576 and 576/576 diffs respectively)`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-19-GPU-BATCHED-FP32-DETERMINISM.md
- Host and CUDA builds agreed on all 10 configurations.
  - Source quote: `Host and CUDA builds produced bit-identical digests for every one of the 10`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-19-GPU-BATCHED-FP32-DETERMINISM.md

**What it does NOT show.** Behaviour of a whole model, other GPUs, or whether grouped or int8 could be made to match.

**Scope and caveats, as recorded.**

- Single matmul (q_proj, layer 0), not a full forward pass; the whole-model follow-on covers only row-batched fp32 and is in an internal log, not a public report.
- One GPU architecture (Tesla T4, sm_75); no claim about other GPUs or compute capabilities.
- Whether grouped or int8 could be made to match was not attempted; those mismatches were the expected outcome.
- Driver source and Kaggle recipe not published, so the sweep cannot be re-run from public material.
- The published sweep table lists host-build digests; the CUDA digests are reported as byte-identical to them, not tabulated separately.
- Run by us; no unaffiliated reproduction.

**Outcome.** Positive (the check worked as expected, within the stated scope).

**What we learned.** In our fp32 test, the pinned order of operations decided the digest. The same order matched on CPU and GPU, and a different order broke it, which is what a digest is supposed to detect. This is one matmul on one GPU type, so it shows the check works there, not that it holds everywhere.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-19-GPU-BATCHED-FP32-DETERMINISM.md

Read the result page. The driver source and Kaggle recipe are not published, so the sweep cannot be re-run from public material.

<a id="lab-cleanroom-reimplementations"></a>

### Clean-room reimplementations: one mismatch (from a memo), one match (from spec v0.1), one partial that exposed a spec error

*Date: 2026-08-28 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** Can someone who has never seen our code build the same bits from the written description alone?

**Why it matters.** A specification is only useful if someone who never saw the original code can build the same thing from it.

**Method, step by step.**

1. Give isolated AI coding agents the written material only, never the reference source.
2. Attempt 1 (Rust) worked from an internal memo; attempt 2 (Rust) from spec v0.1; attempt 3 (C11) from spec v0.2.
3. Compare their four digests and 16 token ids with the reference on x86_64 and aarch64, with gcc and clang.
4. When the C version missed one digest, dump a hash per tensor from both and find where they first differ.

**Method as recorded.** Isolated AI coding agents run by one operator wrote verifiers without opening the reference source. E15e (Rust) worked from an internal design memo plus two result docs, not the spec. E15g (Rust) worked from spec v0.1 only. E15j (C11) worked from spec v0.2 plus the E15d digests doc, on x86_64 and aarch64 with gcc and clang. E15k localised the C mismatch by dumping a SHA-256 digest per tensor for both implementations, then inspected the witness-chain code. Run by us. Every cited CI run is private. All four pages are public and return 200.

**Results (exact, sourced).**

- First Rust attempt (E15e, built from a design memo, not the spec) did not match: inv_freq digest and the full witness digest differed. The token ids and argmax digest matched.
  - Source quote: `## Verdict: MISMATCH, but an informative one`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15e_CLEANROOM_RESULT.md
- Second Rust attempt (E15g, spec v0.1 only) matched all four digests and all 16 token ids on x86_64 and aarch64 on its first CI run. The CI run is private.
  - Source quote: `**Status: MATCH. Full bit-for-bit conformance on first CI run, no fixes needed.**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15g_CLEANROOM_V2_RESULT.md
- The E15g implementer read only the v0.1 spec text for algorithm content. It also read build and CI scaffolding files, which are logged.
  - Source quote: `implemented reading **only**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15g_CLEANROOM_V2_RESULT.md
- C11 attempt (E15j, spec v0.2) matched 3 of 4 digests on all four cells (x86_64 and aarch64, gcc and clang). Only the witness digest CIS2_REF differed. The 16 token ids matched.
  - Source quote: `Result: PARTIAL conformance — 3 of 4 digests match bit-for-bit, cross-ISA/cross-compiler-identical`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15j_CLEANROOM_C_RESULT.md
- The cause was the order of the five items in the witness chain, not the forward pass. Per-tensor digests (about 124 per run, decode steps 0 and 1 only) matched.
  - Source quote: `root cause found — witness-chain item ORDER, not the forward pass`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15k_DIVERGENCE_LOCALIZATION.md
- The C code had copied the item order from the spec's written prose, which disagreed with the reference. This is classed as a spec defect.
  - Source quote: `copied verbatim from `docs/CIS2_SPEC_v0.2.md` §12.1's written prose`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15k_DIVERGENCE_LOCALIZATION.md
- After we corrected the spec and the C code, all four C cells reproduced the pinned CIS2_REF. We corrected the spec ourselves after seeing the mismatch, so this is a post-fix match.
  - Source quote: `E15j is now a full 4/4-digest, cross-language (Rust vs from-spec-text-only C11), cross-ISA (x86_64/aarch64), cross-compiler (gcc/clang) conformance PASS`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15k_DIVERGENCE_LOCALIZATION.md

**What it does NOT show.** That independent humans can do it; the implementers were AI agents run by one operator inside our organisation. The cited CI runs are private.

**Scope and caveats, as recorded.**

- Implementers were AI coding agents run by one operator inside our organisation, not independent humans. No unaffiliated reproduction.
- E15e was built from an internal design memo and result docs, not the published spec, so it is not a spec-text-only test.
- E15j also read the E15d digests doc, so it was not strictly spec-text-only. E15g read build and CI scaffolding files, logged as not algorithmic.
- The C match in E15k came only after we fixed the spec and the C code. The spec-as-written produced only a partial match.
- Targets were spec v0.1 and v0.2, since superseded by v0.3b.
- All cited CI runs are private and cannot be checked externally. The result docs are our own historical development notes.
- Model was SmolLM2-135M, fp32, one prompt (4 prompt tokens, 16 generated tokens). Sample size is one prompt per attempt.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** The failures taught more than the match. The C attempt showed that the spec's own prose on witness-chain order contradicted the reference. A spec-only implementer reproduced it faithfully, and the mismatch exposed the defect. Fixing the spec led to a full C match.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15e_CLEANROOM_RESULT.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15g_CLEANROOM_V2_RESULT.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15j_CLEANROOM_C_RESULT.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15k_DIVERGENCE_LOCALIZATION.md

Read the four result pages (links above). The CI runs they cite are private and cannot be checked externally.

<a id="lab-sincos-prereg-2ulp"></a>

### Sin/cos accuracy for RoPE against a pre-registered 2 ULP bar (v0.2, v0.3, v0.3b)

*Date: 2026-08-29 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** Is the pinned sin/cos accurate enough for long contexts, measured against a bar we set before we tested?

**Why it matters.** Rotary position encoding feeds sin and cos with large angles at long context. If the pinned functions are inaccurate there, the spec pins a bad answer exactly.

**Method, step by step.**

1. Write the pass mark down first: within 2 ULP of the correctly rounded f32 value.
2. Build a 60-digit-precision reference (mpmath) for the angles up to position 8192 on two models.
3. Score three versions: the original, a version with a higher-precision reduction only, and a version with octant reduction plus new polynomials.
4. Report each against the bar.

**Method as recorded.** A pre-registration set a 2 ULP bar (oracle within 2 ULP of correctly-rounded f32) before the v0.3 fix was implemented. An mpmath 60-digit oracle covered RoPE angles for positions up to max_position_embeddings=8192, using the SmolLM2-135M (theta=1e5) and Qwen2.5-0.5B (theta=1e6) values. It compared three versions of the sin/cos reduction. The v0.3b mechanism was added by a coordinator directive after v0.3 missed the bar. Local x86_64 sandbox harness (scripts/h2m_accuracy_harness.py). Run by us.

**Results (exact, sourced).**

- The pre-registration was written before implementation.
  - Source quote: `**Status: pre-registered before implementation.**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_PREREG.md
- v0.2 (f32-only reduction, Taylor polynomial) had errors up to 115198 ULP for sin and up to 163969 ULP for cos, in the local oracle run.
  - Source quote: `| v0.2 (f32-only reduce, Taylor) | up to 115198 | 1.30e-2 | up to 163969 | 1.36e-2 |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_RESULT.md
- v0.3 (f64-staged reduction only) cut the error by roughly 55 to 70 times, with a max of 2813.5 raw ULP, and still missed the 2 ULP bar. The doc attributes the residual to the unchanged Taylor polynomial.
  - Source quote: `"<=2 ULP" bar is NOT met`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_RESULT.md
- v0.3b (octant reduction plus separate minimax polynomials) reached a maximum of 1.5 ULP for sin and cos on both models and met the bar, in the local harness run.
  - Source quote: `| **v0.3b (octant reduce, minimax)** | **1.5** | **1.2e-7** | **1.5** | **1.2e-7** |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_RESULT.md

**What it does NOT show.** Cross-ISA or CI confirmation (pending when written), positions above 8192, or that the final mechanism was pre-registered. It was added after the second version missed.

**Scope and caveats, as recorded.**

- Local x86_64 sandbox harness numbers only. CI runs were dispatched but were still in flight when the document was written, and the doc records no CI confirmation. Cross-ISA (aarch64) confirmation was pending.
- Positions 0 to 8192 only. The v0.3b run used a dense grid (stride 7, plus positions 0 to 19 and the last position), not every position.
- The 2 ULP bar was pre-registered for the v0.3 mechanism. The v0.3b mechanism was chosen after v0.3 missed, so it was not itself pre-registered.
- The doc says the v0.3 ULP counts are inflated near sin/cos zero-crossings, a known property of the ULP metric. The v0.3 filtered figure (values with |sin/cos| >= 1e-2) is up to 486.5 ULP.
- The work sits on branch cm/e15m-spec-v0.3-rope with 'Do NOT merge to main pending review'. The doc is on main, but the branch URL returns 404 unauthenticated, so the branch work is not public.
- Gate (3), the token-match oracle runs, was not re-run for v0.3b in that pass.
- Run by us; no unaffiliated reproduction.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** Fixing only the reduction improved the error a lot and still failed the bar, because the polynomial was now the dominant error. We kept the bar and changed both the reduction and the polynomials, which met it in the local harness.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_RESULT.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_PREREG.md

Read the pre-registration and the result page (links above). The branch the work sits on is not public.

<a id="lab-bitflip-weights"></a>

### One flipped bit in the weights: which checks notice?

*Date: 2026-09-13 | Outcome: Positive (the check worked as expected, within the stated scope) | Run by us; no unaffiliated reproduction.*

**Question.** If one bit of an AI model's weights is silently corrupted, can you tell by re-reading its output, or do you need to check the computation itself?

**Why it matters.** Weights are files that can be corrupted or tampered with. Re-reading the answer is the cheap check; checking the computation is the expensive one. We wanted to know how much the cheap one misses.

**Method, step by step.**

1. Take one pruned BitNet-2B checkpoint and one prompt, 64 greedy tokens.
2. Flip single bits in the weights: Experiment 1 used 50 trials, Experiment 2 used 295 trials spread across tensor classes.
3. Run three kinds of check on each corrupted run and count the misses, with 95% Wilson intervals.
4. Recount everything from the raw per-trial logs on a second host.

**Method as recorded.** Pruned BitNet-2B checkpoint, prompt 'Once upon a time', 64 new tokens, greedy, one host (aefinity-box). Experiment 1 (moat-3): 50 trials (5 no-flip controls, 40 random low-mantissa flips in bits 0-4, 5 forced bit-7 flips); A = text/argmax replay, B = top-5 logit-set match, C = full witness-chain digest match. Experiment 2 (moat-3b): 295 trials stratified by tensor class plus a bit-position sweep; the harness source (commit 1567ee1, header lines 28-30) defines A = generated token ids identical to the clean baseline, B = top-5 logit index set identical at every step, C = witness-chain digest match, which agrees with the write-up's summary tables. The write-up's setup paragraph describes Experiment 2's A and B differently (run completed without error; receipt accepted); the harness code is the authority. Wilson 95% intervals computed for the doc; counts recounted from raw per-trial logs on a second host (recomputation only, not re-inference). Harness commits (14ef1a1, 1567ee1) are public; we did not rebuild them for this summary.

**Results (exact, sourced).**

- Experiment 2 (295 trials): of 247 trials where the output logits changed, text replay (A: same generated token ids) missed 182. The harness source defines A this way; the write-up's setup paragraph describes A differently, but its tables and the code agree.
  - Source quote: `| text/argmax replay (A) | 182 / 247 | [0.679, 0.788] |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md
- Experiment 2: the top-5 logit-set check (B, labelled 'top-k / receipt-style' in the write-up's table) missed 82 of the same 247.
  - Source quote: `| top-k / receipt-style check (B) | 82 / 247 | [0.276, 0.393] |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md
- The witness digest row is 0 of 247. The document says this is exact by construction, since a digest miss and a C-fail are the same event.
  - Source quote: `| CIS witness digest (C) | 0 / 247 | [0.000, 0.015] |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md
- Experiment 1 (50 trials): text replay passed 3 corruptions that the digest caught (trials 16, 25, 47). Top-5 replay also failed on all 3, so its miss count was 0 at this sample size.
  - Source quote: `| A pass AND C fail (text replay misses a corruption the digest catches) | 3 |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md
- Null result: 43 flips (37 of 70 SCALE_FFN and 6 of 35 TRIT_FFN trials) left the witness digest identical to the clean baseline. The digest by design stays silent on these, and a byte-level check would flag them.
  - Source quote: `A byte-level integrity check would flag these 43 cases; the CIS digest, by design, does not, because it attests to computation, not storage.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md
- The write-up corrected its own original report after the second recount: trial 47 was a bit-7 flip from the random set, not one of the 5 dedicated high-bit control trials.
  - Source quote: `Correction from the second recount: the original report used trial 47 as "the" high-bit example;`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md

**What it does NOT show.** Adversarial tampering (none was tested), other prompts or models, or timing. The digest's 0 of 247 is exact by construction, so it is not evidence about the digest; the informative numbers are the misses of the other two checks.

**Scope and caveats, as recorded.**

- The digest's 0/247 is exact by construction (C is defined as a digest or baseline-output mismatch); the informative numbers are how often A and B miss.
- The write-up's setup paragraph describes Experiment 2's A as 'inference completed without error' and B as 'receipt accepted'. The harness source at commit 1567ee1 defines A as identical generated token ids, B as an identical top-5 logit index set and C as a witness-digest match, matching the write-up's tables; we follow the code.
- Experiment 1's random flips were low-mantissa bits 0 to 4 only (plus 5 forced bit-7 flips). Flips were chosen by the harness, not an adversary.
- B is the top-5 logit-set check in both experiments per the harness source; the write-up's prose calls Experiment 2's B a receipt check. The two experiments' counts are still reported separately, not merged.
- In Experiment 1 every method caught all 5 forced high-bit flips. In Experiment 2 the EMBED class (80 trials) was missed by both A and B 80 of 80 times.
- Embedding result: EMBED C-fail was 80/80 for the fixed prompt only. The unused-embedding-row case was not tested.
- No adversarial (optimised) tampering was tested. No timing claims are made.
- One pruned 2B checkpoint, one prompt, one hardware family; second host recomputed counts from logs only. The checkpoint is not linked publicly, so outsiders may not be able to rerun as-is.
- Run by us; no unaffiliated reproduction.

**Outcome.** Positive (the check worked as expected, within the stated scope).

**What we learned.** In the larger run, among the 247 trials where the output actually changed, the text-replay column missed 182 and the top-k/receipt-style check missed 82. Some flips (43) changed nothing in the computation. A check on the computation itself is by definition silent only on flips that changed nothing, but that 0/247 is true by construction, so the informative finding is how often the weaker checks miss. Single prompt and model, harness-chosen flips, no adversary.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-BITFLIP-HEADTOHEAD.md
- https://github.com/Aefinity-AI/alice-aegis/commit/14ef1a1
- https://github.com/Aefinity-AI/alice-aegis/commit/1567ee1

Read the result page and the two public harness commits (links above).

<a id="lab-embedding-edits"></a>

### Realistic edits to the embedding table, including one hidden row

*Date: 2026-09-17 | Outcome: Positive (the check worked as expected, within the stated scope) | Run by us; no unaffiliated reproduction.*

**Question.** Can a small, realistic edit to a model hide from output checks if the test prompts never touch it?

**Why it matters.** A realistic model edit may touch only rare words. If your tests never use those words, output checks pass while the model has changed.

**Method, step by step.**

1. Make realistic edits to the embedding table of one pruned BitNet-2B checkpoint: INT8 round-trip, 1% pruning, an approximated fine-tune patch, and single-row patches.
2. For single rows, pick 8 rows the prompts never read and 8 rows they do read, with 5 prompts each (40 trials per case).
3. Compare three detectors against the unedited baseline: text replay, top-5 logit set, witness digest.
4. Report counts with Wilson 95% intervals. A same-shape checkpoint substitution was attempted in design and found infeasible.

**Method as recorded.** Substitution classes on the bf16 embedding table (vocab 50,256, hidden 2,560) of one pruned BitNet-2B checkpoint: INT8 round-trip (a), 1% magnitude pruning (d), an approximated fine-tune patch (b), and single-row patches of +1 to the row's int8-quantized code (all 2,560 elements of the row move) on rows that the prompts do not read (b') or do read (b''). Global classes used a 20-prompt set; single-row classes used 8 rows x 5 prompts = 40 trials (a 5-prompt subset, rows sampled with a seed-42 PRNG), greedy decode, 64 new tokens. Detectors: A text replay, B top-5 logit-index set, C witness digest; 'detected' means the check differs from baseline. Wilson 95% CIs. Run by us; the harness is not yet published in a public repo.

**Results (exact, sourced).**

- For a single edited embedding row that none of the test prompts read (8 random rows x 5 prompts = 40 trials), text replay and the top-5 check each detected 0 of 40; the witness digest detected 40 of 40.
  - Source quote: `When the row is not exercised by the test prompts, A and B miss it completely (0/40 each in (b')).`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md
- Control with 8 rows the prompts do read (40 trials): the top-5 check detected 21 of 40 (52.5%, Wilson 37.5-67.1%); text replay detected 11 of 40 (27.5%). Even when rows are read, detection is only partial.
  - Source quote: `| B (top-5 logit-index check) | 21/40 | 52.5% | 37.5–67.1% | 0/40 (0.0%) |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md
- 1% magnitude pruning of the whole table (20 prompts): text replay detected 18 of 20 (90.0%, Wilson 69.9-97.2%); the top-5 check and witness digest detected 20 of 20.
  - Source quote: `| A (text replay) | 18/20 | 90.0% | 69.9–97.2% |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md
- In the classes that were run, the witness digest detected every trial. Here 'detected' means the digest differs from baseline; the document reports no false-positive test for it.
  - Source quote: `The witness digest (C) is the only detector of the three that caught every trial in every class tested here`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md
- UNABLE: substituting a different same-shape checkpoint was found infeasible and not run (no independently trained checkpoint with matching shape was available).
  - Source quote: `### (c) Different same-shape checkpoint — found infeasible`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md

**What it does NOT show.** Smarter attackers, rare-token patches, false positives of the digest, or any other part of the model than the embedding table. Samples are small (20 or 40).

**Scope and caveats, as recorded.**

- Small samples (n=20 or n=40), wide intervals; one checkpoint, one prompt set, embedding table only.
- The single-row classes used only a 5-prompt subset of the 20 prompts, and 8 rows; the 40 trials are 8 rows x 5 prompts, not 40 independent rows.
- The edit is +1 step of the int8-quantized code on all 2,560 elements of the row, not a bf16 last-bit edit.
- The INT8 class changed 96.91% of values (INT8 round-trip: all three detectors 20/20); the document says this does not show A/B would catch a smaller quantization.
- The fine-tune class is a labelled approximation (token-bigram nudge), not a real gradient step; the document calls its all-caught result weaker evidence than it looks.
- Row choice was a fixed-seed PRNG; the control (b'') drew rows from the prompts' own tokens, a looser selection than (b'). An attacker who knows the test prompts, or a patch confined to rare tokens, was not tested.
- The harness is not published, so the experiment cannot be rerun from the repo.
- Run by us; no unaffiliated reproduction.

**Outcome.** Positive (the check worked as expected, within the stated scope).

**What we learned.** Output checks are only as good as the prompts you test with. One edited row that no prompt read was missed by text replay and by the top-5 check in 40 of 40 trials, while a check over the computation caught all 40. Even when prompts did read the edited row, those output checks caught only 11 and 21 of 40.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-17-EMBED-SUBSTITUTION-HEADTOHEAD.md

Read the result page. The harness is not yet in a public repo, so the experiment cannot be rerun from public files.

<a id="lab-receipt-verified-eval"></a>

### Receipt-verified agent evaluation, and the hole we found in our own verifier

*Date: 2026-09-13 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** If every test item needs a verified receipt, can someone pass off a genuine receipt under the wrong item?

**Why it matters.** If a test score depends on receipts, someone could present a real receipt for the wrong test item. We tried to do exactly that to our own verifier.

**Method, step by step.**

1. Run 60 single-tool-call items; each emits a receipt that is replayed against pinned artifacts before it is scored.
2. Apply four hand-made tampers: flip an output token, change a tool-argument byte, truncate the chain by one step, file a valid receipt under another item.
3. Check version 1 (no item binding) and version 2 (item id, prompt and a session nonce folded into the start of the chain).

**Method as recorded.** 60-item single-tool-call suite (template T1), pruned BitNet-2B, one host (box1). Every item emits an agent_trace receipt that is replayed against pinned model/embed/vocab artifacts before the item is scored. One hand-made tamper was applied to each of four items: flip an output token, change a tool-arg byte, truncate the chain by one step, and replay a valid receipt under a different item's filename. v1 receipts have no context binding. v2 folds item-ctx = sha256(item_id || prompt_bytes || session_nonce) into the trace genesis. Run by us.

**Results (exact, sourced).**

- All 60 receipts verified.
  - Source quote: `| Receipt verification | 60/60 PASS |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md
- Task score on receipt-verified outputs.
  - Source quote: `| Score (receipt-verified outputs, arg_match AND output_match) | 45/60 |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md
- v1 caught 3 of 4 tampers; after context binding, v2 caught all 4.
  - Source quote: `Overall: v1 = 57/60 PASS, **3/4 tampers caught**. v2 = 56/60 PASS, **4/4 tampers caught**.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md
- The v1 miss: a valid receipt filed under another item's name (lookup_hit_01) verified like a genuine one.
  - Source quote: `**PASS (not caught)**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md

**What it does NOT show.** Out-of-sample protection: the fix was tested on the same four cases that exposed the hole. One host, one model and one template. The 45 of 60 is a task score, not a benchmark.

**Scope and caveats, as recorded.**

- Four hand-made tampers, not adversarially optimized or randomly sampled; the v2 fix was tested on the same four cases that exposed the hole, so 4/4 is not out-of-sample.
- Template T1 only (calculator, lookup, mixed single tool-call turns); one pruned BitNet-2B model; a single host (box1) generated all receipts, so there is no cross-machine claim.
- The 45/60 score is a task score on receipt-verified outputs and is not a benchmark. The source reports no timing figures.
- The fix lives on branch cm/safe2c-ctx-binding (commit 13ed3c47ae5a), and the source says it was not yet merged into alice-aegis main.
- Run by us; no unaffiliated reproduction.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** A receipt can verify and still be filed on the wrong item. We found that by trying to break our own verifier, and binding each receipt to its item closed the case we found.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-13-RECEIPT-VERIFIED-EVAL60.md
- https://github.com/Aefinity-AI/alice-aegis/commit/13ed3c47ae5a

Read the result page and the fix commit. The source says the fix was on a branch not yet merged into main.

<a id="lab-logging-vs-receipts"></a>

### Ordinary logging versus replay-based receipts on one-field edits

*Date: 2026-09-22 | Outcome: Positive (the check worked as expected, within the stated scope) | Run by us; no unaffiliated reproduction.*

**Question.** If someone edits one field in an AI agent's log, does the log show it?

**Why it matters.** Logs are text. The question is whether a log can tell you it has been edited.

**Method, step by step.**

1. Record one two-step tool-using episode.
2. Make three single-field edits to the record.
3. Look at each in the receipt's own unverified display, then run the replay verifier.

**Method as recorded.** Three single-field mutations of one recorded two-step tool-using episode (pruned BitNet-2B, one host, 2026-09-22), each shown in the receipt's own unverified display and through the replay verifier. Run by us.

**Results (exact, sourced).**

- A changed internal token id (one id, step 0) was invisible in the ordinary display, but replay named the step and the field.
  - Source quote: `(verifier line: step 0 divergence: toks-match=false tool-match=true in-match=true out-match=true decode-chain-match=true)`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/RECEIPT-VS-LOGGING.md
- An altered tool output ('20' changed to '21') was rejected at step 0 by replay. In the ordinary display this change was visible as printed text, but nothing in the log format flagged it as wrong.
  - Source quote: `(verifier line: step 0 divergence: toks-match=true tool-match=true in-match=true out-match=false decode-chain-match=true)`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/RECEIPT-VS-LOGGING.md

**What it does NOT show.** Anything about third-party logging products; the 'ordinary logging' here is our own display. Three edits, one episode, one machine.

**Scope and caveats, as recorded.**

- Three chosen mutations of one episode, one model, one machine; not adversarial.
- 'Ordinary logging' is our own unverified display, not a third-party logging product.
- The viewer only reformats the verifier's verdict; it is not independent evidence.
- Run by us; no unaffiliated reproduction.
- In the altered-tool-output case the ordinary display did show the changed value ('21'); the source's point is that the log format itself does not flag it.
- The source describes a third case, a flipped decode-chain digest bit, also caught at step 0 and invisible in the ordinary display. It is omitted from this entry's results.
- Model artifacts are referenced by hash only and are not checked into the public repo. The fixtures live in the alice-aegis repo, and this entry does not verify that repo is public.

**Outcome.** Positive (the check worked as expected, within the stated scope).

**What we learned.** A log is text anyone could have typed. Replaying the computation catches the mismatch without knowing in advance which field was changed.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/RECEIPT-VS-LOGGING.md

Read the result page (link above).

<a id="lab-receipt-overhead"></a>

### What receipts cost on a real agent episode

*Date: 2026-09-22 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** How much slower and heavier does an AI agent get when every step carries a verifiable receipt?

**Why it matters.** Integrity checks are not free. A claim that every step is verifiable means little without its cost next to it.

**Method, step by step.**

1. Run one three-step agent episode with receipts on box1 and time it.
2. Time a plain 72-token decode of the same prompt.
3. Verify the receipt locally on box1 and through a single-worker daemon on box2.
4. Re-run box1 once more to read peak memory and CPU-package energy.

**Method as recorded.** One agent episode (scenario1-tool-use: 3 steps, 24-token budget per step) on a pinned BitNet-2B artifact triple. box1 = Intel i5-5200U (AVX2/FMA); box2 = Celeron N4020 (no AVX2/FMA), which verifies only through a gateway daemon with a single background worker (box2 never runs 2B generation). The phone was unreachable and was not tested. Peak memory and energy come from a separate re-run on 2026-09-23 of the identical command on box1. Run by us.

**Results (exact, sourced).**

- On box1, the 3-step episode with receipts took 44.74 s wall-clock. A plain single-pass 72-token decode of the same prompt took 17.84 s (2.51x). The receipt is 1,599 bytes. Local verification took 40.08 s and passed. The source calls 2.51x an upper bound on receipt cost, not a clean measurement of the receipt code, because the episode loop also re-prefills at every step and the plain decode does not.
  - Source quote: `| box1 (aefinity-box) | 44.74s wall (`agent_trace gen`, K=3 N=24) | 17.84s wall (`cis_decode`, N=72, same prompt) | 1599 bytes | 40.08s wall, PASS (local, direct) |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md
- On box2, the daemon returned ALLOW (PASS) about 12 min 13 s after submission. This figure is bounded by polling at 20 s intervals and is not a precise wall-clock time. An earlier run of the same scenario shape through the same daemon took about 7.5 min.
  - Source quote: `~12m13s submit-to-ALLOW`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md
- On box1, a separate 2026-09-23 re-run of the same command (45.94 s elapsed) had a peak resident set size of 1,309,996 KB. Its energy was 369.45 J, measured on the CPU package only (RAPL package-0), over a window of about 46 s. The source says to read this as a lower bound on whole-system energy.
  - Source quote: `| box1 (aefinity-box) | 1,309,996 KB | 369.45 J (RAPL package-0 only, ~46s window) |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md
- The box2 timing was not controlled for other queue activity. The daemon serializes all verify work through one worker, so the source reports the two box2 timings as observed rather than as a single figure.
  - Source quote: `no attempt was made to control for other daemon-queue activity`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md

**What it does NOT show.** A clean measurement of receipt cost (the two timed runs are different workloads), repeat statistics, wall-power energy, or any phone result (the phone was unreachable).

**Scope and caveats, as recorded.**

- One episode, one run per cell, wall-clock; no repetition statistics.
- The two timed runs are different workloads: a 3-step tool-use loop that re-prefills at each step, versus a plain 72-token single-pass decode. The source says the 2.51x is an upper bound on receipt cost, not an isolation of the receipt code. A separate earlier single-step (K=1) run is reported in the source as 31.2% overhead, 946 bytes per receipt and 14.865 s verify. That figure is cited in the source only, with no link to its own page.
- box2 timing is polling-bounded (20 s poll interval) and depends on daemon queue activity. Two observations were 12m13s and an earlier ~7.5 min. box2 memory and energy and all phone results are n/a (box2 never runs 2B generation, no energy meter on box2, phone unreachable).
- Peak memory and energy come from a separate re-run (45.94 s, 1,309,996 KB). The original run's peak RSS is inconsistent within the source: the prose says 1,406,336 KB and the source's own note says 1,463,176 KB. The source itself says the prose figure appears to predate the committed log.
- Energy is CPU package only (RAPL), not wall power.
- Underlying logs are committed in a repo that is not public; only the summary page is publicly checkable.
- Run by us; no unaffiliated reproduction.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** Receipts are not free. In this episode the receipt loop took 2.51x the plain decode, and the source calls that an upper bound. On old hardware, verification took 40 s on box1 and minutes on box2. The cost should be reported next to every integrity claim. These are single runs, not a benchmark.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-RECEIPT-OVERHEAD-TABLE.md

Read the result page. The underlying logs are in a repo that is not public.

<a id="lab-continuous-validation"></a>

### Continuous validation: does a one-byte corruption get caught, and what hides it?

*Date: 2026-09-27 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** If one byte of a deployed model file changes, will a monitoring check actually report it?

**Why it matters.** A monitor that quietly repairs what it was meant to report is worse than no monitor.

**Method, step by step.**

1. Run the self-check twice by hand, about 6.5 minutes apart.
2. Overwrite one byte of model.safetensors on purpose and run the verifier on it.
3. Restore the files and run the monitor script twice by hand.
4. Re-run on a fresh clone on 2026-10-01.

**Method as recorded.** By hand on one host (Intel i5-10210U, no GPU, ChromeOS Crostini): two self-checks about 6.5 minutes apart, one byte of model.safetensors overwritten on purpose (0xff at offset 1,000,000), the verifier run directly on the corrupted file, then the files restored and the monitor script run twice by hand (about 11 minutes apart, clean files only). No scheduler. A re-run on a fresh clone at commit 205b024 on 2026-10-01 reproduced the monitor PASS and the corruption FATAL. Run by us.

**Results (exact, sourced).**

- Two baseline runs matched.
  - Source quote: `**Phase 1 result: PASS** — two hand-started runs, about 6.5 minutes apart on one host, produced matching digests (n=2, same host, same day).`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md
- A one-byte weight change was stopped by the sha256 hash pin in the verifier before the forward pass ran.
  - Source quote: `CIS2_VERIFY3 FATAL: model.safetensors sha256 mismatch,`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md
- Negative finding: the self-check's fetch step detects the mismatch but re-downloads the pinned weights, so the monitor (which wraps the self-check) would likely log PASS and mask the corruption. This was inferred from the earlier self-check run on the corrupted file; the monitor itself was not run on corrupted weights.
  - Source quote: `repairs corrupted weights silently and would likely log PASS, masking the corruption in monitor mode`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md
- The monitor's FAIL path was never exercised.
  - Source quote: `The monitor script was not run against corrupted weights, so its FAIL path was not exercised in this experiment.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md
- A flaw in our own monitor script was disclosed: the logged 'digest_hint' was really a test-binary name suffix (script since changed to parse the witness digest line, or print unknown).
  - Source quote: `is not a model or output digest. It is the suffix of the cargo test binary name`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md

**What it does NOT show.** That continuous validation works as a deployed service. There was no scheduler, n=2, one host, and the monitor was never run on corrupted weights.

**Scope and caveats, as recorded.**

- Shows only that the file-hash gate works; the corrupted run never reached the forward pass, so this is no new evidence about logit digests.
- config.json, tokenizer.json, tampered pins/EXPECTED_DIGESTS.md and a tampered verifier binary were not tested.
- n=2 on one host, no scheduler, hand-run; the document says it is not an operational continuous-validation deployment. Scheduled operation, multi-host and long-horizon data not shown.
- The monitor PASS only means the self-check matched this repository's own EXPECTED_DIGESTS.md; the document calls it a consistency check, not an independent one.
- The 2026-10-01 re-run was by us; the source calls it 'independent' but no outside party is named, so no unaffiliated reproduction. The 09-27 run times and the second baseline run could not be re-checked.
- The document says wiring the monitor to cron and disabling the fetch self-repair in monitor mode would be needed before FAIL could serve as an incident signal.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** The hash gate catches a one-byte change. But a convenience feature, the automatic re-download, would likely hide exactly the corruption a monitor exists to report (inferred, not run on corrupted input).

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-27-CONTINUOUS-VALIDATION.md

Read the result page. The repository's self-check commands are above under CIS-2.

<a id="lab-training-checkpoints-cross-isa"></a>

### Training checkpoints across CPUs and instruction sets

*Date: 2026-09-24 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** If you run the same training job with the same seed on two computers, do you get the same model?

**Why it matters.** If the same training job gives different checkpoint bytes on different computers, a trained model cannot be reproduced from its recipe.

**Method, step by step.**

1. Train a tiny language model with a fixed seed and corpus; hash the raw parameter bytes at steps 50, 100, 150 and 200.
2. Run default PyTorch on an AVX2 CPU and a no-AVX2 CPU.
3. Run PyTorch again with the CPU kernel and thread count pinned.
4. Run a from-scratch fixed-order C trainer (13,088 parameters) on five hosts.

**Method as recorded.** A tiny language-model trainer, checkpoints at steps 50, 100, 150 and 200 hashed (sha256) over raw parameter bytes, same seed and synthetic corpus in every run. Three variants: default PyTorch (torch 2.14.0+cpu) on an AVX2/FMA CPU (Intel i5-5200U) and a no-AVX2 CPU (Intel Celeron N4020); the same PyTorch script with the CPU kernel pinned (ATEN_CPU_CAPABILITY=default, MKL_CBWR=COMPATIBLE, single-threaded) on the same two machines; and a from-scratch fixed-order fp32 C trainer (byte-level MLP, 13,088 parameters, 200 steps) on five hosts: three x86_64 without AVX2, one x86_64 with AVX2/FMA, and one aarch64 phone. Run by us.

**Results (exact, sourced).**

- Default PyTorch: the printed losses were identical, but every checkpoint hash differed between the two CPUs from step 50. Same-machine reruns matched on each host. The source calls the cause (different vectorized kernel path) 'consistent with', not demonstrated.
  - Source quote: `**MISMATCH.** The four printed loss scalars are bit-identical (same Python `repr()` at every checkpoint on both hosts), but all four checkpoint sha256 digests differ, starting at the first recorded checkpoint (step 50).`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-24-CROSS-ISA-TRAINING-RECEIPT.md
- Pinned PyTorch (kernel dispatch and thread count pinned) gave byte-identical checkpoints on the same two x86_64 machines; the source says this is not a cross-ISA result.
  - Source quote: `**MATCH — cross-machine, not cross-ISA.**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-24-CROSS-ISA-TRAINING-RECEIPT.md
- The fixed-order C trainer gave identical checkpoint hashes on all five hosts, including one aarch64 phone; a second clean build on one x86_64 host and the phone reproduced the same digests.
  - Source quote: `All four checkpoint sha256 digests are identical across all five hosts: three x86_64 machines without AVX2, one x86_64 machine with AVX2/FMA, and one aarch64 machine — a cross-ISA result.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-24-CROSS-ISA-TRAINING-RECEIPT.md

**What it does NOT show.** Large models, GPUs, or any general guarantee. Each result is an observed outcome for one configuration on our own hosts.

**Scope and caveats, as recorded.**

- Toy scale: the C trainer has 13,088 fp32 parameters and runs 200 steps; no claim about large models or step counts.
- The C trainer is a different architecture (byte-level MLP) from the PyTorch runs; no numeric parity between them is claimed.
- CPU only; no GPU host was tested.
- The C trainer source is not released.
- One run per configuration; the cross-ISA result rests on a single aarch64 device.
- The source pins no general guarantee: each result is an observed outcome for its specific configuration and host set.
- No timing figures are reported (identity/correctness experiment only).
- Our own hosts only. Run by us; no unaffiliated reproduction.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** Identical printed loss numbers hid different checkpoint bytes; only hashing the raw bytes revealed it. Pinning the kernel made two x86_64 machines agree, and a fixed-order trainer gave identical bytes across instruction sets, shown so far only at toy scale on our own hosts.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-24-CROSS-ISA-TRAINING-RECEIPT.md

Read the result page. The C trainer source is not released.

<a id="lab-e22-necessity-matrix"></a>

### E22: which spec rules does the test vector actually exercise?

*Date: 2026-09-09 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** If we deliberately break one rule of our own spec, does the official test notice?

**Why it matters.** A passing test only means something if breaking the rules makes it fail. We broke our own rules to see how much the test notices.

**Method, step by step.**

1. Make 16 single-rule mutations of the C verifier.
2. Build and run each against the pinned vector on one host.
3. Include unmutated builds at four optimisation levels as controls.
4. Count a rule as exercised if breaking it moves the digest.

**Method as recorded.** Sixteen single-clause mutations of the C verifier (CIS-2 v0.3b), each built and run against the pinned test vector (a single 4-token prompt on a 135M checkpoint with head_dim = 64) on one host (cm-box1, i5-5200U, gcc 14.2.0), plus unmutated builds at four optimisation levels as positive controls. A clause counts as exercised if breaking it moves the witness digest. Run by us; one machine, one compiler.

**Results (exact, sourced).**

- 12 of 16 mutations moved the digest, 3 did not, 1 was declared skipped (M07, skipped by the leg).
  - Source quote: `**12 of 16 mutations moved the digest. 3 did not. 1 was declared skipped.**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md
- The argmax tie-break rule (M15, section 11) is not exercised by this vector because no tie occurs in any of its 16 argmaxes over a 49152-wide fp32 logit vector. The source says the clause is correct and necessary in general and that the vector never reaches the branch.
  - Source quote: `**M15** | **§11 argmax tie-break** | **SAME** | **not exercised**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md
- Correction by the authors: the M16 row (attention scale via pinned rsqrt) was a vacuous mutation, because it substituted the function for its own body, so it tested nothing. The first published explanation (head_dim = 64 is a perfect square) was withdrawn as a rationalisation.
  - Source quote: `**VACUOUS MUTATION — see correction below**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md
- A rule that can be broken without effect on the digest is untested by this vector, not redundant. This is a statement about the conformance suite, not the spec.
  - Source quote: `A clause that can be broken with no observable effect is not thereby redundant`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md
- Unmutated builds reproduced the baseline digest at four optimisation levels (O0, O1, O3, Os). Scope is this compiler on this host only.
  - Source quote: `-O0 / -O1 / -O3 / -Os   →  d82743059d…  SAME`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md

**What it does NOT show.** That a rule is redundant just because the vector does not exercise it. Also not shown: any result on another compiler or machine.

**Scope and caveats, as recorded.**

- One compiler (gcc 14.2.0), one machine (i5-5200U), one 4-token prompt on one 135M checkpoint with head_dim = 64. The source says the silence is a property of this vector, not of the spec.
- Run by us; no unaffiliated reproduction.
- M01 (section 1.3 FTZ/DAZ pin) was revised after the first run by E38, E39 (erratum E-12) and E40 (erratum E-13). Its null is now explained: no denormal arises anywhere in the decode on the two checkpoints tested (E40 counted 562,531,070,920 intermediates, 0 subnormal). The clause is untriggered here, not unnecessary, and there is still no end-to-end necessity witness. The spec guards it separately: section 15 item 4 requires its self-test to pass independently of the digest.
- M07 (section 6.1) was skipped, so it is neither a hit nor a miss.
- The M16 correction and rsqrt route table were measured on a different host (penguin, Crostini, gcc -O2) than the main matrix. The source says the section 6.1 check rsqrt(64.0) == 0.125 cannot discriminate between implementations. Op-level goldens for rsqrt and the tie-break were added later in cis2-verify (follow-up items 2 and 3 marked done).
- The source reports no timing figures from this run.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** Passing the published test does not prove every rule matters. 12 of 16 single-rule breaks were caught. The tie-break and the denormal-flush pin are protected only by inputs this vector never contains. One of our own null results turned out to be a vacuous edit that tested nothing, and we corrected it in place. Correcting it exposed a weak spot in the spec's own rsqrt check, which tests only a value where every implementation agrees.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E22_NECESSITY_MATRIX.md

Read the matrix page and the corrections inside it (link above).

<a id="lab-e24-unicode-gap"></a>

### E24: the spec never says which Unicode version defines a letter

*Date: 2026-09-09 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** Can two programs that follow the spec exactly still split the same text differently?

**Why it matters.** Splitting text into tokens depends on which characters count as letters. Two programs that follow the spec could split differently.

**Method, step by step.**

1. Notice our own CI check fail the same way on x86_64 and aarch64.
2. Generate the letter, number and whitespace tables under Unicode 15.0.0 and 15.1.0 and difference the sets.
3. Encode four test strings with both tables.

**Method as recorded.** A CI check that regenerates the verifier's Unicode tables (cis2-verify/tools/gen_unicode.py) failed identically on the x86_64 and aarch64 GitHub runners (run 34340397775), so it was not an ISA difference. The difference between Unicode 15.0.0 and 15.1.0 was then measured by generating the LETTER, NUMBER and WHITESPACE tables twice in one session (unicodedata2==15.0.0 vs the interpreter's own 15.1.0 database) and differencing the codepoint sets. Measured on the development box (Debian 13, x86_64, crosvm guest) and GitHub ubuntu-24.04 / ubuntu-24.04-arm runners. Run by us. Concerns spec v0.3b section 3.1.4.

**Results (exact, sourced).**

- The LETTER table grew by 622 codepoints between Unicode 15.0.0 and 15.1.0 (CJK Unified Ideographs Extension I). The NUMBER and WHITESPACE tables did not change.
  - Source quote: `| LETTER | `\p{L}`, `char::is_alphabetic` | 136,104 cp | 136,726 cp | **+622: U+2EBF0..U+2EE5D** |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E24_UNICODE_VERSION_GAP.md
- Spec v0.3b names no Unicode version for the pre-tokenizer's property classes.
  - Source quote: `Neither the clause nor any other part of the document names a Unicode version.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E24_UNICODE_VERSION_GAP.md
- Bounded: this is a finding, not a reproduction failure, and no published digest moves.
  - Source quote: `**Status:** finding, bounded. Not a reproduction failure. No published digest moves.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E24_UNICODE_VERSION_GAP.md

**What it does NOT show.** Any change to the published digests; the finding is bounded. The spec text itself is unchanged and the fix is proposed for v0.4.

**Scope and caveats, as recorded.**

- Found by our own CI, not an outside report.
- Run by us; no unaffiliated reproduction.
- Harmless for the pinned artifacts: for the pinned SmolLM2-135M vocabulary, four test strings encoded to identical token ids with the 15.0.0 and 15.1.0 tables. The source says this holds by property of the vocabulary, not by anything the spec states, and a future Unicode release could diverge.
- The spec amendment pinning Unicode 15.1.0 is only proposed for v0.4; the fix is a maintainer decision.
- Only the checkability of the generated file was fixed (REQUIRED_UCD pin and CI install of unicodedata2==15.1.0); the spec text itself is unchanged.
- The source states no timing number from these runs may be used.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** A spec can be exact about arithmetic and still leave the input text under-specified. Claims like 'generated from the Unicode database' need a check pinned to the environment.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E24_UNICODE_VERSION_GAP.md

Read the finding (link above).

<a id="lab-e25-rmsnorm-order"></a>

### E25: the RMSNorm multiply order matters, and our spec sentence saying otherwise was false

*Date: 2026-09-09 | Outcome: Positive (the check worked as expected, within the stated scope) | Run by us; no unaffiliated reproduction.*

**Question.** Does a tiny change in the order of multiplication change the AI's internal numbers, even when the output text stays the same?

**Why it matters.** If text matches while the bits differ, comparing output text cannot show that two systems computed the same thing.

**Method, step by step.**

1. Build a census version of the decode that uses the non-conforming multiplication order.
2. Run SmolLM2-135M on 'Once upon a time' for 16 tokens.
3. Count elements that differ, and check whether the digest and the tokens moved.

**Method as recorded.** Scalar witnesses, a unit test of the real function, and a census build running the pinned decode in the non-conforming order on SmolLM2-135M (prompt "Once upon a time", 16 generated tokens), one host (a Debian 13 Crostini VM on ChromeOS, x86_64; no timing reported). Run by us; recorded as erratum E-1.

**Results (exact, sourced).**

- The spec's earlier claim that no divergence had been observed was wrong.
  - Source quote: `That sentence is false as of 2026-09-09.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md
- 34.60% of RMSNorm elements in one 16-token decode differ between the two orders (SmolLM2-135M).
  - Source quote: `231,014 of 667,584 RMSNorm elements — 34.60% — distinguish the two orders in a single 16-token decode.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md
- The alternate order moved the witness digest.
  - Source quote: `CENSUS witness_digest_moved=true`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md
- In the same run, the generated tokens did not change (for this 16-token vector only).
  - Source quote: `CENSUS argmax_digest_moved=false`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md

**What it does NOT show.** That tokens never change: a longer decode might compound the differences, and this was not tested.

**Scope and caveats, as recorded.**

- The false sentence had already been shown false by E22 and was not updated until E25.
- The SmolLM2-135M result is one pinned vector; the census build is an instrument, not a conforming verifier. The document also reports a second model (Qwen2.5-0.5B) census, and the CHANGELOG E-1 addendum gives its counts; the entry's figures here are SmolLM2 only.
- The source states tokens_moved=false is a fact about this 16-token vector, not a guarantee: a longer decode could compound one-ULP differences into a different argmax. E25 does not test that.
- An earlier draft reported a raw counter (1,335,168) without noting a double decode; corrected in the document.
- Run by us on one host; no unaffiliated reproduction.

**Outcome.** Positive (the check worked as expected, within the stated scope).

**What we learned.** A reordering that leaves the generated text unchanged (on this short vector) still changes the bits, so comparing text is not enough. A published limitation was out of date, and we corrected it in the open.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E25_RMSNORM_ASSOCIATION.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/CHANGELOG.md

Read the page and the CHANGELOG erratum E-1 (links above).

<a id="lab-e26-trig-range"></a>

### E26: sin/cos at very long contexts — the sampled answer was wrong

*Date: 2026-09-09 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** Does the pinned sin/cos stay accurate at the huge angles a million-token context produces, and can spot-checking tell you?

**Why it matters.** Spot-checking a function is cheap and can be reassuring and wrong.

**Method, step by step.**

1. Run a sampled sweep of 4,096 arguments per binade.
2. Replace it with an exhaustive sweep of every f32 in [0, 2^20) against a float64 oracle.
3. Check symmetry and the rotary angle sets for 131,072 positions on both models.

**Method as recorded.** First a sampled sweep of 4,096 arguments per binade (reported max 1 ULP for sin and cos over [2^0, 2^16)); then an exhaustive sweep of every f32 in [0, 2^20) against a float64 host-libm oracle, plus symmetry checks and the RoPE angle set for 131,072 positions on both models (SmolLM2-135M and Qwen2.5-0.5B), on one VM (ChromeOS Crostini, x86_64) under the pinned FTZ+DAZ floating-point environment. Run by us.

**Results (exact, sourced).**

- The first, sampled answer was wrong.
  - Source quote: `The first answer was wrong, and the way it was wrong is the point`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md
- The sample never landed on the hard cases.
  - Source quote: `4096 samples out of 8,388,608 per binade simply never landed near a zero of`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md
- Exhaustive sweep below 2^16, measured in ULP of the result: sin 66, cos 2283 (large near zeros of sin and cos). The sampled sweep had reported at most 1 ULP (one 2-ULP cos) over [2^0, 2^16). Over the full [0, 2^20) sweep the ULP maxima are sin 2283, cos 2617.
  - Source quote: `TRIG-X EXHAUSTIVE |x|<2^16 max|ulp| sin=66 (at 4.4767695e3)  cos=2283 (at 5.2516434e4)`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md
- The full sweep covered 1,233,125,376 arguments.
  - Source quote: `Every f32 in `[0, 2^20)` — **1,233,125,376 arguments**, subnormals included:`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md
- Measured as absolute error, the worst case over [0, 2^20) is 9.4218e-8, which is 0.790 ULP-of-unity.
  - Source quote: `over the entire range is **0.790 ULP-of-unity**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md

**What it does NOT show.** A proof, behaviour at |x| of 2^31 or more, or that the ULP figure measures a defect: it is inflated near zeros of sin and cos.

**Scope and caveats, as recorded.**

- The large ULP figures are ULP of the result near zeros of sin/cos, where relative error is inflated; the absolute-error figure is the one about the reduction (at the worst ULP point the absolute error is 1.86e-11).
- The accuracy oracle is the host libm (glibc f64 sin/cos rounded to f32); the spec pins bits, not accuracy, and a more accurate reduction would be non-conforming. Double rounding can shift a reported ULP count by one.
- Source: an exhaustive enumeration on one host, not a proof; nothing is claimed for |x| >= 2^31. Worst absolute error below 2^31 is 2.0925e-7 (1.756 ULP-of-unity).
- The earlier sampled program is kept in the repo marked SUPERSEDED, with its numbers not to be quoted.
- No timing figures (VM).
- Run by us on one machine; no unaffiliated reproduction.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** 4,096 samples per binade never hit the worst points among about 8.4 million, so sampling gave a comfortable answer that was wrong. An exhaustive sweep replaced it. Absolute error stays flat while ULP error grows near zeros of sin/cos, so ULP alone is the wrong figure of merit for these functions.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E26_TRIG_RANGE.md

Read the page (link above); the earlier sampled program is marked SUPERSEDED.

<a id="lab-e27-exp-ln-range"></a>

### E27: exp, ln and SiLU on every float32 input, and a defect in our spec

*Date: 2026-09-09 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** Is the pinned exponential accurate on every possible input, and are the spec's safety guards correct?

**Why it matters.** The softmax inside every transformer uses exp. If its guards are wrong the spec pins a wrong answer exactly.

**Method, step by step.**

1. Evaluate exp, ln and SiLU on all 2^32 float32 bit patterns.
2. Compare against a float64 reference and run oracle-free monotonicity checks.
3. Re-run on a second machine.

**Method as recorded.** Every one of the 2^32 f32 bit patterns evaluated for exp_pinned, ln_pinned and silu_pinned under the pinned environment (FTZ/DAZ, 8 worker threads) against a host glibc float64 oracle narrowed to f32 and flushed, plus oracle-free monotonicity checks. Run by us on one machine (penguin, x86_64 VM); the same binary was re-run by us on a second machine (Celeron, no AVX2, same glibc) with a byte-identical log.

**Results (exact, sourced).**

- Every one of the 3,257,925,634 arguments where both the pinned exp and the oracle are finite is within one ULP (max relative error 1.1921e-7 = 2^-23), measured against a float64 oracle.
  - Source quote: `Every one of the 3,257,925,634 arguments for which both `exp_pinned` and the oracle are finite is within **one ULP**.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E27_EXP_LN_RANGE.md
- Defect in our own spec: the high guard (x > 88.0 returns +Infinity) clips 94,743 arguments (0x42B00001 to 0x42B17217) whose true exp is finite and representable in f32. Behaviour is pinned as normative and unchanged; an erratum was filed.
  - Source quote: `§6.2's high guard clips 94,743 values below the representable range`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E27_EXP_LN_RANGE.md
- exp and ln were monotone over the whole finite domain (zero violations), an oracle-free check.
  - Source quote: `exp monotone: violations=0`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E27_EXP_LN_RANGE.md

**What it does NOT show.** Correct rounding, a second compiler or libm, or that the defective range is reachable by other models or prompts (it was entered 0 times in the instrumented decode).

**Scope and caveats, as recorded.**

- Accuracy is against a float64 oracle (host glibc exp narrowed to f32), not correct rounding; where narrowing double-rounds the oracle itself may differ from the correctly rounded f32.
- The headline is the guard defect, not the accuracy.
- The source states the second-machine re-run used the same binary and same glibc, so it does not test a second compiler or libm.
- The clip band was entered 0 times in an instrumented decode (one model, six ASCII prompts, at most 64 tokens); no claim that other models or prompts cannot reach it.
- Two-ULP silu figure is for the function in isolation, not accumulated through an FFN.
- The source says an earlier draft's FTZ reasoning about the silu discontinuity was wrong; E39 (CHANGELOG ERRATUM E-12) later corrected neighbouring FTZ reasoning.
- Run by us; no unaffiliated reproduction.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** The accuracy was the unremarkable part. Exhaustive testing found a real defect in our own spec that sampled tests could not, and we recorded it in the open.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E27_EXP_LN_RANGE.md

Read the page (link above).

<a id="lab-layer-oracle-e28-e36-e37"></a>

### E28, E36, E37: every internal activation compared against an independent implementation

*Date: 2026-09-09 | Outcome: Positive (the check worked as expected, within the stated scope) | Run by us; no unaffiliated reproduction.*

**Question.** Could errors inside the model cancel out, so the final answer looks right while the inside is wrong?

**Why it matters.** Errors inside a model could cancel, so the final answer looks right while the middle is wrong.

**Method, step by step.**

1. Feed the same token ids to our verifier and to a Hugging Face transformers fp32 forward pass.
2. Compare every intermediate tensor.
3. Start with one prompt, then widen to six cells on each model.

**Method as recorded.** Teacher-forced comparison of every intermediate tensor of the verifier against a Hugging Face transformers fp32 forward pass: one prompt on SmolLM2-135M and Qwen2.5-0.5B (E28), then six prompt/length cells on SmolLM2-135M (E36) and six on Qwen2.5-0.5B (E37). Run by us.

**Results (exact, sourced).**

- E28: 13,452 intermediate tensors (one prompt, 19 positions, two models: SmolLM2-135M and Qwen2.5-0.5B) compared; worst relative L2 disagreement 9.9e-5, on one tensor of one model (Qwen). This is a single-prompt maximum, not a bound for the model.
  - Source quote: `Worst disagreement: **9.9e-5** relative`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E28_LAYER_ORACLE.md
- E36 corrected our own published worst case: over six SmolLM2-135M prompt cells (80,565 tensors) the worst was 3.406e-05, 1.53 times the 2.228e-05 E28 published from its single SmolLM2 prompt.
  - Source quote: `worst case is **3.406e-05**, 1.53x the`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E36_ORACLE_PROMPT_SWEEP.md
- E37: six Qwen2.5-0.5B cells add 64,260 tensors; with E36 that is 144,825 tensors across two architectures. On Qwen, E28's 9.923e-05 turned out to be the six-cell maximum (rel_rms rose to 2.883e-03); the earlier layer-ratio bounds were per-prompt and were corrected (erratum E-9).
  - Source quote: `Taken with E36 this is 144,825 tensors across two`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E37_QWEN_ORACLE_SWEEP.md

**What it does NOT show.** Bit-exactness (the oracle is a different implementation), tokenization, or all prompts.

**Scope and caveats, as recorded.**

- Agreement is to about 1e-5 relative (up to ~1e-4 on Qwen), not bit-exact, because the oracle is a different implementation and must not be bit-exact; this is an accuracy check, not a determinism check.
- Two small models; six prompts per model is still not all prompts (E37 states this).
- The Qwen runs use supplied token ids from the oracle tokenizer and are not conformance runs; they attest to spec sections 4-11 only, not tokenization (section 3).
- The oracle (transformers) is an independent implementation, not ground truth.
- Not run in CI; reproducible on demand with the model artifacts and torch.
- Run by us; no unaffiliated reproduction.

**Outcome.** Positive (the check worked as expected, within the stated scope).

**What we learned.** A maximum measured on one input is only that input's maximum. Widening the sweep corrected our own published number on SmolLM2 (1.53x higher), and on Qwen showed the single-prompt figure happened to be the worst case, so it was unknown, not reliably low.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E28_LAYER_ORACLE.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E36_ORACLE_PROMPT_SWEEP.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E37_QWEN_ORACLE_SWEEP.md

Read the three pages (links above). The comparison is reproducible on demand with the model artifacts and torch; it is not run in CI.

<a id="lab-e29-optimizer-invariance"></a>

### E29: does the compiler's optimiser change the bits?

*Date: undated in the source | Outcome: Positive (the check worked as expected, within the stated scope) | Run by us; no unaffiliated reproduction.*

**Question.** Does getting identical results mean giving up on fast, optimised code?

**Why it matters.** If identical results meant giving up optimised code, the approach would be too slow to use.

**Method, step by step.**

1. Dump every intermediate of the normative decode from differently compiled builds.
2. Compare them exactly with sha256 and a structural diff, and inspect the disassembly.
3. Cover three binaries on two models, then ten opt-level and target-cpu cells.

**Method as recorded.** Every intermediate of the normative decode was dumped from differently compiled builds and compared exactly (sha256 plus a structural diff), with disassembly analysis. Core test: three x86_64 binaries (baseline; target-cpu=native with AVX2 on an i5-10210U; target-cpu=native SSE-only on a Celeron N4020) on SmolLM2-135M and Qwen2.5-0.5B. Extension: ten opt-level x target-cpu cells on SmolLM2-135M, x86_64. The same document later extends this to 20 cells across x86_64 and aarch64 in CI (E31). All with rustc 1.98.0. Run by us.

**Results (exact, sourced).**

- On the x86_64 builds tested, the optimiser vectorised the code (hundreds of AVX2 instructions) and the dumped intermediates did not change.
  - Source quote: `turns out to be **no**: the optimizer may vectorize, and does, and the bits do not move.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E29_OPTIMIZER_INVARIANCE.md
- Ten distinct x86_64 binaries (opt-level 0,1,2,3,s x generic/native) on SmolLM2-135M produced one identical 51,750,154-byte dump, with zero FMA instructions.
  - Source quote: `**Ten distinct binaries. One dump.**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E29_OPTIMIZER_INVARIANCE.md

**What it does NOT show.** A second compiler (one rustc version throughout), other flags, or why: the mechanism explanation was later corrected in E39.

**Scope and caveats, as recorded.**

- Core test: two machines (penguin, a ChromeOS Crostini VM, and a bare-metal Celeron box), same glibc, one rustc version (1.98.0, same LLVM). It is not a second-compiler test.
- The ten-cell opt-level sweep was SmolLM2-135M only, x86_64, run locally. At opt-level 0 the arithmetic kernels were not vectorised (the 147 ymm instructions there are in tokenizer/allocator code), so the informative cells are opt-level 1/2/3/s with native.
- Scope is limited: six prompts, longest context 64 generated tokens, ASCII only; flags outside opt-level, target-cpu, lto, codegen-units and profile-use are untested.
- The source later adds an aarch64 half (E31): 20 cells over x86_64 and aarch64 on GitHub-hosted runners, same dump. Same rustc. The earlier 'x86_64 only' caveat applies to the ten-cell sweep, not to the whole document.
- The document's mechanism explanation about subnormals/FTZ was later corrected in E39 (per E39, conclusions survive but the stated reason was wrong).
- Run by us; no unaffiliated reproduction. No timing claims.

**Outcome.** Positive (the check worked as expected, within the stated scope).

**What we learned.** Optimisation was not the enemy for this decode. The pinned order of operations is preserved in the emitted code, so builds with very different vector instruction counts produced identical bytes. This is measured on one compiler version and on the tested models and prompts.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E29_OPTIMIZER_INVARIANCE.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E39_FTZ_IS_NOT_WHERE_WE_SAID.md

Read the page and E39 (links above).

<a id="lab-ftz-reach-e35-e40"></a>

### E35 to E40: does the flush-to-zero rule ever matter? (after two wrong explanations)

*Date: 2026-09-09 | Outcome: Null (no effect found, or nothing yet to report) | Run by us; no unaffiliated reproduction.*

**Question.** Does one obscure rule about tiny numbers ever change a real AI output, and how sure can we be?

**Why it matters.** One obscure rule about tiny numbers is pinned in the spec. If it never matters, is it needed?

**Method, step by step.**

1. Count how often tiny values arise (E35, E38).
2. Analyse exp exhaustively over 2^32 inputs (E39).
3. Classify every reduction and RMSNorm intermediate (E40).

**Method as recorded.** Counting instruments on six prompts (E35); 20 cells on both models including non-ASCII prompts and 256-token decodes (E38); exhaustive analysis of exp over 2^32 inputs (E39); then classification of every reduction and RMSNorm intermediate (E40). Run by us; corrections recorded as errata E-10 and E-12.

**Results (exact, sourced).**

- E35: zero of 21,248,280 exp evaluations reached the band it studied (a band later shown not to be where the flush rule acts).
  - Source quote: `Zero of 21,248,280 `exp_pinned` evaluations across six prompts`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E35_DENORMAL_REACH.md
- E38's wider sweep found 2 arguments in that band on one long decode (Qwen2.5-0.5B, 256 tokens); the digest did not move.
  - Source quote: `with **2** of that cell's 22,626,240 arguments inside`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E35_DENORMAL_REACH.md
- E39: the mechanism we had given in four places was wrong; the conclusions survive, the reason did not.
  - Source quote: `the mechanism claim in E29, E35, E38 and erratum E-10 is wrong`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E39_FTZ_IS_NOT_WHERE_WE_SAID.md
- The claim that a denormal arises in a real decode was withdrawn.
  - Source quote: `is **withdrawn**.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/CHANGELOG.md
- E40 classified 562,531,070,920 intermediates across both pinned checkpoints; none was subnormal.
  - Source quote: `**562,531,070,920** classified`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E40_MATVEC_RMSNORM_REACH.md
- No weight operand in either model is subnormal.
  - Source quote: `**0 of 628,547,776 weight operands across both §0 models are subnormal**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E40_MATVEC_RMSNORM_REACH.md
- Conclusion: on the normative vector the rule does not affect the digest.
  - Source quote: `On the normative vector, §1.3's FTZ/DAZ is not digest-relevant.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E40_MATVEC_RMSNORM_REACH.md

**What it does NOT show.** That the rule is unnecessary in general: on constructed inputs it can change bits in the softmax division step. The finding holds for the two pinned checkpoints and the stated prompts only.

**Scope and caveats, as recorded.**

- Read the four documents in order; two of our own mechanism claims were retracted, while the measurements stood.
- Holds for the two pinned checkpoints and the stated prompts only.
- Run by us; no unaffiliated reproduction.
- E39 shows the flush rule can change bits in the softmax division step on constructed inputs; the finding is only that it did not on the normative vector.
- E40 reports a defect in E39's own counting instrument, found by a control and fixed; the source states it could not bite at that call site.
- The 2-argument E38 finding was in a band that E39 later showed is independent of the flush rule.

**Outcome.** Null (no effect found, or nothing yet to report).

**What we learned.** We never found a case where the flush rule changes the digest. The explanations we first gave for why were wrong, and we published the corrections next to the exhaustive count that replaced them.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E35_DENORMAL_REACH.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E38_REACH_SWEEP.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E39_FTZ_IS_NOT_WHERE_WE_SAID.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E40_MATVEC_RMSNORM_REACH.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/CHANGELOG.md

Read the four pages in order and the CHANGELOG (links above).

<a id="lab-e41-detokenization-gap"></a>

### E41: the spec pins how text becomes tokens, but not how tokens become text

*Date: 2026-09-10 | Outcome: Negative (the claim or approach failed, or we retracted it) | Run by us; no unaffiliated reproduction.*

**Question.** Could two certified programs agree on every number in a receipt yet disagree on what it says?

**Why it matters.** A receipt is read by people. If two conforming programs can print different text for the same digests, the receipt's meaning is not pinned.

**Method, step by step.**

1. Read the spec against the tokenizers of the two named checkpoints.
2. Count vocabulary entries and output indices where turning ids back into text is ambiguous.
3. Probe with small Rust examples.

**Method as recorded.** Read CIS-2 spec v0.3b against the tokenizers of the two checkpoints it names (SmolLM2-135M and Qwen2.5-0.5B) and counted where turning ids back into text is ambiguous. Probes were Rust examples run on one host (Debian 13, x86_64 VM). Run by us.

**Results (exact, sourced).**

- Two conforming implementations can disagree on a receipt's text.
  - Source quote: `two conforming implementations can disagree about what a receipt says while agreeing on every digest in it.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md
- 313 of SmolLM2's 49,152 vocabulary entries are not valid UTF-8 on their own.
  - Source quote: `**313** of SmolLM2's 49,152 vocab entries are not valid UTF-8 alone (0.64 %)`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md
- 271 of Qwen's 151,936 output indices map to no string in the tokenizer files.
  - Source quote: `**271** of Qwen's 151,936 logit indices are in neither `model.vocab` nor `added_tokens``
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md
- All 17 of SmolLM2's special tokens decode to text that re-encodes to different ids, so a rendered control token cannot be told from text spelling it.
  - Source quote: `**17** of 17 SmolLM2 `added_tokens` decode to text that re-encodes to *different* ids`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md

**What it does NOT show.** That any real receipt was misread, that other tokenizers behave the same, or that it affects conforming runs on Qwen.

**Scope and caveats, as recorded.**

- A gap in our spec (v0.3b), not a defect in the checkpoints; recorded as erratum E-14.
- Two checkpoints only; the counts are properties of those artifacts, not of tokenizers in general.
- The 271 unmapped Qwen ids did not win the argmax on one prompt over 16 decode steps (untriggered on this vector, not shown impossible); no search over prompts was run.
- Qwen's tokenizer.json is refused by the spec's conforming path, so the Qwen gap does not affect conforming runs.
- No survey of other inference specifications; no claim the gap is unusual.
- Run by us on one machine; no unaffiliated reproduction.

**Outcome.** Negative (the claim or approach failed, or we retracted it).

**What we learned.** Matching digests is not the same as matching meaning. The missing piece is a text-level definition; whether v0.4 specifies detokenization or declares it out of scope is a spec-owner decision.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E41_DETOKENIZATION_IS_UNSPECIFIED.md

Read the page (link above).

<a id="lab-ev1-mini-eval"></a>

### ev-1: a 160-item mini evaluation on the pinned 135M model

*Date: 2026-09-23 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** Can a tiny model be evaluated in a way anyone can repeat exactly, and what does it actually score?

**Why it matters.** Before measuring big claims we wanted a small evaluation anyone can repeat bit for bit.

**Method, step by step.**

1. Assemble 160 items in four categories.
2. Run them through the repository's reference binary on SmolLM2-135M, fp32, greedy.
3. Score with simple substring and refusal-marker heuristics.
4. Run twice and compare digests.

**Method as recorded.** 160 items in four categories (60 truthfulness sampled from TruthfulQA, 20 self-consistency, 60 tool-use arithmetic-completion proxy, 20 refusal probes) on SmolLM2-135M base (fp32, greedy) through the repo's own cis2_ref reference binary. Heuristic substring and refusal-marker scoring. Run by us on a single host. This is a substitute for the originally intended 2B model, which is not in this repo.

**Results (exact, sourced).**

- Truthfulness: 3 of 60 passed (0.05), by verbatim-substring heuristic.
  - Source quote: `| `truthfulness` | 60 | 3 | 0.05 |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md
- Refusal probes: 10 of 20 passed (0.5). The source says this sits at chance and was not broken out further.
  - Source quote: `| `refusal` | 20 | 10 | 0.5 |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md
- Tool-use proxy (arithmetic completion, not tool-call format): 5 of 60 passed.
  - Source quote: `| `tool_use` | 60 | 5 | 0.0833... |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md
- Self-consistency: 20 of 20 items produced identical run1/run2 digests within the same process on one host. A separate cross-process rerun log exists. No second-host verify was run.
  - Source quote: `| `self_consistency` | 20 | 20 | 1.0 |`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md
- The committed summary.json matches the four category numbers above.
  - Source quote: `"truthfulness": {       "n_items": 60,       "n_pass": 3,`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/eval/results/summary.json

**What it does NOT show.** Anything about a 2B or instruction-tuned model, safety, or other machines. The second-host verify was not run.

**Scope and caveats, as recorded.**

- A non-instruction-tuned 135M base model; truthfulness and tool-use scores are near the floor with weak heuristic scoring.
- Model substitution: this is NOT the 2B model; no claim is made about any 2B-scale or instruction-tuned model.
- Refusal items are narrow, non-operational probes written by us; refusal 10/20 is at chance and is not a safety measurement.
- tool_use is arithmetic completion, not tool-call-format correctness.
- Single host. The standalone --mode verify pass on a second machine has NOT been run, so there is no cross-host claim.
- The point is repeatability, not accuracy.
- Run by us; no unaffiliated reproduction.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** The model scores poorly but repeats exactly on one machine. We report the poor accuracy alongside the perfect same-host repeatability. Cross-host verification is still open.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/results/2026-09-22-ev1-mini-eval-kit.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/eval/results/summary.json

Read the page and the committed summary.json (links above).

<a id="lab-test-standard-ledger"></a>

### Our test standard and the public experiment ledger

*Date: 2026-10-12 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** How can an outsider tell that a lab didn't tune its results after the fact, rewrite them later, or quietly drop the failures?

**Why it matters.** Results are only as credible as the process behind them.

**Method, step by step.**

1. Write the pass mark before the run.
2. Publish a salted, hash-chained fingerprint of the private register.
3. Number every defect as an erratum.
4. Remove numbers that have no provenance.

**Method as recorded.** Stated practices in public files: (1) pre-registration, a pass mark written before the run, then a verdict; (2) a public salted, hash-chained fingerprint ledger of the private register, with a verify_ledger.py script and an OpenTimestamps proof file (LEDGER.tsv.ots); (3) no timing or throughput numbers in the spec repo; (4) provenance on every number; (5) defects recorded as numbered errata in CHANGELOG.md, and pinned digests do not move silently; (6) mismatches are welcomed as results. The standard is stated and applied by us, not audited by an outside party. All six URLs returned HTTP 200 unauthenticated (github.com and raw.githubusercontent.com) on 2026-10-12.

**Results (exact, sourced).**

- The ledger covers 84 registered experiments, 65 with a verdict; 161 of 235 lines are backfill (ledger/README.md as of 2026-10-15).
  - Source quote: `At the time of this export the ledger holds 235 lines. They cover 84 registered experiments, and 65 of them have a verdict line. 161 of the 235 lines are marked backfill.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md
- The ledger states what it cannot prove.
  - Source quote: `It cannot show when an experiment ran. A lab could run an experiment in private, look at the result, and then publish a pass mark.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md
- The start rule is a promise the page itself cannot check.
  - Source quote: `That rule is a promise. This page cannot check it.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md
- Provenance on every number, or the number is removed.
  - Source quote: `A number with no provenance gets removed rather than trusted.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md
- Pinned digests do not move silently.
  - Source quote: `The rule is that goldens do not move silently: if an erratum changes a pinned digest, the change, the cause and the new value all land in the same commit as the version bump.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md
- No unqualified superlatives.
  - Source quote: `**No unqualified superlatives.**`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md
- A mismatch is a result.
  - Source quote: `Open the PR whether your digests match or not. A mismatch is a result.`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md

**What it does NOT show.** That we always followed the standard; no outsider has audited it.

**Scope and caveats, as recorded.**

- Stated and applied by us; no unaffiliated audit of whether practice always matched the statement.
- 161 of 235 ledger lines are backfill and prove existence only from their publication date; backfill lines show no order of writing.
- The ledger shows counts and line kinds, not what was tested or found.
- The ledger count is a snapshot and will grow.
- The ledger cannot show when an experiment ran; the rule that a run starts only after its bar line is public applies from the day of publication on, with exceptions marked start-unanchored.
- The ledger chain verification was not re-run by this verifier; the earlier claim of an unauthenticated-clone verification is removed from the method text.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** We publish how we test, including what the method cannot prove, and we correct our own published claims through numbered errata.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/LEDGER.tsv
- https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/verify_ledger.py
- https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/CHANGELOG.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/E15m_PREREG.md

Read the ledger README, LEDGER.tsv and verify_ledger.py, then CONTRIBUTING.md and CHANGELOG.md (links above). We did not re-run the chain verification for this page.

<a id="lab-hall-of-divergence"></a>

### Open challenge: the Hall of Divergence

*Date: 2026-09-22 | Outcome: Null (no effect found, or nothing yet to report) | Run by us; no unaffiliated reproduction.*

**Question.** Has anyone outside the lab reproduced these results, or broken them?

**Why it matters.** Everything on this site was run by us. The honest next step is for others to run it.

**Method, step by step.**

1. Publish a table for verified reproductions and divergences.
2. List only runs with a full log.
3. Offer credit only, no cash or prize.

**Method as recorded.** A public table of verified reproductions and verified divergences for the CIS-2 spec (v0.3b). Credit only, no cash or prize. Only runs with a full log are listed. Reporters can also open a clean-room implementation PR or a spec-defect issue (CONTRIBUTING.md).

**Results (exact, sourced).**

- Every listed reproduction is our own run (two internal rows, 2026-09-22, own machines: Intel i5-5200U with AVX2 and Intel Celeron N4020 scalar, each 9 passed / 0 failed). No third-party reproduction is listed.
  - Source quote: `The two rows above are internal Aefinity AI runs, not third-party reproductions`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/HALL-OF-DIVERGENCE.md
- No divergence has been reported as of this check (2026-10-12).
  - Source quote: `*No divergence reported yet.*`
  - Source: https://github.com/Aefinity-AI/cis2-spec/blob/main/HALL-OF-DIVERGENCE.md

**What it does NOT show.** Anything about whether outsiders will succeed. Our own two rows only seed the table's format.

**Scope and caveats, as recorded.**

- A standing challenge, not a completed experiment.
- No unaffiliated reproduction is recorded.
- The two internal rows are run by us on our own machines (Debian 13, Linux 6.12.94); the source says they only seed the table's format.
- The logs for both internal rows are not committed to the public repo; the page says a public log commit is a follow-up.
- The quote wraps across a line break in the source (whitespace only).

**Outcome.** Null (no effect found, or nothing yet to report).

**What we learned.** As of 2026-10-12 no one outside the lab has reproduced or broken the CIS-2 results, and the page says so plainly. The only listed runs are our own, and their logs are not yet public.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/cis2-spec/blob/main/HALL-OF-DIVERGENCE.md
- https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md

Follow CONTRIBUTING.md to open a PR or issue. To reproduce, use the command under CIS-2 above.

<a id="lab-ranger-mock-run"></a>

### RANGER mock run: low-bit quantization ideas tested on synthetic tensors

*Date: 2026-07-14 | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** Do popular tricks for shrinking AI models to very few bits actually work, when tested where they can fail?

**Why it matters.** Low-bit compression ideas often look good in prose. We tested them where they could fail.

**Method, step by step.**

1. Build synthetic tensors with documented outlier patterns, fixed seed 20260714.
2. Run tests E0 to E5 plus a follow-up E6, pure numpy.
3. Rebuild any test that did not compute its target.

**Method as recorded.** Pure numpy, fixed seed 20260714, no GPU, no real model; tests E0 to E5 (plus an E6 follow-up) on engineered tensors reproducing documented LLM outlier pathologies (massive-activation channels, attention sinks, super-weights). Run by us.

**Results (exact, sourced).**

- On synthetic tensors, bits saved per width doubling came out at -0.60 against a predicted -0.50 (the file labels this a pass; it came only after the author rebuilt a first test that was not computing the target).
  - Source quote: `**−0.60 bits per 2× width** (predicted −0.50)`
  - Source: https://github.com/Aefinity-AI/ranger/blob/main/research/experiments/RESULTS.md
- Falsified sub-hypothesis: on synthetic tensors, rotation helps at 4-bit (1.23x) but is slightly worse than plain per-token quantization at 3- and 2-bit (0.92x).
  - Source quote: `wins at **W4A4 (1.23×)** but is slightly *worse* than plain per-token quant at W3A3 and W2A2 (0.92×)`
  - Source: https://github.com/Aefinity-AI/ranger/blob/main/research/experiments/RESULTS.md
- In the first combined test, rotation smeared the super-weights, so protecting the top rotated weights in sparse form failed. The fix was to split them off before rotating.
  - Source quote: `rotation delocalizes the super-weights`
  - Source: https://github.com/Aefinity-AI/ranger/blob/main/research/experiments/RESULTS.md

**What it does NOT show.** Real-model quality, quantization-aware training, or outlier patterns beyond the hand-set ones.

**Scope and caveats, as recorded.**

- Synthetic tensors, not a real model; tests mechanisms only, not end-to-end LLM quality, per the file's own limitations section.
- Outlier model (gain, count, sink strength) is hand-set; real distributions vary by model family.
- No quantization-aware training loop was run.
- The author states the first width test was wrong (it did not compute the target) and rebuilt it; the combined-stack test also failed at v1 and was redesigned.
- A follow-up test (E6, same file) found rotation and width are largely redundant for outliers: rotation adds only +0.1 dB on top of width. This corrects an earlier theory claim, and its design also needed two redesigns.
- The file's 'below ~3 bits you need QAT' remark rests on an outside paper (ParetoQ); it was not tested here.
- Run by us; no unaffiliated reproduction.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** On synthetic data, one sub-hypothesis was falsified and two design constraints emerged: rotate only after splitting off the sparse outliers, and rotation helps 4-bit activations but not below 4 bits. A later test showed width and rotation overlap on outliers. These are mechanism-level findings, not claims about real models.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/ranger/blob/main/research/experiments/RESULTS.md

Read the results file (link above). It is pure numpy with a fixed seed.

<a id="lab-ranger-phase1"></a>

### RANGER Phase 1: the quantization ideas on real models (SmolLM2-135M, Qwen3-0.6B)

*Date: undated in the source | Outcome: Mixed (some parts held, some did not, or we corrected ourselves) | Run by us; no unaffiliated reproduction.*

**Question.** Do those shrinking tricks survive on real pretrained models, and was our earlier null result even valid?

**Why it matters.** Synthetic results do not count until they survive on real models.

**Method, step by step.**

1. Measure perplexity on a WikiText-2 slice for SmolLM2-135M, replicate on Qwen3-0.6B.
2. Fix predictions and kill gates before each run; claim effects only above 3x run noise.
3. Re-test small effects on disjoint slices.

**Method as recorded.** Teacher-forced perplexity on non-overlapping ctx-1024 windows of a 16,384-token WikiText-2 slice (SmolLM2-135M); Qwen3-0.6B replication at 8,192 tokens, ctx 512, so only within-model deltas compare. CPU-only 6 GB VM. Predictions and kill gates fixed before each run; effects claimed only above 3x the ~0.05 PPL run noise. A confirmation pass on disjoint slices re-tested the small effects. Run by us.

**Results (exact, sourced).**

- Our earlier E7 null result was retracted as an artifact of how it was built; nothing about super-weight protection can be concluded from E7.
  - Source quote: `E7's null result was an artifact by construction — retract it.`
  - Source: https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md
- On SmolLM2-135M (fp32), 4-bit per-token activation quantization collapses perplexity from 16.14 to 13,773; a folded rotation sandwich recovers 92.3% of the log-PPL collapse, leaving PPL at 27.11 (still above the 16.14 baseline). On Qwen3-0.6B the recovery was 92.5% (34.23 to 146,845 collapse). Fake-quant is an upper bound on deployable A4.
  - Source quote: `A4 per-token quantization collapses PPL 16.14 → 13,773; a per-linear folded rotation sandwich recovers **92.3%** of the log-PPL collapse (→ 27.11)`
  - Source: https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md
- Refuted: the 'skip the rotation' upgrade. Static exemption of 8 census channels recovered only 59.1% at 135M (25% with activation-measured channels at 0.6B; the census-derived set did nothing on Qwen) versus 92%+ for rotation.
  - Source quote: `Pillar 1's "skip the rotation" upgrade is refuted`
  - Source: https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md
- Null at 135M: no super-weight lever over an honest g=128 4-bit baseline, and MSE clipping hurts there (24.896 to 26.917). The 'rescues 0.38 of clip damage' sub-result was refuted as noise on a disjoint slice (-0.015). At 0.6B, clipping helps (48.06 to 41.82) and the coordinate increment is small but real (+0.45, then +0.24).
  - Source quote: `At 135M there is no exploitable super-weight lever over an honest W4 baseline — and MSE-clipping actively hurts.`
  - Source: https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md
- Across models, the overlap between the weight census and activation-outlier channels fell from 6/10 (SmolLM2-135M) to 2/10 (Qwen3-0.6B); the census still found the single top channel on both.
  - Source quote: `Census→activation overlap collapses: 6/10 → 2/10.`
  - Source: https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md

**What it does NOT show.** Parity with the unquantized model (recovery is of the collapse, not full parity), larger models, or deployable int4 (fake-quant is an upper bound).

**Scope and caveats, as recorded.**

- Two small models, CPU-only, one WikiText-2 slice (plus one disjoint confirmation slice each); Qwen absolute perplexity is chat-tuned (34.23 bf16) and not comparable to SmolLM2; slice-to-slice magnitude varies a lot, direction is the replicated quantity.
- Per-token dynamic fake-quant upper-bounds deployable 4-bit activations; rotation used a QR orthogonal, not a fast Hadamard; Qwen rotation arm ran in bf16 with storeback rounding noted.
- Super-weight effects are documented in the literature from about 1B parameters up; scale-gated pending larger runs.
- Rotation sandwich W4A4 end-to-end point is 53.868 PPL vs 16.14 baseline: recovery is of the collapse, not full parity.
- The source document describes itself with a superlative ordinal; do not repeat that wording publicly.
- Run by us; no unaffiliated reproduction.

**Outcome.** Mixed (some parts held, some did not, or we corrected ourselves).

**What we learned.** A prior null result was retracted publicly. Rotation recovery replicated across two architectures (92.3% and 92.5%), while the census-replaces-rotation shortcut was refuted, and a super-weight lever is null at 135M and only small at 0.6B. One of our own sub-results (0.38 rescue) was refuted by our confirmation pass.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/ranger/blob/main/research/phase1/RESULTS-phase1.md

Read the results file (link above).

<a id="lab-retraction-prochot"></a>

### Retraction: our benchmark laptop was running at about one fifth speed

*Date: 2026-08-05 | Outcome: Negative (the claim or approach failed, or we retracted it) | Run by us; no unaffiliated reproduction.*

**Question.** Were our speed measurements measuring our code, or a hidden hardware throttle?

**Why it matters.** A speed number is meaningless if the machine was secretly throttled.

**Method, step by step.**

1. Print the current core ratio against the requested ratio at boot.
2. Apply a fix, clearing bd-PROCHOT and requesting the maximum P-state.
3. Generate the same 214 tokens with two same-day builds.

**Method as recorded.** A boot-time diagnostic printed the current core ratio against the requested ratio on a Dell Inspiron 15 (i5-5200U, bare metal, no OS). Two builds made the same day, differing only by the STAGE 7 fix (clear bd-PROCHOT and request max P-state), generated the same 214 tokens with a 14.17M-parameter model. Run by us.

**Results (exact, sourced).**

- The CPU was clamped to ratio 5 of a requested 27, with PROCHOT asserted while the thermal sensor read cool.
  - Source quote: `was clamped to core ratio 5 out of a requested 27.`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md
- Every earlier number from that box (before 2026-07-29) was taken at roughly a fifth of nominal clock, and was retracted.
  - Source quote: `Every performance number we took on that box before 2026-07-29 was measured on a CPU`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md
- After the fix, cur_ratio went from 5 to 25 on 3 of 3 cold boots (one machine).
  - Source quote: `Reproduced on 3/3 cold boots.`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md
- Wall-time ratio across the two same-day builds was 3.861x, below the 5.000x the ratio change implies; output was byte-identical. Not reported as a speedup.
  - Source quote: `We are deliberately **not** reporting this as a speedup.`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md
- Published as a retraction.
  - Source quote: `this post is a retraction, not a speedup`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md
- Limitation of the before/after: no clear-only arm.
  - Source quote: `No clear-only arm.`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md

**What it does NOT show.** A speed-up, durability across suspend, or the effect of each half of the fix, since there was no clear-only arm.

**Scope and caveats, as recorded.**

- One machine (n=1 laptop, 3 cold boots); run by us; no unaffiliated reproduction.
- The fix (MSR 0x1FC bit 0) is about fifteen years old; the post cites prior art and does not claim it as new. The measurement error is the point.
- The fix stage changed two things at once (cleared bd-PROCHOT and requested the maximum P-state); no clear-only arm was run, so the ordering hypothesis is untested.
- Durability is untested: unknown whether the clear survives S3 suspend or an EC re-assert after a firmware event.
- The 3.861x vs 5.000x gap is described as a crude indicator of memory-bound work, not a measured decomposition.
- The post's tok/s column is too coarse to quote; tick counts are the instrument.

**Outcome.** Negative (the claim or approach failed, or we retracted it).

**What we learned.** Measure the machine before measuring the code. We retracted every earlier number from that box instead of reporting a speed-up.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_bd-prochot-benchmark-lie.md

Read the post (link above).

<a id="lab-soft-float-avx2"></a>

### A compiler setting silently deleted our vector instructions

*Date: 2026-08-05 | Outcome: Negative (the claim or approach failed, or we retracted it) | Run by us; no unaffiliated reproduction.*

**Question.** How can code run hundreds of times slower than its parts predict, with no error and correct output?

**Why it matters.** Code can be badly slow with no error and correct output.

**Method, step by step.**

1. Count vector instructions in the preserved shipped binary with objdump.
2. Rebuild with a hard-float target.
3. Measure ticks per token and score a pre-registered prediction.

**Method as recorded.** Counted the vector instructions in the binary actually shipped (objdump census of a preserved copy), then rebuilt with a custom hard-float target and measured ticks/token on the Dell Inspiron 15 (i5-5200U, bare metal, no OS). A pre-registered root-cause prediction was scored. Run by us.

**Results (exact, sourced).**

- Hand-written AVX2 kernels compiled to zero vector instructions; the binary ran 217 to 258 times slower than the hard-float rebuild (soft-float 1.65-1.67e9 vs hard-float 6.48-7.59e6 ticks/token).
  - Source quote: `Our hand-written AVX2 kernels compiled to zero vector instructions, and the resulting binary ran 217–258× slower than it should have.`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_uefi-soft-float-deletes-your-avx2.md
- Instruction census of the shipped (preserved, bit-identical) soft-float binary: no xmm, ymm or vfmadd instructions.
  - Source quote: `census: xmm=0 ymm=0 vfmadd=0`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_uefi-soft-float-deletes-your-avx2.md

**What it does NOT show.** A controlled benchmark; the 217 to 258 times is a ratio of ranges on one machine.

**Scope and caveats, as recorded.**

- One machine (Dell Inspiron 15, i5-5200U, bare metal, no OS); 217 to 258 times is the ratio of soft-float to hard-float ticks/token on that machine, derived from ranges (1.65e9/7.59e6 to 1.67e9/6.48e6), not a controlled benchmark.
- A debugging post-mortem tied to Rust's stock x86_64-unknown-uefi target (+soft-float).
- The first census (v1) was itself wrong because a concurrent rebuild overwrote the artifact; it was re-run on a preserved bit-identical copy and the log superseded. Conclusion unchanged.
- A pre-registered root-cause prediction was also scored, in an analysis that covers the held-back operating-system comparison; we do not link that analysis while the comparison is held back.
- Run by us; no unaffiliated reproduction.

**Outcome.** Negative (the claim or approach failed, or we retracted it).

**What we learned.** Trust the binary you ship, not the annotation you wrote. Nothing failed and nothing warned; only counting instructions in the artifact exposed it. A mechanical check (assert nonzero ymm/vfmadd count in CI) is the fix, not a benchmark.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/posts/2026-08-05_uefi-soft-float-deletes-your-avx2.md

Read the post (link above).

<a id="lab-os-cost-held-back"></a>

### What does an operating system cost? A pre-registered result we held back

*Date: 2026-08-01 | Outcome: Held back (a pre-registered rule withholds the result until its cause is understood) | Run by us; no unaffiliated reproduction.*

**Question.** Is running AI with no operating system at all faster than a minimal Linux on the same laptop?

**Why it matters.** A surprising result should be explained before it is published.

**Method, step by step.**

1. Pre-register a comparison of a no-OS build against a minimal Linux on one laptop.
2. Run it. The first result surprised us.
3. Apply the pre-registered rule: a surprising result is not published until its cause is understood.
4. Look for the mechanism. We found one contributing cause in our own build (soft-float); the question remains open.

**Method as recorded.** A pre-registered comparison of a no-OS build against a minimal Linux on one laptop (Dell Inspiron 15, i5-5200U), using paired boots on a fixed set of prompts. Run by us.

**Results (exact, sourced).** Held back. No numbers from this comparison are published. They will be published when the mechanism is understood.

**What it does NOT show.** What an operating system costs, or any claim about speed.

**Scope and caveats, as recorded.**

- One laptop (Dell Inspiron 15, i5-5200U); run by us.
- The first result surprised us. Our pre-registered rule says a surprising result is not published until its cause is understood, so the result is held back.
- We found one contributing cause in our own build (soft-float). It does not settle the question, which remains open.
- No numbers from this comparison are published. They will be published when the mechanism is understood.
- Run by us; no unaffiliated reproduction.

**Outcome.** Held back (a pre-registered rule withholds the result until its cause is understood).

**What we learned.** A surprising result was held back by a rule we had written in advance. We found one contributing cause in our own build (soft-float), but the question remains open; the numbers will be published when the mechanism is understood.

**Check it yourself.** There is nothing to check yet: the numbers are held back until the mechanism is understood. The related soft-float lab is public: [A compiler setting silently deleted our vector instructions](#lab-soft-float-avx2).

<a id="lab-lut-kernel-retraction"></a>

### The '16% slower' lookup-table kernel claim, retracted

*Date: 2026-07-30 | Outcome: Negative (the claim or approach failed, or we retracted it) | Run by us; no unaffiliated reproduction.*

**Question.** Does a performance number copied from a source comment hold up when actually measured?

**Why it matters.** Numbers that were never measured spread easily.

**Method, step by step.**

1. Put all arms in one binary and interleave them in one loop on identical packed weights.
2. Make three logged runs.
3. Compare the f32 arm and the pshufb arm.

**Method as recorded.** All arms in one binary, interleaved in one loop, on identical packed weights; three logged runs on a Chromebook crosvm guest (i5-10210U), git_head a249b2c. Run by us.

**Results (exact, sourced).**

- The earlier '16% slower' claim does not reproduce: the pshufb arm was bimodal (8.2 vs ~11.2 GMAC/s effective, a 36% swing) while the f32 arm moved only 4.7%. In the faster mode pshufb was 1.19-1.21x faster than the f32 matvec kernel; in run 1 it lost at 1.09x, so the ordering flips between runs.
  - Source quote: `"16% SLOWER" is NOT REPRODUCIBLE.`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/hardware_logs/lut_mpgemm_ab_findings_2026-07-30.md
- The decision to reject the kernel still stands, on different grounds. The memory-traffic ratio is derived arithmetic (1.670x per token), not a measurement. The derivation uses prior-log figures to reach a projected ~28% slower decode in the bandwidth-bound regime.
  - Source quote: `The rejection verdict STANDS, on memory-traffic grounds, not kernel throughput.`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/hardware_logs/lut_mpgemm_ab_findings_2026-07-30.md

**What it does NOT show.** End-to-end decode speed (the 28% figure is derived) or any VNNI machine.

**Scope and caveats, as recorded.**

- Three logged runs on a virtualised machine (crosvm guest, i5-10210U); the pshufb arm was bimodal. A fourth spot-run was unlogged and the source says it substantiates nothing.
- The bimodality explanation (working set straddling the 6 MB LLC) is an untested hypothesis in the source.
- The original number came from a source-file comment, which our own provenance rule does not admit; the bench had never measured the f32 arm it claimed to lose to.
- The benchmarked pshufb kernel is numerically incorrect (madd pairing artifact, flagged in-source); repairing it would erode the faster-mode gain.
- The 28% slower figure is a derivation from earlier logs, not a measured end-to-end result.
- No VNNI (vpdpbusd) machine was measured; that revisit is still open.
- Run by us; no unaffiliated reproduction.

**Outcome.** Negative (the claim or approach failed, or we retracted it).

**What we learned.** A number cited from a source file but never measured was wrong in the form claimed. The conclusion survived, for a different reason.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/hardware_logs/lut_mpgemm_ab_findings_2026-07-30.md

Read the findings (link above).

<a id="lab-fabricated-metrics-audit"></a>

### Audit of our own removed code: benchmark lines that measured nothing

*Date: 2026-07-10 | Outcome: Negative (the claim or approach failed, or we retracted it) | Run by us; no unaffiliated reproduction.*

**Question.** Did an earlier version of our software print performance numbers it never measured?

**Why it matters.** This is where our provenance rule came from.

**Method, step by step.**

1. Review the print statements of a deleted crate preserved in git history.
2. Check whether they take format arguments.

**Method as recorded.** Review of the print statements in a deleted crate (antigravity-aegis, removed 2026-07-10) whose code is preserved in git history at commit 5b69327. Run by us.

**Results (exact, sourced).**

- The printed benchmark lines in the removed crate were fixed string literals, not measurements.
  - Source quote: `All are `println!` calls with **no format arguments** — string literals asserting measurements that were never taken.`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/EVIDENCE_fabricated_metrics.md

**What it does NOT show.** Anything about current code; no experiment was run.

**Scope and caveats, as recorded.**

- An audit of our own old code; no experiment was run.
- The quote is verbatim, but it wraps across two lines in the source file.
- The source also says the crate did not compile (9 errors), so the printed numbers could not have been produced even in principle.
- The document quotes 7 lines from main.rs, including the three [BENCHMARK] lines (TTFT, TPS, Peak RSS). It is a self-review with no independent reproduction.

**Outcome.** Negative (the claim or approach failed, or we retracted it).

**What we learned.** Every published number needs a machine, a log and a source behind it. This audit is where that rule came from.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/EVIDENCE_fabricated_metrics.md

Read the audit (link above); the commit it cites is 5b69327.

<a id="lab-es1-trit-census"></a>

### E-S1: how far can a ternary 2B model be compressed without loss?

*Date: 2026-09-04 | Outcome: Null (no effect found, or nothing yet to report) | Run by us; no unaffiliated reproduction.*

**Question.** Can a 1.58-bit AI model be squeezed much smaller without losing anything?

**Why it matters.** Could a ternary model be made much smaller without losing anything?

**Method, step by step.**

1. Count all 2,084,044,800 weights in the 210 body tensors.
2. Code them with rANS, xz and zstd.
3. Verify the round trip byte for byte.

**Method as recorded.** Census and lossless coding (rANS, xz, zstd) of all 2,084,044,800 weights in the 210 body tensors of the BitNet-b1.58-2B engine model file aegis_pruned_model.safetensors, with a byte-exact round trip, on one Dell i5-5200U. Counts and byte sizes only. Run by us.

**Results (exact, sourced).**

- The best of the lossless coders tested (zstd -19 on packed bytes) reached 1.532 bits per weight, 399,113,010 bytes, against 2.000 bits per weight for the engine's current packing.
  - Source quote: `| **zstd -19 on packed bytes** | **1.532** | **399,113,010** |`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/experiments/ES1_TRIT_CENSUS_RESULTS.md
- The round trip was byte-exact on every tensor, with 0 mismatches.
  - Source quote: `Byte-exact round-trip on every tensor: **0 mismatches**.`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/experiments/ES1_TRIT_CENSUS_RESULTS.md
- The trits are near-uniform, so the weights compress only a little.
  - Source quote: `Pretrained ternary weights do not compress much`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/experiments/ES1_TRIT_CENSUS_RESULTS.md

**What it does NOT show.** Anything about coding speed or changes to the model.

**Scope and caveats, as recorded.**

- One model, one machine (Dell i5-5200U).
- Against ideal trit packing (1.600 bits per weight) the saving is about 4%. The 23% saving against the engine's file comes only from that file spending 2 bits per trit.
- Generic zstd beat the one-trit-context rANS coder on the gate and up projections. The source says this is worth about 1% overall and that a row/column-adaptive model is the only remaining lossless headroom. That was not tested here.
- Going below this level needs model changes (sparsity), which this lab does not make.
- Counts and byte sizes only. Coding speed was not measured.
- Run by us; no unaffiliated reproduction.

**Outcome.** Null (no effect found, or nothing yet to report).

**What we learned.** Pretrained ternary weights are close to uniform, so lossless coding gains little. Real savings would need changes to the model, not a better coder.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/alice-aegis/blob/main/docs/experiments/ES1_TRIT_CENSUS_RESULTS.md

Read the results (link above).

<a id="lab-refuted-literature-claims"></a>

### Claims from the literature that failed when we ran them

*Date: undated in the source | Outcome: Negative (the claim or approach failed, or we retracted it) | Run by us; no unaffiliated reproduction.*

**Question.** Do published recipes for training small ternary models work as claimed on ordinary hardware?

**Why it matters.** Recipes repeated in papers and blog posts can fail on ordinary hardware.

**Method, step by step.**

1. Record each cited recipe as refuted, corrected or surviving.
2. Run it on our target box where we can.
3. Where we cannot, say so and cite the requirement.

**Method as recorded.** Our research notes record each cited recipe as refuted, corrected or surviving. The soft-prompt recipe was refuted by execution on our own target machine. The T4 claim was refuted by reading the requirements stated in a cited source, and we did not run it on a T4. Run by us.

**Results (exact, sourced).**

- A stock Hugging Face transformers recipe (AutoBitLinear, online_quant=False) for training soft prompts on the Falcon-E checkpoint gave outputs wrong by about 300 times on one real layer (layer-0 q_proj), as measured by us on our target box.
  - Source quote: `so the stock recipe's outputs are wrong by weight_scale^2 (~301.9x measured on real layer-0 q_proj)`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/program/model-lab/refuted_claims.md
- The claim that stock onebitllms runs on a free Kaggle/Colab T4 in 2-5 hours is marked REFUTED in our notes. The basis is a documented hardware requirement (Triton >=3.3 needs compute capability 8.0+, and the T4 is sm_75). We did not run it on a T4. The notes say the path may survive only in an unverified older-library environment.
  - Source quote: `Triton >=3.3 (bundled with torch >=2.7) requires NVIDIA CC 8.0+ and dropped Turing`
  - Source: https://github.com/Aefinity-AI/alice-aegis/blob/main/program/model-lab/refuted_claims.md

**What it does NOT show.** That the recipes fail everywhere. This is our environment and one set of library versions.

**Scope and caveats, as recorded.**

- Our environment and one set of library versions.
- Entries are our own research notes made public.
- Run by us; no unaffiliated reproduction.
- The soft-prompt result is one measurement on one layer of one checkpoint (Falcon-E). The source says the recipe was salvaged in weaker form and requires a step-0 logit-parity gate.
- The T4 refutation rests on the documented requirement in a cited source, not on our own run. The source says the path survives only behind an UNVERIFIED torch<=2.6 / triton-3.2 / pinned-TRL environment.
- The source notes there is no independent replication of the soft-prompt path anywhere.

**Outcome.** Negative (the claim or approach failed, or we retracted it).

**What we learned.** Several widely repeated recipe claims failed when we checked them, so we keep a public list of what failed. For each claim, the list says whether we ran it ourselves or checked it against a source's stated requirements.

**Check it yourself.** Public pages:

- https://github.com/Aefinity-AI/alice-aegis/blob/main/program/model-lab/refuted_claims.md

Read the notes (link above).

## Our test standard

This page describes the protocol as our public repository documents it. It is stated and applied by us and has not been audited by an outside party.

**The practices**

- Pre-registration: a pass mark is written before the run, then a verdict is recorded.
- A public, salted, hash-chained fingerprint ledger of the private register, with a `verify_ledger.py` script and an OpenTimestamps proof file (`LEDGER.tsv.ots`).
- No timing or throughput numbers in the spec repository.
- Provenance on every number.
- Defects recorded as numbered errata in `CHANGELOG.md`; pinned digests do not move silently.
- Mismatches are welcomed as results.

**In the repository's own words**

- "At the time of this export the ledger holds 235 lines. They cover 84 registered experiments, and 65 of them have a verdict line. 161 of the 235 lines are marked backfill." (https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md)
- "It cannot show when an experiment ran. A lab could run an experiment in private, look at the result, and then publish a pass mark." (https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md)
- "That rule is a promise. This page cannot check it." (https://github.com/Aefinity-AI/cis2-spec/blob/main/ledger/README.md)
- "A number with no provenance gets removed rather than trusted." (https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md)
- "The rule is that goldens do not move silently: if an erratum changes a pinned digest, the change, the cause and the new value all land in the same commit as the version bump." (https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md)
- "**No unqualified superlatives.**" (https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md)
- "Open the PR whether your digests match or not. A mismatch is a result." (https://github.com/Aefinity-AI/cis2-spec/blob/main/CONTRIBUTING.md)

**What the standard cannot prove**

- Stated and applied by us; no unaffiliated audit of whether practice always matched the statement.
- 161 of 235 ledger lines are backfill and prove existence only from their publication date; backfill lines show no order of writing.
- The ledger shows counts and line kinds, not what was tested or found.
- The ledger count is a snapshot and will grow.
- The ledger cannot show when an experiment ran; the rule that a run starts only after its bar line is public applies from the day of publication on, with exceptions marked start-unanchored.
- The ledger chain verification was not re-run by this verifier; the earlier claim of an unauthenticated-clone verification is removed from the method text.

Details: [Our test standard and the public experiment ledger](#lab-test-standard-ledger); the standing challenge: [Open challenge: the Hall of Divergence](#lab-hall-of-divergence).

## What we have learned

Each lesson cites the labs it comes from. All are from our own runs, at the scopes stated in those labs.

1. **Check the computation, not just the text it produced.** Identical printed losses hid different checkpoint bytes. An altered RMSNorm order changed the digest and left the 16 tokens alone. Edited embedding rows hid from output checks that no prompt exercised. Labs: [One flipped bit in the weights: which checks notice?](#lab-bitflip-weights); [Realistic edits to the embedding table, including one hidden row](#lab-embedding-edits); [E25: the RMSNorm multiply order matters, and our spec sentence saying otherwise was false](#lab-e25-rmsnorm-order); [Ordinary logging versus replay-based receipts on one-field edits](#lab-logging-vs-receipts); [Training checkpoints across CPUs and instruction sets](#lab-training-checkpoints-cross-isa).
2. **In our fp32 tests, the pinned order of operations determined the bits.** The same order matched across the CPUs and the one GPU we tried, and a different order broke the digest; default library kernels did not match across two CPUs in training. Heavily vectorised builds matched when the order was preserved. Scope: one small model, a few machines, run by us. Labs: [Batching and precision on a Tesla T4: which shortcuts change the digest](#lab-t4-batching-precision); [E29: does the compiler's optimiser change the bits?](#lab-e29-optimizer-invariance); [CIS-2: the same AI output, bit for bit, on different machines](#lab-cis2-cross-machine-digest); [Training checkpoints across CPUs and instruction sets](#lab-training-checkpoints-cross-isa).
3. **A spot check can give a comfortable wrong answer.** 4,096 samples per binade never hit the worst points among about 8.4 million. A maximum measured on one prompt was only that prompt's maximum, and widening the sweep corrected our own published number. Labs: [E26: sin/cos at very long contexts — the sampled answer was wrong](#lab-e26-trig-range); [E28, E36, E37: every internal activation compared against an independent implementation](#lab-layer-oracle-e28-e36-e37); [E27: exp, ln and SiLU on every float32 input, and a defect in our spec](#lab-e27-exp-ln-range).
4. **Trying to break our own work finds the holes.** A mismatch exposed a spec error, a mis-filed receipt exposed a verifier hole, and exhaustive tests exposed a defect in a spec guard. Each was recorded in the open. Labs: [Clean-room reimplementations: one mismatch (from a memo), one match (from spec v0.1), one partial that exposed a spec error](#lab-cleanroom-reimplementations); [Receipt-verified agent evaluation, and the hole we found in our own verifier](#lab-receipt-verified-eval); [E24: the spec never says which Unicode version defines a letter](#lab-e24-unicode-gap); [E27: exp, ln and SiLU on every float32 input, and a defect in our spec](#lab-e27-exp-ln-range); [E41: the spec pins how text becomes tokens, but not how tokens become text](#lab-e41-detokenization-gap); [E22: which spec rules does the test vector actually exercise?](#lab-e22-necessity-matrix).
5. **Measure the machine and the shipped binary before measuring the code.** A throttled CPU and a compiler setting each invalidated speed numbers while everything appeared to work; a soft-float build explained one separate slowness and is one contributing cause in the operating-system comparison, which stays open. Labs: [Retraction: our benchmark laptop was running at about one fifth speed](#lab-retraction-prochot); [A compiler setting silently deleted our vector instructions](#lab-soft-float-avx2); [What does an operating system cost? A pre-registered result we held back](#lab-os-cost-held-back); [The '16% slower' lookup-table kernel claim, retracted](#lab-lut-kernel-retraction).
6. **A number without a measurement behind it is not a number.** Printed benchmark lines were fixed strings, a source-comment figure did not reproduce, and recipes repeated in the literature failed when we ran them. This is where our rule of provenance on every number comes from. Labs: [Audit of our own removed code: benchmark lines that measured nothing](#lab-fabricated-metrics-audit); [The '16% slower' lookup-table kernel claim, retracted](#lab-lut-kernel-retraction); [Claims from the literature that failed when we ran them](#lab-refuted-literature-claims).
7. **Our explanations were wrong more often than our measurements.** A mechanism we gave in four places was wrong while the counts stood, and one of our own null results was a vacuous edit. We now publish the correction next to the measurement. Labs: [E35 to E40: does the flush-to-zero rule ever matter? (after two wrong explanations)](#lab-ftz-reach-e35-e40); [E22: which spec rules does the test vector actually exercise?](#lab-e22-necessity-matrix); [E29: does the compiler's optimiser change the bits?](#lab-e29-optimizer-invariance).
8. **A convenience feature can hide the failure a check exists to find.** The self-check's automatic re-download would likely mask the corruption a monitor is meant to report. This was inferred, not run on corrupted weights. Labs: [Continuous validation: does a one-byte corruption get caught, and what hides it?](#lab-continuous-validation).
9. **Integrity has a cost; report it next to the claim.** 2.51 times the plain decode on one old laptop, which the source calls an upper bound, from single runs. Labs: [What receipts cost on a real agent episode](#lab-receipt-overhead).
10. **Passing a test does not mean every rule is tested.** 12 of 16 single-rule breaks were caught. The tie-break and the denormal-flush pin are protected only by inputs the vector never contains. Labs: [E22: which spec rules does the test vector actually exercise?](#lab-e22-necessity-matrix); [E35 to E40: does the flush-to-zero rule ever matter? (after two wrong explanations)](#lab-ftz-reach-e35-e40).
11. **A bar set in advance keeps us honest, and we say when it was not set in advance.** A 2 ULP bar was missed by the first fix and we kept the bar. A surprising result was held back by a rule we wrote in advance. The final sin/cos mechanism was added after a miss and was not itself pre-registered. Labs: [Sin/cos accuracy for RoPE against a pre-registered 2 ULP bar (v0.2, v0.3, v0.3b)](#lab-sincos-prereg-2ulp); [What does an operating system cost? A pre-registered result we held back](#lab-os-cost-held-back); [Batching and precision on a Tesla T4: which shortcuts change the digest](#lab-t4-batching-precision).
12. **Everything so far has been run by us.** No unaffiliated party has reproduced the results. Until one does, every claim on this site is 'reproduced by us'. Labs: [Open challenge: the Hall of Divergence](#lab-hall-of-divergence); [CIS-2: the same AI output, bit for bit, on different machines](#lab-cis2-cross-machine-digest); [Our test standard and the public experiment ledger](#lab-test-standard-ledger).

## Projects

### CIS-2

An open (Apache-2.0) specification and verifiers for bit-identical fp32 LLM inference, with public conformance vectors. Pinned vector: SmolLM2-135M, prompt 'Once upon a time', 16 greedy tokens, fp32. The conformance suite internals are not public; only the spec and vectors are.

- Specification and verifiers: https://github.com/Aefinity-AI/cis2-spec
- Spec v0.3b: https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/CIS2_SPEC_v0.3b.md
- Pinned digests: https://github.com/Aefinity-AI/cis2-spec/blob/main/EXPECTED_DIGESTS.md
- Conformance vectors: https://huggingface.co/datasets/aefinityAIINC/cis2-conformance
- Open challenge: https://github.com/Aefinity-AI/cis2-spec/blob/main/HALL-OF-DIVERGENCE.md

Reproduce it:

Reproduce the headline check with the command the repository README gives:

```
git clone https://github.com/Aefinity-AI/cis2-spec && cd cis2-spec && ./selfcheck.sh
```

The README also lists a narrower local script, `scripts/self_check.sh`, run after the same `git clone`. The README says it needs a Rust toolchain (`cargo`) and network access to download the pinned SmolLM2-135M weights.

**Limits, in the README's words:** "No unaffiliated party has reproduced it yet." It covers fp32 greedy decoding on small open models, mostly on CPU; production bf16/GPU serving is outside the spec today. It does not show that a model's answer is correct, safe or fair.

Labs: [CIS-2: the same AI output, bit for bit, on different machines](#lab-cis2-cross-machine-digest); [An NVIDIA GPU reproduces the CPU reference digest (Tesla P100)](#lab-gpu-p100-reproduces-cpu); [Batching and precision on a Tesla T4: which shortcuts change the digest](#lab-t4-batching-precision); [Clean-room reimplementations: one mismatch (from a memo), one match (from spec v0.1), one partial that exposed a spec error](#lab-cleanroom-reimplementations); [One flipped bit in the weights: which checks notice?](#lab-bitflip-weights); [Receipt-verified agent evaluation, and the hole we found in our own verifier](#lab-receipt-verified-eval); [E22: which spec rules does the test vector actually exercise?](#lab-e22-necessity-matrix); [Open challenge: the Hall of Divergence](#lab-hall-of-divergence).

### ALICE (alice-aegis)

A public repository for a bare-metal inference engine in Rust for a ternary (BitNet b1.58) transformer that boots from UEFI firmware with no operating system, plus a Linux userspace harness. Its README credits Microsoft's BitNet b1.58-2B-4T (MIT licence) for the model weights. The repository also holds our hardware logs and retractions.

- Repository: https://github.com/Aefinity-AI/alice-aegis

Labs: [Retraction: our benchmark laptop was running at about one fifth speed](#lab-retraction-prochot); [A compiler setting silently deleted our vector instructions](#lab-soft-float-avx2); [What does an operating system cost? A pre-registered result we held back](#lab-os-cost-held-back); [The '16% slower' lookup-table kernel claim, retracted](#lab-lut-kernel-retraction); [Audit of our own removed code: benchmark lines that measured nothing](#lab-fabricated-metrics-audit); [E-S1: how far can a ternary 2B model be compressed without loss?](#lab-es1-trit-census); [Claims from the literature that failed when we ran them](#lab-refuted-literature-claims).

### RANGER

Public research notes on low-bit quantisation: a synthetic mock run and a Phase 1 run on two real small models. The repository README is a title only; the public content is under `research/`.

- Repository: https://github.com/Aefinity-AI/ranger

Labs: [RANGER mock run: low-bit quantization ideas tested on synthetic tensors](#lab-ranger-mock-run); [RANGER Phase 1: the quantization ideas on real models (SmolLM2-135M, Qwen3-0.6B)](#lab-ranger-phase1).

### Elsewhere

Public profiles named on the live site: https://github.com/Aefinity-AI and https://huggingface.co/aefinityAIINC.


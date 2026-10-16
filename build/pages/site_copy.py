"""Structured copy for the site build.

Everything here is derived from content/CONTENT.md, content/labs.json or the
v2 public/pilot.html. Text is shortened only for layout; meaning is unchanged.
build.py asserts that every figure number appears in its lab's sourced text.
"""
import os
import re


SITE = "https://aefinityai.com"
EMAIL = "justin@aefinityai.com"
PHONE_DISPLAY = "409-320-1536"
PHONE_TEL = "+14093201536"
COMPANY = "AEFINITY AI INC."
CITY = "Orange, Texas"
SITE_SOURCE = "https://github.com/Aefinity-AI/aefinityai.com"
PARTNER_PATH = "https://github.com/Aefinity-AI/cis2-spec/blob/main/docs/public/Design_Partner_Adoption_Path.md"

# Desktop navigation. NAV_MORE shows in the mobile menu and the footer only.
NAV = [
    ("/alice/", "A.L.I.C.E."),
    ("/cis/", "CIS-1"),
    ("/labs/", "Labs"),
    ("/questions/", "Questions"),
    ("/standard/", "Standard"),
    ("/operations/", "Operations"),
    ("/mission/", "Mission"),
]
NAV_MORE = [
    ("/learned/", "Learned"),
    ("/projects/", "Projects"),
]
NAV_CTA = ("/contact/", "Book a briefing")
FOOT_NAV = NAV + NAV_MORE + [("/operations/how-we-run/", "How we run"), ("/contact/", "Contact"), ("/pilot", "Archived: CIS-2 replay pilot")]

# Outcome labels. Definitions are CONTENT.md's own wording.
OUTCOMES = [
    ("positive", "Positive", "The check worked as expected, within the stated scope."),
    ("mixed", "Mixed", "Some parts held, some did not, or we corrected ourselves."),
    ("negative", "Negative", "The claim or approach failed, or we retracted it."),
    ("null", "Null", "No effect found, or nothing yet to report."),
    ("held", "Held back", "A pre-registered rule withholds the result until its cause is understood."),
]

# Short chip labels for the ten hard questions (shortened from CONTENT.md headings).
QUESTION_SHORT = {
    1: "Same bits on two computers",
    2: "Graphics cards and shortcuts",
    3: "Silent weight changes",
    4: "Agent records and their cost",
    5: "Rebuilt from the written spec",
    6: "Do our tests test anything",
    7: "No tuning after the fact",
    8: "Speed numbers",
    9: "Shrinking models",
    10: "Repeatable evaluation",
}

# "How we work": each line is verbatim from CONTENT.md
# ("How to read this site" and "Our test standard").
HOW_WE_WORK = [
    ("Pass mark set in advance", "Pre-registration: a pass mark is written before the run, then a verdict is recorded."),
    ("Every number sourced", "Every number comes with its public source and a short verbatim quote."),
    ("Failures listed", "Failures, nulls, retractions and corrections of our own work are listed with the successes."),
    ("Run by us", "Every result is run by us. No unaffiliated party has reproduced any of it yet."),
]

# Home page: six labs chosen for balance (two positive, two mixed, two negative).
HOME_LABS = [
    "logging-vs-receipts",
    "bitflip-weights",
    "receipt-verified-eval",
    "e22-necessity-matrix",
    "retraction-prochot",
    "e41-detokenization-gap",
]

# Home page: lessons to feature (numbers from "What we have learned").
HOME_LESSONS = [1, 3, 5, 12]

# Machine nicknames -> hardware descriptions from the same lab. Applied to prose
# only (claims, method, steps, caveats, learned, paragraphs), never to quotes.
# Ordered: longest / most specific phrases first.
NICKNAME_PHRASES = [
    ("box1 = Intel i5-5200U (AVX2/FMA); box2 = Celeron N4020 (no AVX2/FMA), which verifies",
     "one machine is an Intel i5-5200U (AVX2/FMA); the other is a Celeron N4020 (no AVX2/FMA), which verifies"),
    ("(shown with an i5-5200U fingerprint, the box1 AVX2 row)", "(shown with an i5-5200U fingerprint, the i5-5200U AVX2 row)"),
    ("separately lists box1 with its log not published", "separately lists the i5-5200U host with its log not published"),
    ("One machine-table host (penguin)", "One machine-table host (one of our own machines)"),
    ("one host (aefinity-box)", "one host (one of our own machines)"),
    ("one host (box1)", "one host (one of our own machines)"),
    ("a single host (box1)", "a single host (one of our own machines)"),
    ("(cm-box1, i5-5200U, gcc 14.2.0)", "(an Intel i5-5200U machine, gcc 14.2.0)"),
    ("(penguin, Crostini, gcc -O2)", "(a ChromeOS Crostini VM, gcc -O2)"),
    ("(penguin, x86_64 VM)", "(an x86_64 VM)"),
    ("(penguin, a ChromeOS Crostini VM, and a bare-metal Celeron box)", "(a ChromeOS Crostini VM and a bare-metal Celeron box)"),
    ("(box2 never runs 2B generation)", "(the Celeron N4020 never runs 2B generation)"),
    ("(box2 never runs 2B generation,", "(the Celeron N4020 never runs 2B generation,"),
    ("no energy meter on box2", "no energy meter on the Celeron N4020"),
    ("Re-run box1 once more", "Re-run on the i5-5200U machine once more"),
    ("two box2 timings", "two Celeron N4020 timings"),
    ("The box2 timing", "The Celeron N4020 timing"),
    ("box2 timing is", "Celeron N4020 timing is"),
    ("box2 memory", "Celeron N4020 memory"),
    ("On box1,", "On the i5-5200U machine,"),
    ("On box2,", "On the Celeron N4020,"),
    ("on box1", "on the i5-5200U machine"),
    ("on box2", "on the Celeron N4020"),
]

# Other prose rewrites, same meaning, to keep forbidden words off the site.
PROSE_PHRASES = [
    ("after submission.", "after it was sent to the daemon."),
    ("do not repeat that wording publicly.", "we do not repeat that wording."),
]

NICKNAME_RE = r"\b(cm-box1|box1|box2|box3|penguin|aefinity-box)\b"

# Lab-page record panel: models and hardware, set by hand per lab. Each entry is
# (label, evidence); build.py asserts that the evidence string appears in that
# lab's own method, caveats or claims in labs.json, so a label never names
# hardware the lab did not use. Pending or negated mentions are labelled as such.
RAIL = {
    "cis2-cross-machine-digest": {
        "models": [("SmolLM2-135M, fp32", "SmolLM2-135M, prompt")],
        "hardware": [("Our own x86_64 machines (AVX2 and scalar)", "own x86_64 machines (AVX2 and scalar"),
                     ("Xeon Platinum 8488C, free cloud workspace (four-digest script only)", "Xeon Platinum 8488C, 4 vCPU"),
                     ("aarch64 Android phone", "An aarch64 Android phone reproduced")]},
    "gpu-p100-reproduces-cpu": {
        "models": [("SmolLM2-135M", "SmolLM2-135M, four vectors")],
        "hardware": [("NVIDIA Tesla P100 (Kaggle)", "Kaggle Tesla P100")]},
    "t4-batching-precision": {
        "models": [("One layer-0 matmul of the reference model", "q_proj, layer 0, hidden size 576")],
        "hardware": [("NVIDIA Tesla T4 (Kaggle)", "Kaggle Tesla T4"), ("Host CPU build", "host CPU build")]},
    "cleanroom-reimplementations": {
        "models": [("SmolLM2-135M, fp32", "Model was SmolLM2-135M, fp32")],
        "hardware": [("CI runners, x86_64 and aarch64 (runs private)", "on x86_64 and aarch64 with gcc and clang")]},
    "sincos-prereg-2ulp": {
        "models": [("SmolLM2-135M and Qwen2.5-0.5B RoPE settings", "SmolLM2-135M (theta=1e5) and Qwen2.5-0.5B (theta=1e6)")],
        "hardware": [("Local x86_64 sandbox", "Local x86_64 sandbox harness"),
                     ("aarch64 confirmation pending", "Cross-ISA (aarch64) confirmation was pending")]},
    "bitflip-weights": {
        "models": [("Pruned BitNet-2B", "Pruned BitNet-2B checkpoint")],
        "hardware": [("One of our own machines", "one host (aefinity-box)")]},
    "embedding-edits": {
        "models": [("Pruned BitNet-2B", "one pruned BitNet-2B checkpoint")],
        "hardware": []},
    "receipt-verified-eval": {
        "models": [("Pruned BitNet-2B", "pruned BitNet-2B, one host")],
        "hardware": [("One of our own machines", "one host (box1)")]},
    "logging-vs-receipts": {
        "models": [("Pruned BitNet-2B", "pruned BitNet-2B, one host")],
        "hardware": [("One host", "one model, one machine")]},
    "receipt-overhead": {
        "models": [("Pinned BitNet-2B", "pinned BitNet-2B artifact triple")],
        "hardware": [("Intel i5-5200U (AVX2/FMA)", "Intel i5-5200U (AVX2/FMA)"),
                     ("Celeron N4020 (no AVX2/FMA), verifies only", "Celeron N4020 (no AVX2/FMA), which verifies only")]},
    "continuous-validation": {
        "models": [],
        "hardware": [("Intel i5-10210U, ChromeOS Crostini, no GPU", "Intel i5-10210U, no GPU, ChromeOS Crostini")]},
    "training-checkpoints-cross-isa": {
        "models": [("Tiny trainers (C version: 13,088 parameters)", "13,088 parameters")],
        "hardware": [("Intel i5-5200U (AVX2/FMA)", "AVX2/FMA CPU (Intel i5-5200U)"),
                     ("Intel Celeron N4020 (no AVX2)", "no-AVX2 CPU (Intel Celeron N4020)"),
                     ("C trainer: five hosts, incl. an aarch64 phone", "one aarch64 phone")]},
    "e22-necessity-matrix": {
        "models": [("135M checkpoint, one 4-token prompt", "single 4-token prompt on a 135M checkpoint")],
        "hardware": [("Intel i5-5200U, gcc 14.2.0", "i5-5200U, gcc 14.2.0"),
                     ("ChromeOS Crostini VM (M16 correction only)", "Crostini, gcc -O2")]},
    "e24-unicode-gap": {
        "models": [("SmolLM2-135M vocabulary", "pinned SmolLM2-135M vocabulary")],
        "hardware": [("Our x86_64 development VM", "development box (Debian 13, x86_64, crosvm guest)"),
                     ("GitHub x86_64 and aarch64 runners", "ubuntu-24.04 / ubuntu-24.04-arm runners")]},
    "e25-rmsnorm-order": {
        "models": [("SmolLM2-135M", "on SmolLM2-135M (prompt"),
                   ("Qwen2.5-0.5B (census, reported)", "second model (Qwen2.5-0.5B) census")],
        "hardware": [("Debian 13 Crostini VM, x86_64", "a Debian 13 Crostini VM on ChromeOS, x86_64")]},
    "e26-trig-range": {
        "models": [("SmolLM2-135M and Qwen2.5-0.5B", "both models (SmolLM2-135M and Qwen2.5-0.5B)")],
        "hardware": [("ChromeOS Crostini VM, x86_64", "one VM (ChromeOS Crostini, x86_64)")]},
    "e27-exp-ln-range": {
        "models": [],
        "hardware": [("An x86_64 VM", "x86_64 VM)"),
                     ("Celeron (no AVX2), same-binary re-run", "second machine (Celeron, no AVX2, same glibc)")]},
    "layer-oracle-e28-e36-e37": {
        "models": [("SmolLM2-135M", "six prompt/length cells on SmolLM2-135M"),
                   ("Qwen2.5-0.5B", "six on Qwen2.5-0.5B")],
        "hardware": []},
    "e29-optimizer-invariance": {
        "models": [("SmolLM2-135M and Qwen2.5-0.5B", "Celeron N4020) on SmolLM2-135M and Qwen2.5-0.5B")],
        "hardware": [("Intel i5-10210U (AVX2)", "AVX2 on an i5-10210U"),
                     ("ChromeOS Crostini VM", "a ChromeOS Crostini VM"),
                     ("Bare-metal Celeron N4020", "SSE-only on a Celeron N4020"),
                     ("GitHub x86_64 and aarch64 runners", "x86_64 and aarch64 on GitHub-hosted runners")]},
    "ftz-reach-e35-e40": {"models": [], "hardware": []},
    "e41-detokenization-gap": {
        "models": [("SmolLM2-135M and Qwen2.5-0.5B tokenizers", "(SmolLM2-135M and Qwen2.5-0.5B)")],
        "hardware": [("Debian 13 x86_64 VM", "one host (Debian 13, x86_64 VM)")]},
    "ev1-mini-eval": {
        "models": [("SmolLM2-135M base, fp32", "SmolLM2-135M base (fp32, greedy)")],
        "hardware": [("A single host", "Run by us on a single host")]},
    "test-standard-ledger": {"models": [], "hardware": []},
    "hall-of-divergence": {
        "models": [],
        "hardware": [("Intel i5-5200U (AVX2)", "Intel i5-5200U with AVX2"),
                     ("Intel Celeron N4020 (scalar)", "Intel Celeron N4020 scalar")]},
    "ranger-mock-run": {
        "models": [("None: synthetic tensors", "no real model")],
        "hardware": [("CPU, numpy, no GPU", "Pure numpy, fixed seed 20260714, no GPU")]},
    "ranger-phase1": {
        "models": [("SmolLM2-135M", "slice (SmolLM2-135M)"), ("Qwen3-0.6B", "Qwen3-0.6B replication")],
        "hardware": [("CPU-only 6 GB VM", "CPU-only 6 GB VM")]},
    "retraction-prochot": {
        "models": [("14.17M-parameter model", "14.17M-parameter model")],
        "hardware": [("Dell Inspiron 15, i5-5200U, bare metal", "Dell Inspiron 15 (i5-5200U, bare metal, no OS)")]},
    "soft-float-avx2": {
        "models": [],
        "hardware": [("Dell Inspiron 15, i5-5200U, bare metal", "Dell Inspiron 15 (i5-5200U, bare metal, no OS)")]},
    "os-cost-held-back": {
        "models": [],
        "hardware": [("Dell Inspiron 15, i5-5200U", "Dell Inspiron 15, i5-5200U")]},
    "lut-kernel-retraction": {
        "models": [],
        "hardware": [("Chromebook crosvm guest, i5-10210U", "Chromebook crosvm guest (i5-10210U)")]},
    "fabricated-metrics-audit": {"models": [], "hardware": []},
    "es1-trit-census": {
        "models": [("BitNet b1.58 2B engine model", "BitNet-b1.58-2B engine model")],
        "hardware": [("Dell i5-5200U", "one Dell i5-5200U")]},
    "refuted-literature-claims": {
        "models": [("Falcon-E checkpoint", "checkpoint (Falcon-E)")],
        "hardware": [("Our own target machine", "refuted by execution on our own target machine"),
                     ("Not run on a T4", "we did not run it on a T4")]},
}

# Inline SVG figures. Every number is checked against the lab's own claims and
# quotes at build time. kind "bars": horizontal bars against a stated maximum.
FIGURES = {
    "bitflip-weights": {
        "title": "Corruptions missed, out of the 247 trials where the output changed",
        "kind": "bars", "max": 247, "unit": "missed",
        "rows": [("Text / argmax replay (A)", 182, "182 / 247"),
                 ("Top-k / receipt-style check (B)", 82, "82 / 247"),
                 ("CIS witness digest (C)", 0, "0 / 247")],
        "note": "Experiment 2, 295 trials. Row C is 0 by construction, per the source.",
        "check": ["182", "82", "247", "295"],
    },
    "embedding-edits": {
        "title": "One edited embedding row that no test prompt reads: trials detected, out of 40",
        "kind": "bars", "max": 40, "unit": "detected",
        "rows": [("Text replay", 0, "0 / 40"),
                 ("Top-5 check", 0, "0 / 40"),
                 ("Witness digest", 40, "40 / 40")],
        "note": "8 random rows by 5 prompts = 40 trials.",
        "check": ["0 of 40", "40 of 40"],
    },
    "t4-batching-precision": {
        "title": "Elements that differ from the batch-1 reference, out of 576",
        "kind": "bars", "max": 576, "unit": "differ",
        "rows": [("Row-batched fp32 (batch 1, 4, 8)", 0, "0 / 576"),
                 ("Grouped fp32", 455, "455 / 576"),
                 ("int8", 576, "576 / 576")],
        "note": "One matrix multiply on a Tesla T4; host and CUDA builds agreed on all 10 configurations.",
        "check": ["0/576", "455/576", "576/576"],
    },
    "ev1-mini-eval": {
        "title": "Items passed, by category",
        "kind": "ratio",
        "rows": [("Truthfulness", 3, 60), ("Tool-use proxy", 5, 60),
                 ("Refusal probes", 10, 20), ("Self-consistency", 20, 20)],
        "note": "Self-consistency measures repeatability, not accuracy. The source says the refusal score sits at chance.",
        "check": ["3 of 60", "5 of 60", "10 of 20", "20 of 20"],
    },
    "sincos-prereg-2ulp": {
        "title": "Maximum sin/cos error in ULP against the pre-registered 2 ULP bar (log scale)",
        "kind": "log", "bar": 2,
        "rows": [("v0.2 sin", 115198), ("v0.2 cos", 163969), ("v0.3 (max)", 2813.5),
                 ("v0.3b sin", 1.5), ("v0.3b cos", 1.5)],
        "note": "The values come from different local runs (v0.2 from the oracle run, v0.3b from the harness run, v0.3 as raw ULP), so the bars are not a like-for-like comparison. v0.3b meets the bar; v0.2 and v0.3 do not.",
        "check": ["115198", "163969", "2813.5", "1.5", "2 ULP"],
    },
    "e22-necessity-matrix": {
        "title": "16 single-rule mutations of the spec: did the digest move?",
        "kind": "waffle",
        "cells": [("moved", 12, "Digest moved"), ("same", 3, "Digest unchanged"), ("skip", 1, "Declared skipped")],
        "note": "Each square is one mutation. Unchanged rows include the tie-break, which the vector never reaches, and a vacuous mutation the authors corrected.",
        "check": ["12 of 16", "3 did not", "1 was declared skipped"],
    },
}

# Pilot page copy, from the v2 public/pilot.html. Two timing phrases removed
# ("It takes about 15 minutes", "about 15 min") under the no-timing rule.
PILOT = {
    "title": "CIS-2 replay pilot (archived)",
    "lede": "Archived research (2026-10), development paused. This pilot is no longer offered. The page stays as a record of what it was.",
    "glance": [
        ("Length", "4 to 6 weeks"),
        ("Scope", "One pipeline, one open-weight model, a set of requests"),
        ("Replay", "On a machine separate from yours, with the open verifier"),
        ("Output", "Mismatch report, replayable artifact, plain statement of limits"),
        ("Status", "Archived research (2026-10), development paused; no longer offered"),
    ],
    "report_rows": [("req 001", True, "all digests equal"), ("req 002", True, "all digests equal"),
                    ("req 003", False, "earliest divergent step, if traced"), ("req 004", True, "all digests equal")],
    "report_caption": "Illustration of the report's shape, not a real result.",
    "who": [
        ("Inference providers and platform teams", "Who want a third party to be able to check that a deployment serves the model it says it serves."),
        ("AI governance and audit platforms", "That want to attach checkable evidence of the exact computation to a record."),
        ("Evaluation and assurance teams", "Who need results that others can replay."),
    ],
    "steps_intro": "The specification and verifiers are open (Apache-2.0); how much integration help you need is settled in scoping.",
    "steps": [
        ("Scoping", "We agree one pipeline, one open-weight model, a set of requests, and what a match must mean for you."),
        ("Receipts", "Your pipeline emits CIS-2 receipts for those requests. The specification and verifiers are open (Apache-2.0); how much integration help you need is settled in scoping."),
        ("Replay", "We replay the receipts on a machine separate from yours with the open verifier and compare every digest."),
        ("Report", "You get a mismatch report that lists every request whose digests differ and, where the per-step trace is available, the earliest step at which it diverges; a replayable artifact (receipts, pinned digests, a verify script) your own staff can re-run; and a plain statement of limits."),
    ],
    "get": [
        ("A written answer to one question", "Do your receipts replay bit for bit elsewhere, and if not, where do they stop matching?"),
        ("Nothing you have to trust us for", "The verifier is open, and the artifact re-runs without us."),
    ],
    "not": [
        ("Not a correctness, safety or fairness audit.", "A matching receipt shows a computation was reproduced, not that the answer was right."),
        ("Not a certification, and not legal advice.", "We think the evidence is relevant to record-keeping requirements such as the EU AI Act's logging provisions; no auditor or lawyer has confirmed that mapping."),
        ("Not a promise that your stack will match.", "Our evidence is small open models in fp32, mostly on CPU, limited to greedy decoding. Production bf16 or GPU serving is outside the spec today, so the pilot shows how far your stack gets, and the report says so."),
    ],
    "before": "See whether it matches. It needs no account or GPU.",
    "before_fine": "The README lists what has been run, on which machines, and what has not. No unaffiliated party has reproduced it yet; every run listed is ours.",
    "start": "Paid pilots; contact us for scope and terms. Email justin@aefinityai.com with three lines.",
    "about": "AEFINITY AI INC. is an early-stage company in Orange, Texas, founded by Justin Thompson.",
    "lines": ["Which pipeline and model.", "Which precision and hardware you serve on.", "What you would use a receipt for."],
    "mailto": "mailto:justin@aefinityai.com?subject=CIS-2%20pilot&body=Pipeline%20and%20model%3A%20%0D%0APrecision%20and%20hardware%20we%20serve%20on%3A%20%0D%0AWhat%20we%20would%20use%20a%20receipt%20for%3A%20%0D%0A",
    "mailto_short": "mailto:justin@aefinityai.com?subject=CIS-2%20pilot",
}

SELFCHECK_CMD = "git clone https://github.com/Aefinity-AI/cis2-spec && cd cis2-spec && ./selfcheck.sh"


# --------------------------------------------------------------------------
# Commercial pages (/alice/, /cis/, /operations/, /contact/ and the home
# offerings band). Short and confident, but nothing false: no customers,
# partners, certifications or compliance claims; no prices; CIS-3 is named
# with its purpose only. build.py runs COMMERCIAL_BANNED over every page and
# checks each number in PROOF against labs.json.
# --------------------------------------------------------------------------
def mailto(subject):
    return f"mailto:{EMAIL}?subject=" + subject.replace(" ", "%20")


OFFER_TITLE = "Bare-metal inference, built for air-gapped work."

ARCHIVE_NOTE = "Archived research (2026-10), development paused."

# Home hero: A.L.I.C.E. on the first screen. The research labs stay published,
# below the A.L.I.C.E. story.
HERO = {
    "kicker": "Aefinity AI · A.L.I.C.E. · Bare-metal inference",
    "h1": "A.L.I.C.E.: AI inference that runs <em>on bare metal.</em>",
    "lede": "A.L.I.C.E. is built to run a ternary language model with integer math and no general-purpose operating system. Every generation carries a receipt that a separate host verifier re-derives. Built for air-gapped inference and security, and for defense and Army field requirements. Non-air-gapped variants are planned, to be built and tested to spec.",
    "mission_note": "We are not another AI platform or cloud service.",
}
HERO_FLOW = [
    ("Bootable image", "Inference runs without a general-purpose operating system."),
    ("Integer and ternary math", "BitNet b1.58 weights, integer arithmetic, run on the CPU."),
    ("Receipt", "Each generation produces a receipt."),
    ("Host verifier", "A separate verifier re-derives the receipt and reports any mismatch."),
]
OFFERINGS = [
    {"icon": "alice", "tag": "A.L.I.C.E.", "kind": "Bare-metal inference", "href": "/alice/", "cta": "Explore A.L.I.C.E.",
     "body": "Integer and ternary inference built to run without a general-purpose operating system, on hardware you control. Pilot-stage, scoped with each deployment."},
    {"icon": "cis", "tag": "CIS-1", "kind": "Protocol under A.L.I.C.E.", "href": "/cis/", "cta": "See CIS-1",
     "body": "Bit-identical integer and ternary inference, with a receipt for every generation that a host verifier can re-derive."},
    {"icon": "airgap", "tag": "Air-gapped inference and security", "kind": "Primary use", "href": "/alice/#airgap", "cta": "See the primary use",
     "body": "Inference and security work on disconnected networks, field kits and edge devices. Built for defense and Army field requirements."},
    {"icon": "compass", "tag": "Roadmap", "kind": "Planned, not built", "href": "/alice/#roadmap", "cta": "See the roadmap",
     "body": "Non-air-gapped variants and Project Guardian, soldier-facing work: planned, to be built and tested to spec. Not available today."},
]

# Proof strip. Each "check" token must appear in the named lab's sourced text.
PROOF = [
    {"big": "33", "label": "published labs", "check": None},
    {"big": "84", "label": "registered experiments on a public, hash-chained ledger",
     "check": ("test-standard-ledger", "84 registered experiments")},
    {"big": "One receipt", "label": "BitNet b1.58 2B-4T (vocabulary-pruned) under CIS-1: the same receipt on three x86 machines, with and without AVX2, re-verified by a standalone verifier. Our own runs, October 2026.", "check": None},
    {"big": "Bootable", "label": "The bootable image has been demonstrated in QEMU and on physical hardware with a smaller model.", "check": None},
]

OPS_BAND = {
    "kicker": "Autonomous Operations",
    "title": "Your work, run by AI, to a lab standard",
    "body": "We design, set up and manage AI-run workflows for office operations, customer service and research. Every action logged. Every risky step gated for a human. Every result checked before it ships.",
}

BRIEFING = {
    "title": "Tell us what you need to run air-gapped.",
    "body": "We reply personally.",
}

ALICE = {
    "title": "A.L.I.C.E.: bare-metal inference for air-gapped work",
    "h1": "Bare-metal inference, <em>built for air-gapped work.</em>",
    "lead": "A.L.I.C.E. is inference built to run without a general-purpose operating system, using integer and ternary math. Every generation carries a receipt that a separate host verifier re-derives. Built for air-gapped inference and security, and for defense and Army field requirements.",
    "caps": [
        ("airgap", "Primary use: inference and security on air-gapped networks"),
        ("server", "Built to run without a general-purpose operating system"),
        ("nocloud", "No outside data processor, no cloud connection required"),
        ("target", "Integer and ternary arithmetic (CIS-1), designed for bit-identical results"),
        ("laptop", "Today: BitNet b1.58 2B-4T, vocabulary-pruned, on ordinary x86 CPUs"),
    ],
    "how_title": "How it works",
    "how": [
        ("Bootable image", "Inference runs without a general-purpose operating system underneath it."),
        ("Integer inference", "A ternary BitNet b1.58 model, integer arithmetic, on the CPU."),
        ("Receipt", "Each generation produces a receipt."),
        ("Host verifier", "A separate verifier re-derives the receipt and reports any mismatch."),
    ],
    "today_title": "What runs today",
    "today_intro": "Everything below is from our own runs. No outside party has reproduced any of it yet.",
    "today": [
        ("Model", "BitNet b1.58 2B-4T, vocabulary-pruned, run under CIS-1 integer math."),
        ("Receipts", "In October 2026, one generation produced the same receipt on three x86 machines, with and without AVX2, and a standalone verifier re-verified it on each."),
        ("Bootable image", "Demonstrated in QEMU and on physical hardware with a smaller model."),
    ],
    # (icon, who, the need in one line, what A.L.I.C.E. gives)
    "uses": [
        ("shield", "Defense, government and secure facilities", "Restricted networks are disconnected on purpose.",
         "Inference and security work on disconnected networks, field kits and edge devices, on hardware you control. Built for defense and Army field requirements; we are pursuing Army SBIR work."),
        ("bolt", "Critical infrastructure and industrial sites", "Operations cannot depend on the network.",
         "An offline operations assistant for procedures, logs and shift handovers that keeps working when the network does not."),
        ("compass", "Remote and field operations", "Ships, remote sites, disaster response.",
         "A working assistant aboard a ship, at a remote site or in a response kit, with no connectivity required."),
        ("hospital", "Hospitals and clinics", "Patient data cannot leave the hospital network.",
         "Clinical notes, discharge letters, inbox triage and coding support, on machines inside the hospital network. Designed to keep patient data on hospital hardware."),
        ("scales", "Law firms and legal departments", "Privileged documents cannot go to a third-party processor.",
         "Review and summarize privileged documents with no third-party processor."),
        ("bank", "Finance and insurance", "Decisions are examined after the fact.",
         "Decision support, document review and model risk checks on your own servers."),
        ("flask", "Research and regulated R&D", "IP has to stay in house.",
         "Keep IP and AI-assisted work in house, on your own machines."),
        ("folder", "Any team handling sensitive data", "HR, internal investigations, board materials.",
         "Summarize and search HR files, investigation notes and board papers on a machine in the room, designed so nothing leaves it."),
    ],
    "roadmap_title": "Roadmap: planned, not built",
    "roadmap_intro": "Nothing in this section exists as a product today. Each item is to be built and tested to spec.",
    "roadmap": [
        ("laptop", "Non-air-gapped variants", "Planned. Variants for networked deployments, to be built and tested to spec."),
        ("shield", "Project Guardian", "Planned future work for soldiers. This is roadmap, not product: nothing is built, tested or fielded."),
        ("flask", "DeltaNet and hybrid models", "Planned research. Not built."),
    ],
    "engage": [
        ("Briefing", "We map your use case."),
        ("Pilot on your hardware", "Scoped and measured."),
        ("Support", "On site or remote."),
    ],
    "stage": "A.L.I.C.E. is pilot-stage technology; each deployment is scoped and tested with you on site.",
}

CIS = {
    "title": "CIS-1: the protocol under A.L.I.C.E.",
    "h1": "The protocol <em>under A.L.I.C.E.</em>",
    "lead": "CIS-1 is integer and ternary inference whose results are bit-identical, with a receipt for every generation that a host verifier can re-derive.",
    "cis1": [
        "CIS-1 is the protocol A.L.I.C.E. runs under. Inference uses integer and ternary arithmetic with no floating point, so the same model and input are designed to give the same output on any machine that follows the protocol. Each generation produces a receipt, and a separate host verifier re-derives it.",
        "What we have run so far: BitNet b1.58 2B-4T, vocabulary-pruned, produced the same receipt on three x86 machines, with and without AVX2, and a standalone verifier re-verified it on each. These are our own runs from October 2026; no outside party has reproduced them. DeltaNet and hybrid models are planned research and are not built.",
    ],
    "cis1_links": [
        ("A.L.I.C.E. on GitHub", "https://github.com/Aefinity-AI/alice-aegis"),
    ],
    "archive_note": "Archived research (2026-10), development paused. CIS-2 (bit-exact fp32 inference) is no longer a product or an offer. The pages and results stay public as a record.",
    "cis2": "CIS-2 is an open specification with verifiers in C and Rust for bit-exact fp32 inference, with public conformance vectors. In our own runs, one digest reproduced on AVX2 and scalar x86, an AVX-512-capable cloud CPU (generic build, self-check only), an aarch64 phone and a Tesla P100 GPU.",
    "cis2_links": [
        ("CIS-2 on GitHub (archive)", "https://github.com/Aefinity-AI/cis2-spec"),
        ("Conformance vectors on Hugging Face (archive)", "https://huggingface.co/datasets/aefinityAIINC/cis2-conformance"),
    ],
    "cis2_labs": ["cis2-cross-machine-digest", "gpu-p100-reproduces-cpu", "cleanroom-reimplementations"],
    "cis3_kicker": "CIS-3 · LLM edition · Development paused",
    "cis3_h": "Not offered at this time.",
    "cis3_body": "Our work is focused on A.L.I.C.E. and CIS-1.",
    "cta": "Talk to us about A.L.I.C.E.",
    "licensing": "Briefings are on request. Tell us about your air-gapped inference and security requirements.",
}

# Ledger counts. source: claudius-maximus state/ledger/experiments.jsonl @0cb928e1 2026-10-15
# (236 lines: 84 registered, 73 started, 65 result, 14 amended). 84 and 65 match the
# public cis2-spec ledger export quoted on /standard/ ("84 registered experiments, 65 verdicts").
LEDGER_SOURCE = "source: claudius-maximus state/ledger/experiments.jsonl @0cb928e1 2026-10-15"
LEDGER_REGISTERED = 84
LEDGER_RESULTS = 65

OPS = {
    "title": "Autonomous Operations: AI that runs the work, to a lab standard",
    "h1": "AI that runs the work, <em>to a lab standard.</em>",
    "lead": "We design, set up and manage AI-run workflows for office operations, customer service and research. Every action logged. Every risky step gated for a human. Every result checked before it ships.",
    "proof_kicker": "Proof",
    "proof_h": "We run our own lab this way.",
    "proof_body": "Our lab is operated by an AI-managed workflow on a small number of our own refurbished machines, often just one of them online, plus free-tier cloud GPU hours: it registers experiments, runs them, keeps the records, checks its own work and writes the reports. People sign off on money, credentials, outreach and anything public.",
    "loop": ["Register", "Run", "Record", "Check", "Report"],
    "log": [
        ("inbox", "Triage the shared inbox", "Logged", "ok"),
        ("headset", "Draft a reply to a customer question", "Checked", "ok"),
        ("folder", "File the signed documents", "Logged", "ok"),
        ("bank", "Pay a supplier invoice", "Waiting for sign-off", "gate"),
        ("mail", "Send the monthly report", "Waiting for sign-off", "gate"),
    ],
    "gate": "People sign off on money, credentials, outreach and anything public.",
    "site_fact": "This website was produced by the same workflow, with human sign-off. Every claim on its 33 lab pages was checked against its public source by a separate AI checking pass before publishing.",
    "automate": [
        ("inbox", "Office operations", "Inbox triage and drafting, scheduling, documents, records, reporting."),
        ("headset", "Customer service", "Answers drafted from your own knowledge base, clear escalation rules, every reply logged and reviewable."),
        ("data", "Research and data operations", "Pipelines, experiments, reports with a source behind every number."),
        ("server", "Machines and IT care", "Health checks, updates, alerts, recovery."),
    ],
    "standard": [
        ("gate", "Gates", "Money, credentials, outreach and publishing wait for a named person."),
        ("log", "Records", "An append-only log of every action."),
        ("check", "Verification", "A separate checker reviews results before they ship."),
        ("chain", "Provenance", "Every number traces to its source."),
        ("stop", "Control", "A stop switch and rollback for every workflow."),
    ],
    "engage": [
        ("Assess", "Map the work, pick one process."),
        ("Build", "On your PCs and accounts, gated from day one."),
        ("Prove", "A measured before-and-after on that one workflow."),
        ("Manage", "On site or remote, ongoing."),
    ],
    "models": "Built on frontier commercial AI models, or on private models with ALICE where data cannot leave the building.",
}

CONTACT = {
    "title": "Book a briefing",
    "h1": "Book a <em>briefing.</em>",
    "lead": "Tell us about your air-gapped inference and security requirements. We reply personally.",
    # (icon, title, line, subject, extra link)
    "cards": [
        ("alice", "A.L.I.C.E. briefing", "Bare-metal inference for air-gapped work, on hardware you control.", "A.L.I.C.E. briefing", None),
        ("airgap", "Air-gapped inference and security", "Requirements for disconnected networks, field kits and edge devices.", "Air-gapped inference and security", None),
        ("compass", "Non-air-gapped variants and Project Guardian", "Planned work, to be built and tested to spec. Tell us your requirement.", "Planned variants and Project Guardian", None),
        ("ops", "Autonomous Operations", "AI-run workflows, set up and managed to our lab standard.", "Autonomous Operations", None),
    ],
}

# Terms that never appear on any page (outside verbatim quotes), and terms that
# never appear on the commercial pages. Case-insensitive, whole words.
def _private_banned():
    # Extra terms kept outside the public repo, one per line.
    f = os.path.expanduser("~/.config/aefinity/site-banned-private.txt")
    if not os.path.exists(f):
        print("WARNING: private banned-terms file missing; build lint is weaker")
        return []
    return [re.escape(t.strip()) for t in open(f) if t.strip()]


SITE_BANNED = [r"HIPAA", r"FedRAMP", r"lawsuit", r"world'?s",
               r"state-of-the-art", r"revolutionary", r"(?<!not a )partner of", r"accredit\w*"] + _private_banned()
# Lab caveats say "not a guarantee"; the commercial pages never use the word.
COMMERCIAL_BANNED = SITE_BANNED + [r"guarantee\w*", r"certified", r"certif\w+", r"compliant", r"compliance", r"classified",
                                   r"unique", r"first", r"(?<!append-)(?<!self-check )only", r"leading", r"best", r"\$\s?\d", r"price\w*",
                                   r"day rate", r"funding", r"customers\b", r"clients\b", r"partnered", r"partners?\b",
                                   r"independent\w*", r"every recommendation",
                                   r"proves\b", r"validated", r"military-grade", r"unhackable", r"conformant",
                                   r"contract\w*", r"endorse\w*", r"selected"]

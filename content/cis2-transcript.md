# CIS-2 explainer - transcript

## Opening  (0:00)

How can you check what an AI really did?

## The problem  (0:02)

You ask an AI a question, and it gives you an answer.

But which model really produced it? And was anything changed along the way?

Today, you take the operator's word for it.

## Why computers disagree  (0:14)

Why not just run it again and compare? Because computers don't always agree with themselves.

Think of a grocery bill. Add the items in a different order, rounding as you go, and the total can shift by a cent.

Computers do the same. Different chips add in a different order, so one model, on one input, can give slightly different numbers.

Nobody can say if that is noise, or a changed model.

## The recipe  (0:42)

CIS-2 is an open standard that fixes this. It is a written specification that pins down every one of those choices.

Think of a recipe so exact that it fixes the order of every step and how to round every measurement. Any cook, in any kitchen, gets the same cake.

## The receipt  (1:03)

When a model runs under CIS-2, it produces a receipt: a short fingerprint of its work.

At every step, the model scores about forty-nine thousand possible next words. CIS-2 folds all of those numbers into one fingerprint.

Change the weights, the input, or one bit of the arithmetic, and the fingerprint changes completely.

## Tested from the text alone  (1:28)

A recipe is good if a stranger can follow it. So we tested the text on its own: separate builds, made from the spec alone, in Rust and in C.

They never saw each other's code, and both matched on Intel and ARM chips.

The test also caught a mistake in our own write-up: one step was in the wrong order. We fixed the text, and every build then matched.

## Check it yourself  (1:55)

You don't have to take our word for it. The verifier is public and free.

One command downloads the pinned model, checks every file against a known hash, builds the verifier, and runs it.

It compares every fingerprint with the published one. If they all match, you get a PASS. No account, no special hardware.

And if even one byte of the model file is changed, it refuses to run.

## What it catches  (2:23)

Why fingerprint all the numbers, not just the words? Because the words can stay the same while the model underneath has changed.

In our own tests on a separate, larger model, we corrupted it in small ways. Comparing the text missed one hundred and eighty-two of two hundred and forty-seven. The full fingerprint missed none.

Nudge one row out of fifty thousand: comparing text caught none of forty tries. The fingerprint caught all forty.

## Published results  (2:53)

For the main published test, a small open model, a short prompt, and sixteen tokens, there is one pinned fingerprint.

It was reproduced on Intel chips, a cloud server chip, an ARM phone, and an NVIDIA Tesla P100 graphics card.

## Limits  (3:10)

Now, what it does not do. It does not tell you an answer is right, safe, or fair. A model can be perfectly repeatable and still be wrong.

Today it covers full-precision numbers and greedy decoding, on small open models, mostly on ordinary processors.

And every run so far was done by us. No outside party has reproduced it yet.

So we publish a challenge: if you can make it differ, tell us, and we will credit you.

## Where to get it  (3:41)

CIS-2 is open under the Apache license. The specification, the verifiers, and the test vectors are on GitHub and Hugging Face. Run it, break it, and tell us what you find.

Links: https://github.com/Aefinity-AI/cis2-spec  ·  https://huggingface.co/datasets/aefinityAIINC/cis2-conformance  ·  https://aefinityai.com

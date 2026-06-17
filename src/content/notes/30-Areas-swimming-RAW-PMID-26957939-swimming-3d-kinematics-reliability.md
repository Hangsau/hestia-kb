---
_slug: 30-Areas-swimming-RAW-PMID-26957939-swimming-3d-kinematics-reliability
_vault_path: 30-Areas/swimming/RAW/PMID-26957939-swimming-3d-kinematics-reliability.md
uid: PMID-26957939
type: research-article
title: Reliability of Three-Dimensional Angular Kinematics and Kinetics of Swimming
  Derived from Digitized Video
authors: Sanders RH, Gonjo T, McCabe CB
journal: J Sports Sci Med
date: 2016-02-23
pmid: 26957939
pmcid: PMC4763835
status: seedling
validation: ⚠️ SEE CONTRADICTIONS BELOW
tags:
- swimming
- 3D-kinematics
- methodology
- reliability
- digitized-video
created: '2026-05-24'
updated: '2026-06-15'
---

## Abstract

The purpose of this study was to explore the reliability of estimating three-dimensional (3D) angular kinematics and kinetics of a swimmer derived from digitized video. Two high-level front crawl swimmers and one high level backstroke swimmer were recorded by four underwater and two above water video cameras. One of the front crawl swimmers was digitized at 50 fields per second with a window for smoothing by a 4(th) order Butterworth digital filter extending 10 fields beyond the start and finish of the stroke cycle (FC1), while the other front crawl (FC2) and backstroke (BS) swimmer were digitized at 25 frames per second with the window extending five frames beyond the start and finish of the stroke cycle. Each camera view of one stroke cycle was digitized five times yielding five independent 3D data sets from which whole body centre of mass (CM) yaw, pitch, roll, and torques were derived together with wrist and ankle moment arms with respect to an inertial reference system with origin at the CM. Coefficients of repeatability ranging from r = 0.93 to r = 0.99 indicated that both digitising sampling rates and extrapolation methods are sufficiently reliable to identify real differences in net torque production. This will enable the sources of rotations about the three axes to be explained in future research. Errors in angular kinematics and displacements of the wrist and ankles relative to range of motion were small for all but the ankles in the X (swimming) direction for FC2 who had a very vigorous kick. To avoid large errors when digitising the ankles of swimmers with vigorous kicks it is recommended that a marker on the shank could be used to calculate the ankle position based on the known displacements between knee, shank, and ankle markers.

## Technical Relevance

- **Methodology**: reliability of 3D angular kinematics/kinetics from digitized video for swimming
- Coefficients of repeatability: r = 0.93 to r = 0.99 (excellent)
- 50fps sufficient for reliable 3D swimming motion analysis
- Recommendation: marker on shank for swimmers with vigorous kicks (to improve ankle position accuracy)
- Foundation for later Gonjo et al. backstroke/front crawl body roll studies

## ⚠️ CONTRADICTIONS / VALIDATION NOTES

❌ **"r = 0.93 to r = 0.99" stated as repeatability coefficients** — In biomechanics, coefficients of repeatability are typically ICC (intraclass correlation coefficients) orloa (limits of agreement), not Pearson r values. r = 0.93–0.99 are very high for Pearson correlations (which assess linear association), but a poor choice for reliability (which should assess consistency of agreement between repeated measurements). The paper may be mislabeling ICC as "r", or using a repeatability coefficient formula inconsistent with standard K-revision ( Hopkins 2000 ). **Requires verification** — if these are Pearson r rather than ICC, the reliability conclusion may be overstated.

❌ **"50 fields per second" vs "25 frames per second"** — Interlaced video at 50 fields/s provides motion information at both odd and even fields (effective 25 fps per full frame), but temporal resolution differs. FC1 digitized at "50 fields/s" with Butterworth filter window 10 fields beyond stroke boundaries vs FC2/BS at "25 frames/s" with window of 5 frames — these are fundamentally different protocols. The paper claims both sampling rates are "sufficiently reliable," but the difference in smoothing windows (10 vs 5 fields/frames) confounds whether it is the sampling rate or the extrapolation window driving reliability. **Methodological confound not addressed.**

❌ **"Coefficients of repeatability" language** — The paper uses this term but appears to compute repeatability across 5 repeated digitizations of the same stroke cycle from different camera views. This is a test-retest reliability assessment with n=5 repeated measures, but n=3 swimmers (FC1, FC2, BS). Generalizing coefficients of r = 0.93–0.99 to all swimming kinematics is a small-sample inference problem — these coefficients may only characterize within-swimmer, within-stroke variability and not generalize to across-swimmers or across-strokes.

❌ **Ankle error caveat** — The paper notes FC2 (25 fps) had "very vigorous kick" causing large errors in ankle X-direction (swimming direction). However, FC2 was sampled at 25 fps while FC1 (50 fields/s) is not flagged for this problem. This creates ambiguity: is the ankle error due to the vigorous kick itself (a swimmer characteristic), or due to the lower 25 fps sampling rate failing to capture fast ankle motion? The recommendation to add a shank marker conflates two separate issues (biomechanical + methodological) without isolating which one is primary.

❌ **Butterworth filter cut-off frequency not stated** — The abstract specifies 4th-order Butterworth filter and a smoothing window extending N fields beyond stroke boundaries, but does not report cut-off frequency. Without this parameter, the study cannot be replicated and the reliability claim cannot be verified by other labs. Filter settings are a critical methodological detail.
# Bauform Production Readiness Benchmark

**Version:** 1.0  
**Status:** Public  
**Purpose:** Comprehensive evaluation framework for code generation systems

---

## Overview

Most code generation benchmarks (HumanEval, MBPP, CodeContests) measure algorithm correctness on toy problems. **This benchmark measures production readiness** - whether generated code can actually ship.

### What Makes This Different

| Traditional Benchmarks | Bauform Benchmark |
|------------------------|-------------------|
| Toy problems (fibonacci, sorting) | Real-world tools (CSV validators, API clients) |
| "Does it pass unit tests?" | "Can it deploy and run in production?" |
| Static correctness | Security + Performance + Reliability |
| Seconds to run | Minutes to validate (includes deployment) |
| Academic curiosity | Production utility |

---

## Benchmark Structure

```
bauform-evals/
├── r1.0/                          # Current version (10 specs)
│   ├── csv_transformer_v2/
│   │   ├── result.json            # Test results
│   │   ├── result.json.signed     # Cryptographically signed proof
│   │   ├── spec.txt               # Specification
│   │   └── limits.json            # Resource constraints
│   ├── json_validator_v2/
│   ├── email_validator_v2/
│   └── ... (7 more specs)
│
├── SHA256SUMS                      # Integrity verification
├── verify.py                       # Signature verification tool
└── README.md                       # This file
```

---

## The Five Gates

Every generated tool must pass **all five gates** to be considered production-ready:

### ✅ Gate 1: Functional Correctness
- All golden test cases pass (100% required)
- Edge cases handled properly
- Deterministic outputs (where applicable)
- No regressions vs. previous version

### ✅ Gate 2: Security Hardening
- **CSV Injection:** `=1+1`, `+cmd|'`, `@SUM()` → blocked
- **Path Traversal:** `../../etc/passwd` → rejected
- **SSRF:** `http://169.254.169.254/` → blocked
- **JSON Depth Bombs:** 128-level nesting → rejected
- **Command Injection:** Shell metacharacters → sanitized

### ✅ Gate 3: Limit Enforcement
- File size limits → return `413 Payload Too Large`
- Row/record limits → return `413`
- JSON depth limits → return `400 Bad Request`
- Timeout enforcement → no hanging

### ✅ Gate 4: Performance
- **p95 latency** ≤ target (typically 200-500ms)
- **Throughput** measured at 10 concurrent connections
- **Cold start** ≤ 2× steady-state latency
- Measured over 200 requests per test

### ✅ Gate 5: Resource Stability
- **Memory:** No leaks, bounded usage
- **CPU:** Reasonable consumption
- **Determinism:** Same input → same output (3 runs)

---

## Results Summary

- **Paper (October 2025):** 4 example tools detailed
- **Full benchmark:** 10 tools evaluated
- **Success rate:** 10/10 (100%)
- **All results cryptographically signed and verifiable**

---

## Current Specifications (r1.0)

| ID | Name | Category | Spec File |
|----|------|----------|-----------|
| 001 | CSV Validator | Data Processing | [specs/001_csv_validator_v2.yaml](specs/001_csv_validator_v2.yaml) |
| 002 | CSV Transformer | Data Processing | [specs/002_csv_transformer_v2.yaml](specs/002_csv_transformer_v2.yaml) |
| 003 | Email Validator | Validation | [specs/003_email_validator_v2.yaml](specs/003_email_validator_v2.yaml) |
| 004 | JSON Validator | Data Processing | [specs/004_json_validator_v2.yaml](specs/004_json_validator_v2.yaml) |
| 005 | Invoice Matcher | Business Logic | [specs/005_invoice_matcher_v2.yaml](specs/005_invoice_matcher_v2.yaml) |
| 006 | Name Deduplicator | Data Processing | [specs/006_name_deduper_v2.yaml](specs/006_name_deduper_v2.yaml) |
| 007 | Record Paginator | System Utilities | [specs/007_record_paginator_v2.yaml](specs/007_record_paginator_v2.yaml) |
| 008 | REST API Echo | API Integration | [specs/008_rest_api_echo_v2.yaml](specs/008_rest_api_echo_v2.yaml) |
| 009 | Text Analyzer | Text Processing | [specs/009_text_analyzer_v2.yaml](specs/009_text_analyzer_v2.yaml) |
| 010 | URL Fetcher | System Utilities | [specs/010_url_fetcher_v2.yaml](specs/010_url_fetcher_v2.yaml) |

**Total:** 10 production-ready specs  
**Pass Rate (Bauform r1.0):** 10/10 (100%)

Each spec includes:
- Detailed functional & security requirements
- Explicit constraints & performance targets
- Test scenarios (golden cases & adversarial inputs)
- Validation gates (what must pass)
- Deployment guidelines

---

## Verification

All results are **cryptographically signed** with Ed25519 to prevent tampering.

### Verify a Single Result

```bash
# Install dependencies
pip install pynacl

# Verify signature
python verify.py r1.0/csv_validator_v2/result.json.signed

# Check integrity
sha256sum -c SHA256SUMS
```

### Public Key

```
Bauform Signing Key (Ed25519):
Public: [included in each .signed file]
```

Results cannot be forged without the private key (which is not published).

---

## How to Use This Benchmark

### For Researchers

Compare your code generation system against Bauform:

1. **Read the specs:** Each `spec.txt` describes what to build
2. **Generate code:** Use your system to generate implementations
3. **Run your code:** Deploy and test against the same test harness
4. **Report results:** Follow the same format (`result.json`)

### For Practitioners

Evaluate if a code generator is production-ready:

1. **Check the pass rate:** 10/10 = excellent, <8/10 = needs work
2. **Review gate failures:** Which gates failed? Security? Performance?
3. **Examine specific specs:** Does it handle your use cases?

### For Competitors

We welcome submissions from other systems:

```bash
# Run your system against our specs
your_system generate --spec r1.0/csv_validator_v2/spec.txt

# Test your generated code with your harness
# Document your methodology

# Submit results via PR
# Include: result.json, methodology.md, signature
```

**Requirements for submissions:**
- Use the same 10 specs
- Document your methodology clearly
- Provide reproducible results
- Sign your results cryptographically
- No cherry-picking (must submit all 10)

---

## Scoring Methodology

### Primary Metric: Production-Ready Count

**Binary pass/fail per spec.** No partial credit.

A spec passes if and **only if** all 5 gates pass:
```
production_ready = (
    functional_100% AND
    security_gates_pass AND  
    limits_enforced AND
    performance_targets_met AND
    resource_stability
)
```

**Current Results:**
- **Bauform r1.0:** 10/10 (100%)
- **Your System:** Submit results to appear here

### Secondary Metrics

For passed specs, we track:
- **Generation time:** How long to create the tool
- **p95 latency:** Response time under load
- **Memory usage:** Peak RSS
- **Cost:** Estimated API costs (if applicable)

These are for analysis only - they don't affect pass/fail.

---

## Benchmark Philosophy

### Why Binary Scoring?

Production software either works or it doesn't. A CSV validator that passes 98% of test cases but fails on malicious input is **not production-ready**.

### Why These Specs?

Each spec represents **real work developers do:**
- Data validation and transformation
- API integration
- Security hardening
- Business logic implementation

Not toy problems, not competitive programming, not academic exercises.

### Why Five Gates?

Because production code must be:
1. **Functionally correct** (obvious)
2. **Secure** (prevents exploits)
3. **Bounded** (doesn't hang or exhaust resources)
4. **Fast enough** (meets performance SLAs)
5. **Stable** (doesn't leak memory or behave non-deterministically)

Skip any gate and you have pre-production code at best, dangerous code at worst.

---

## Limitations & Disclaimers

### What This Benchmark Does NOT Measure

- **Arbitrary code complexity:** We focus on practical utility, not algorithmic puzzles
- **Every possible use case:** 10 specs can't cover all of software engineering
- **Long-term maintainability:** We test initial generation, not evolution
- **Human readability:** We test functionality, not code quality
- **Edge case coverage:** Test suites are comprehensive but not exhaustive

### Known Limitations

- **Test harness is private:** To prevent gaming, validation logic is not public
- **Specs are minimal:** Real requirements are often more detailed
- **No UI/UX testing:** We test backend logic and APIs only
- **Single-language focus:** Currently Python-only

### Future Directions

**r2.0 planned additions:**
- 20 total specs (10 more)
- Deployment validation (Docker builds, health checks)
- Sustained stress testing (5-minute load tests)
- More languages (JavaScript, Go, Rust)
- API integration specs (OAuth, webhooks, GraphQL)

---

## Citation

If you use this benchmark in research, please cite:

```bibtex
@misc{bauform2025benchmark,
  title={Bauform Production Readiness Benchmark},
  author={Edwards, Gavin},
  year={2025},
  publisher={GitHub},
  howpublished={\url{https://github.com/tekodu/bauform-evals}}
}
```

---

## Contact

- **Issues/Questions:** Open a GitHub issue
- **Email:** gavinedwards1004@gmail.com
- **Paper:** [Link to ArXiv when published]

---

## License

- **Benchmark specifications:** CC0 (public domain)
- **Signed results:** CC BY 4.0 (attribution required)
- **Verification scripts:** MIT License
- **Test harness:** Proprietary (to prevent gaming)

---

## Changelog

### r1.0 (2025-10-25)
- Initial public release
- 10 production-ready specs
- 5-gate validation
- Cryptographic signing
- Bauform baseline: 10/10 pass

---

**Last Updated:** 2025-10-27  
**Benchmark Version:** 1.0  
**Bauform Version:** r1.0

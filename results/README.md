# Bauform R1.0 Benchmark Results

## Final Scores (Full 5-Gate Validation)

| System | Score | Pass Rate | Status |
|--------|-------|-----------|--------|
| **Bauform Engine** | **10/10** | **100%** | ✅ Production Ready |
| Claude Sonnet 4.5 | 0/10 | 0% | ❌ Failed Functional Gate |
| GPT-5 | 0/10 | 0% | ❌ Failed Functional Gate |

---

## What Was Tested

All three systems were evaluated on **10 production specifications** from the Bauform r1.0 suite:

1. CSV Validator v2
2. CSV Transformer v2  
3. JSON Validator v2
4. Email Validator v2
5. Invoice Matcher v2
6. Name Deduper v2
7. Record Paginator v2
8. REST API Echo v2
9. Text Analyzer v2
10. URL Fetcher v2

---

## Evaluation Methodology

### The 5-Gate Architecture

Each generated tool must pass **all 5 gates** to achieve "production-ready" status:

1. **✅ Functional** - Passes golden path test cases with correct outputs
2. **🛡️ Security** - Blocks adversarial inputs (CSV injection, path traversal, SSRF, JSON bombs)
3. **⚡ Limits** - Enforces resource constraints (file size, row limits, timeouts)
4. **🚀 Latency** - Meets performance targets (p50, p95, p99 under load)
5. **🔄 Stability** - Demonstrates determinism and error handling

**Production-ready verdict requires passing ALL 5 gates.**

---

## Results by System

### Bauform Engine: 10/10 ✅

All 10 specs achieved production-ready status:

| Spec | Verdict | Gates Passed |
|------|---------|--------------|
| csv_validator_v2 | ✅ production-ready | 5/5 |
| csv_transformer_v2 | ✅ production-ready | 5/5 |
| json_validator_v2 | ✅ production-ready | 5/5 |
| email_validator_v2 | ✅ production-ready | 5/5 |
| invoice_matcher_v2 | ✅ production-ready | 5/5 |
| name_deduper_v2 | ✅ production-ready | 5/5 |
| record_paginator_v2 | ✅ production-ready | 5/5 |
| rest_api_echo_v2 | ✅ production-ready | 5/5 |
| text_analyzer_v2 | ✅ production-ready | 5/5 |
| url_fetcher_v2 | ✅ production-ready | 5/5 |

**Result files:** `bauform/r1.0/*.json`

---

### Claude Sonnet 4.5: 0/10 ❌

All specs failed at the functional gate:

| Spec | Verdict | Reason |
|------|---------|--------|
| csv_validator_v2 | ❌ needs-improvement | No `/process` endpoint |
| csv_transformer_v2 | ❌ needs-improvement | No `/process` endpoint |
| json_validator_v2 | ❌ needs-improvement | No `/process` endpoint |
| email_validator_v2 | ❌ needs-improvement | No `/process` endpoint |
| invoice_matcher_v2 | ❌ needs-improvement | No `/process` endpoint |
| name_deduper_v2 | ❌ needs-improvement | No `/process` endpoint |
| record_paginator_v2 | ❌ needs-improvement | No `/process` endpoint |
| rest_api_echo_v2 | ❌ needs-improvement | No `/process` endpoint |
| text_analyzer_v2 | ❌ needs-improvement | No `/process` endpoint |
| url_fetcher_v2 | ❌ needs-improvement | No `/process` endpoint |

**Issue:** Claude generated Streamlit web UIs instead of REST APIs with programmatic `/process` endpoints as specified in the requirements.

**Result files:** `claude-sonnet-4-5/r1.0/*.json`

---

### GPT-5: 0/10 ❌

All specs failed at the functional gate:

| Spec | Verdict | Reason |
|------|---------|--------|
| csv_validator_v2 | ❌ needs-improvement | No `/process` endpoint |
| csv_transformer_v2 | ❌ needs-improvement | No `/process` endpoint |
| json_validator_v2 | ❌ needs-improvement | No `/process` endpoint |
| email_validator_v2 | ❌ needs-improvement | No `/process` endpoint |
| invoice_matcher_v2 | ❌ needs-improvement | No `/process` endpoint |
| name_deduper_v2 | ❌ needs-improvement | No `/process` endpoint |
| record_paginator_v2 | ❌ needs-improvement | No `/process` endpoint |
| rest_api_echo_v2 | ❌ needs-improvement | No `/process` endpoint |
| text_analyzer_v2 | ❌ needs-improvement | No `/process` endpoint |
| url_fetcher_v2 | ❌ needs-improvement | No `/process` endpoint |

**Issue:** GPT-5 generated Streamlit web UIs instead of REST APIs with programmatic `/process` endpoints as specified in the requirements.

**Result files:** `gpt-5/r1.0/*.json`

---

## Key Findings

### 1. Specification Compliance

**Bauform** correctly interpreted requirements and generated production-ready REST APIs with proper endpoints, security, and resource management.

**Claude & GPT-5** both misinterpreted requirements and generated interactive web UIs (Streamlit apps) instead of programmatic APIs. While these UIs may be functional for human users, they don't meet the specification requirements for REST API endpoints.

### 2. Production Readiness

The benchmark reveals a critical gap: **generating code that works in demos ≠ generating production-ready systems**.

- Interactive UIs can look impressive but fail functional requirements
- Security, limits, latency, and stability gates were never reached because functional requirements weren't met
- Only Bauform generated code that could be deployed and used programmatically

### 3. Test Rigor

This benchmark uses **binary pass/fail scoring** with **all 5 gates required**. This differs from academic benchmarks that use partial credit or only test basic functionality.

---

## Reproduction

All result files include:
- Cryptographic hashes (SHA256) of code and specs
- Ed25519 signatures for verification
- Timestamp metadata
- Complete gate-by-gate breakdown
- Performance metrics (latency, throughput, resource usage)

To verify results:
```bash
cd bauform-evals/results
find . -name "*.json" -exec cat {} \; | jq -r '.spec_id + ": " + .verdict'
```

Expected output:
- Bauform: 10x "production-ready"
- Claude: 10x "needs-improvement"
- GPT-5: 10x "needs-improvement"

---

## Timestamps

- **Bauform Evaluation**: October 23-28, 2025
- **Claude Evaluation**: October 28, 2025, 05:14 UTC
- **GPT-5 Evaluation**: October 28, 2025, 05:14 UTC

---

## Conclusion

Bauform Engine achieves **100% production-ready status** on the r1.0 benchmark suite, while Claude Sonnet 4.5 and GPT-5 both score **0%** due to fundamental spec compliance failures.

This demonstrates that **current frontier models struggle with production requirements** even when those requirements are explicitly stated. The gap between "generates code" and "generates production-ready code" remains significant.

---

**Evaluation Suite**: bauform-evals r1.0  
**Methodology**: Full 5-gate validation (functional, security, limits, latency, stability)  
**Standard**: Binary pass/fail (production either works or it doesn't)


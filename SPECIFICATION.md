# Bauform Benchmark Technical Specification

**Version:** 1.0  
**Status:** Public  
**Last Updated:** 2025-10-27

---

## Table of Contents

1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Five-Gate Architecture](#five-gate-architecture)
4. [Specification Format](#specification-format)
5. [Validation Methodology](#validation-methodology)
6. [Scoring System](#scoring-system)
7. [Anti-Gaming Measures](#anti-gaming-measures)
8. [Cryptographic Verification](#cryptographic-verification)
9. [Future Roadmap](#future-roadmap)

---

## Overview

The Bauform Production Readiness Benchmark measures whether code generation systems can produce **deployable, secure, performant code** - not just code that compiles or passes unit tests.

### Design Goals

1. **Production focus:** Test real-world utility, not academic exercises
2. **Comprehensive validation:** Security, performance, reliability, not just correctness
3. **Binary scoring:** Either production-ready or not (no partial credit)
4. **Tamper-proof:** Cryptographic signatures prevent cherry-picking
5. **Reproducible:** Clear methodology, deterministic tests

### What This Measures

| Dimension | How We Test |
|-----------|-------------|
| **Correctness** | Golden test cases (100% pass required) |
| **Security** | Adversarial inputs (CSV injection, SSRF, etc.) |
| **Robustness** | Limit enforcement (413/400 responses) |
| **Performance** | Load testing (p95 latency, throughput) |
| **Stability** | Resource tracking (memory, CPU, determinism) |

---

## Design Principles

### 1. Production Reality Over Academic Purity

```python
# Traditional benchmarks
def fibonacci(n):
    return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)

# Bauform benchmark
def validate_csv(file_path, schema, size_limit_mb=10):
    """
    Validate CSV against schema with:
    - Encoding detection
    - Size limit enforcement → 413
    - CSV injection blocking (=, +, @, -)
    - Path traversal protection
    - Streaming for large files
    - Performance target: p95 < 200ms
    """
```

Real developers need CSV validators, not fibonacci implementations.

### 2. Binary Scoring (No Partial Credit)

Production software either ships or it doesn't.

```python
if all_gates_passed:
    verdict = "production-ready"  # 1 point
else:
    verdict = "needs-improvement"  # 0 points
```

A CSV validator that passes 98% of tests but allows CSV injection is **not production-ready**.

### 3. Defense Against Gaming

Benchmark-specific optimizations defeat the purpose:

```python
# This would game the benchmark
if input == "specific_test_case":
    return hardcoded_expected_output

# We detect this through:
- Randomized test data (seeded)
- Hidden test cases  
- Behavioral analysis
- Multiple validation runs
```

### 4. Transparency With Protection

- **Public:** Specs, results, verification tools
- **Private:** Test harness implementation, exact test cases

This prevents gaming while allowing reproduction.

---

## Five-Gate Architecture

Every generated tool must pass **all five gates** sequentially. Fail any gate → immediate `needs-improvement` verdict.

### Gate 1: Functional Correctness

**Purpose:** Does it work on valid inputs?

**Tests:**
- Golden test cases (hand-crafted correct examples)
- Edge cases (empty inputs, boundary values)
- Format validation (correct output structure)
- Determinism check (same input → same output across 3 runs)

**Example (CSV Validator):**
```python
# Golden cases
valid_csv_simple = "name,age\nAlice,30\nBob,25"
valid_csv_quoted = 'name,age\n"Smith, John",45'
valid_csv_unicode = "name,city\nPierre,Montréal"

# Must return: {"valid": true, "rows": N}
```

**Pass criteria:**
- 100% of golden cases pass
- Correct output format
- HTTP 200 status codes
- Consistent results across runs

### Gate 2: Security Hardening

**Purpose:** Does it block malicious inputs?

**Attack vectors tested:**

```python
security_tests = {
    "csv_injection": [
        "=1+1",                    # Formula injection
        "+cmd|'/C calc'!A0",       # Command injection
        "@SUM(1,2)",               # Function injection
        "-2+3"                     # Negative formula
    ],
    
    "path_traversal": [
        "../../etc/passwd",
        "..\\..\\windows\\win.ini",
        "%2e%2e/%2e%2e/secret",
        "/proc/self/environ"
    ],
    
    "ssrf": [
        "http://127.0.0.1/",
        "http://10.0.0.1/",
        "http://169.254.169.254/latest/meta-data/",
        "http://metadata.google.internal/"
    ],
    
    "json_depth_bomb": [
        '{"a":' * 128 + 'null' + '}' * 128
    ],
    
    "command_injection": [
        "; ls -la",
        "| cat /etc/passwd",
        "$(whoami)",
        "`id`"
    ]
}
```

**Pass criteria:**
- All malicious inputs rejected or sanitized
- No code execution
- No data exfiltration
- Appropriate error responses (400/403)

### Gate 3: Limit Enforcement

**Purpose:** Does it enforce resource limits?

**Tests:**
```python
limit_tests = {
    "file_size": {
        "test": "Submit 15MB file (limit: 10MB)",
        "expected": "HTTP 413 Payload Too Large"
    },
    
    "row_count": {
        "test": "Submit 50,000 rows (limit: 10,000)",
        "expected": "HTTP 413"
    },
    
    "json_depth": {
        "test": "Submit 200-level nested JSON (limit: 100)",
        "expected": "HTTP 400 Bad Request"
    },
    
    "request_timeout": {
        "test": "Processing takes >30 seconds",
        "expected": "HTTP 504 or graceful termination"
    }
}
```

**Pass criteria:**
- Size limits enforced correctly
- Appropriate HTTP status codes
- No crashes or hangs
- Clean error messages

### Gate 4: Performance

**Purpose:** Is it fast enough for production?

**Methodology:**
```python
load_test_config = {
    "warm_up_requests": 50,           # Prime caches
    "test_requests": 200,              # Measure these
    "concurrency": 10,                 # Concurrent connections
    "target_p95_ms": 200,              # 95th percentile latency
    "target_p99_ms": 500               # 99th percentile latency
}
```

**Metrics collected:**
- **p50 latency:** Median response time
- **p95 latency:** 95th percentile (primary metric)
- **p99 latency:** 99th percentile
- **Throughput:** Requests per second at 10cc
- **Cold start:** First request latency vs. steady state

**Pass criteria:**
- p95 latency ≤ target (varies by spec, typically 200-500ms)
- p99 latency ≤ 2× p95
- Cold start ≤ 3× steady state p95
- No timeouts under load

### Gate 5: Resource Stability

**Purpose:** Does it behave reliably over time?

**Tests:**
```python
stability_checks = {
    "memory_stability": {
        "test": "Process 100 requests",
        "check": "Memory usage stable (no leaks)",
        "threshold": "< 20% growth from baseline"
    },
    
    "cpu_usage": {
        "test": "Measure CPU-seconds per request",
        "check": "Reasonable CPU consumption",
        "threshold": "< 1 CPU-second per request"
    },
    
    "determinism": {
        "test": "Process same input 3 times",
        "check": "Identical outputs",
        "threshold": "100% match"
    },
    
    "error_recovery": {
        "test": "Bad request followed by good request",
        "check": "Clean recovery, no state corruption",
        "threshold": "Good request succeeds"
    }
}
```

**Pass criteria:**
- No memory leaks
- Bounded CPU usage
- Deterministic outputs (where applicable)
- Clean error recovery
- No resource exhaustion

---

## Specification Format

### Current Format (r1.0)

Minimal text format:

```
Specification: csv_validator_v2
```

With companion files:
- `limits.json`: Resource constraints
- `result.json`: Test results
- `result.json.signed`: Cryptographic proof

### Future Format (r2.0+)

Comprehensive YAML format:

```yaml
spec:
  id: "csv_validator_v3"
  name: "CSV Validator with Encoding Detection"
  version: "3.0"
  category: "data_processing"
  
  description: |
    Validate CSV files against a schema with automatic encoding detection.
    Must handle various encodings (UTF-8, Latin-1, Windows-1252), detect
    and block CSV injection attacks, enforce size limits, and provide
    clear error messages.
  
  functional_requirements:
    - "Parse CSV with automatic encoding detection"
    - "Validate against provided JSON schema"
    - "Handle quoted fields with embedded commas"
    - "Support Unicode characters"
    - "Return detailed validation report"
  
  security_requirements:
    - "Block CSV formula injection (=, +, @, -)"
    - "Prevent path traversal in file operations"
    - "Sanitize error messages (no path disclosure)"
    - "Validate schema before use"
  
  constraints:
    max_file_size_mb: 10
    max_row_count: 10000
    timeout_seconds: 30
    max_memory_mb: 256
  
  performance_targets:
    p95_latency_ms: 200
    p99_latency_ms: 500
    throughput_rps: 50
    cold_start_ms: 1000
  
  test_data:
    golden_cases_dir: "test_data/csv_validator_v3/golden/"
    edge_cases_dir: "test_data/csv_validator_v3/edges/"
    security_cases_dir: "test_data/csv_validator_v3/security/"
  
  validation_gates:
    functional:
      - all_golden_cases_pass
      - edge_cases_handled
      - correct_output_format
      - deterministic_behavior
    
    security:
      - csv_injection_blocked
      - path_traversal_prevented
      - no_information_disclosure
      - schema_validation
    
    limits:
      - file_size_limit_enforced
      - row_count_limit_enforced
      - returns_413_on_oversize
      - graceful_timeout_handling
    
    performance:
      - p95_under_target
      - throughput_meets_minimum
      - cold_start_acceptable
      - no_performance_regression
    
    stability:
      - no_memory_leaks
      - bounded_cpu_usage
      - deterministic_outputs
      - clean_error_recovery
```

---

## Validation Methodology

### Test Execution Flow

```python
def validate_spec(generated_code, spec):
    """
    Sequential gate validation. Stop on first failure.
    """
    # Deploy code
    deployment = deploy_to_test_environment(generated_code)
    
    # Gate 1: Functional
    functional_result = test_functional(deployment, spec)
    if not functional_result.passed:
        return Result(verdict="needs-improvement", failed_gate=1)
    
    # Gate 2: Security
    security_result = test_security(deployment, spec)
    if not security_result.passed:
        return Result(verdict="needs-improvement", failed_gate=2)
    
    # Gate 3: Limits
    limits_result = test_limits(deployment, spec)
    if not limits_result.passed:
        return Result(verdict="needs-improvement", failed_gate=3)
    
    # Gate 4: Performance
    performance_result = test_performance(deployment, spec)
    if not performance_result.passed:
        return Result(verdict="needs-improvement", failed_gate=4)
    
    # Gate 5: Stability
    stability_result = test_stability(deployment, spec)
    if not stability_result.passed:
        return Result(verdict="needs-improvement", failed_gate=5)
    
    # All gates passed
    return Result(
        verdict="production-ready",
        metrics={
            "functional": functional_result.metrics,
            "security": security_result.metrics,
            "performance": performance_result.metrics,
            "stability": stability_result.metrics
        }
    )
```

### Test Environment

```python
test_environment = {
    "isolation": "Docker container per test",
    "network": "Isolated test network",
    "resources": {
        "cpu_limit": "1 core",
        "memory_limit": "512MB",
        "storage_limit": "1GB"
    },
    "monitoring": {
        "metrics": "Prometheus",
        "logs": "Captured for analysis",
        "traces": "Optional distributed tracing"
    }
}
```

---

## Scoring System

### Primary Metric: Production-Ready Count

```python
def calculate_score(results):
    production_ready_count = sum(
        1 for r in results 
        if r.verdict == "production-ready"
    )
    
    total_specs = len(results)
    
    return {
        "production_ready": production_ready_count,
        "total": total_specs,
        "pass_rate": production_ready_count / total_specs
    }
```

**Example:**
- **Bauform r1.0:** 10/10 (100%)
- **System X:** 7/10 (70%)
- **System Y:** 4/10 (40%)

### Secondary Metrics (For Analysis)

Collected for passed specs only:

```json
{
  "generation_metrics": {
    "avg_generation_time_seconds": 45.2,
    "avg_iterations": 1.3,
    "avg_cost_usd": 0.12
  },
  
  "performance_metrics": {
    "avg_p95_latency_ms": 145,
    "avg_throughput_rps": 67.3,
    "avg_memory_mb": 112
  },
  
  "reliability_metrics": {
    "determinism_rate": 1.0,
    "error_recovery_rate": 1.0
  }
}
```

These are **not** used for scoring - only for analysis and comparison.

---

## Anti-Gaming Measures

### 1. Test Data Randomization

```python
def generate_test_data(spec_id, date_seed):
    """
    Generate deterministic but daily-rotating test data
    """
    seed = f"{spec_id}-{date_seed}"
    random.seed(seed)
    
    return {
        "golden": generate_golden_cases(seed),
        "edges": generate_edge_cases(seed),
        "security": generate_security_cases(seed)
    }
```

### 2. Hidden Test Cases

```python
test_suite = {
    "public": load_test_cases("public/"),    # 70% of tests
    "private": load_test_cases("private/")   # 30% of tests (not published)
}
```

Private tests prevent training on exact test cases.

### 3. Hardcoded Response Detection

```python
def detect_hardcoding(code):
    """
    Flag suspicious patterns that suggest hardcoding
    """
    suspicious_patterns = [
        r'"expected_output_\d+"',    # Hardcoded expected outputs
        r'if.*test.*case',            # Test case branching
        r'benchmark.*specific',       # Benchmark-specific code
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return True
    return False
```

### 4. Behavioral Consistency

```python
def verify_consistency(deployment, test_cases):
    """
    Run tests multiple times with variations
    """
    base_results = run_tests(deployment, test_cases)
    
    # Permute test data slightly
    permuted_cases = permute_test_data(test_cases)
    permuted_results = run_tests(deployment, permuted_cases)
    
    # Results should be consistent
    return verify_logical_equivalence(base_results, permuted_results)
```

---

## Cryptographic Verification

### Signature Scheme

**Algorithm:** Ed25519 (fast, secure, deterministic)

**What We Sign:**
- Complete `result.json` file
- Includes all metrics, timestamps, verdicts
- Tamper-evident: Any modification invalidates signature

### Signing Process

```python
from nacl.signing import SigningKey

def sign_result(result_json_path, private_key_hex):
    """
    Sign a result file with Ed25519
    """
    # Load private key
    signing_key = SigningKey(private_key_hex, encoder=HexEncoder)
    
    # Read result file
    with open(result_json_path, 'rb') as f:
        result_bytes = f.read()
    
    # Sign (includes result + signature)
    signed = signing_key.sign(result_bytes)
    
    # Write signed file
    with open(f"{result_json_path}.signed", 'wb') as f:
        f.write(signed)
```

### Verification Process

```python
from nacl.signing import VerifyKey

def verify_result(signed_path, public_key_hex):
    """
    Verify a signed result file
    """
    # Load public key
    verify_key = VerifyKey(public_key_hex, encoder=HexEncoder)
    
    # Read signed file
    with open(signed_path, 'rb') as f:
        signed_data = f.read()
    
    # Verify (raises exception if invalid)
    try:
        original = verify_key.verify(signed_data)
        return json.loads(original)
    except nacl.exceptions.BadSignatureError:
        raise ValueError("Invalid signature - result has been tampered with")
```

### What Signatures Prevent

✅ **Prevents:**
- Cherry-picking best runs (must sign all results)
- Modifying metrics after the fact
- Claiming results from other systems

❌ **Does NOT prevent:**
- Gaming the benchmark through code optimization
- Training on test data
- Running hundreds of times and signing the best set

Additional anti-gaming measures address these.

---

## Future Roadmap

### r2.0 (Planned)

**Additions:**
- 10 more specs (total: 20)
- Deployment validation layer
- Sustained stress testing (5-minute load)
- API integration specs
- More detailed YAML spec format

**Changes:**
- Enhanced anti-gaming (more private tests)
- Improved test data generation
- Better documentation

### r3.0 (Future)

**Additions:**
- Multi-language support (JavaScript, Go, Rust)
- UI/UX testing for frontend generation
- Integration testing (multi-service specs)
- Long-running stability tests (24-hour endurance)

---

## Contact & Contributions

- **Issues:** GitHub issues for technical questions
- **Submissions:** See CONTRIBUTING.md
- **Email:** gavinedwards1004@gmail.com

---

**Last Updated:** 2025-10-27  
**Specification Version:** 1.0  
**Benchmark Version:** r1.0


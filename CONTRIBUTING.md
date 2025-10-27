# Contributing to Bauform Benchmark

We welcome submissions from other code generation systems!

---

## Submission Guidelines

### What We Accept

✅ **Full benchmark runs:** All 10 r1.0 specs  
✅ **Reproducible methodology:** Clear documentation of your approach  
✅ **Cryptographic signatures:** Sign your results with Ed25519  
✅ **Honest reporting:** Include all runs, no cherry-picking  

❌ **Partial results:** Can't submit only your best specs  
❌ **Modified specs:** Use specs exactly as provided  
❌ **Incomplete data:** Must include all required fields  

---

## How to Submit Results

### Step 1: Generate Code for All Specs

```bash
# Clone the benchmark
git clone https://github.com/tekodu/bauform-evals
cd bauform-evals/r0.1/r1.0

# For each spec:
for spec in */spec.txt; do
    echo "Generating for $spec"
    your_system generate --input "$spec" --output "generated_$(basename $(dirname $spec)).py"
done
```

### Step 2: Test Your Generated Code

You must test your generated code using your own harness. At minimum, test:

1. **Functional correctness:** Does it work on valid inputs?
2. **Security:** Does it block malicious inputs?
3. **Error handling:** Does it handle invalid inputs gracefully?
4. **Performance:** What's the p95 latency under load?

Document your testing methodology clearly.

### Step 3: Create Result Files

For each spec, create a `result.json`:

```json
{
  "schema": "bauform-evals/v1.1",
  "spec_id": "csv_validator_v2",
  "suite_id": "r1.0",
  "system": "your_system_name",
  "system_version": "1.0",
  "timestamp_utc": "2025-10-27T12:00:00Z",
  
  "verdict": "production-ready",
  
  "gates": {
    "functional": {"passed": true, "details": "All 100 golden cases passed"},
    "security": {"passed": true, "details": "All 14 malicious inputs blocked"},
    "limits": {"passed": true, "details": "413 returned for oversized inputs"},
    "performance": {"passed": true, "details": "p95 = 145ms (target: 200ms)"},
    "stability": {"passed": true, "details": "Deterministic across 3 runs"}
  },
  
  "metrics": {
    "latency_ms": {"p50": 89, "p95": 145, "p99": 198},
    "throughput_rps": {"steady_10cc": 67.3},
    "resources": {"max_rss_mb": 112, "cpu_user_s": 1.4}
  },
  
  "generation": {
    "time_seconds": 45.2,
    "iterations": 1,
    "cost_usd": 0.15
  },
  
  "methodology": {
    "test_framework": "pytest + docker",
    "load_generator": "locust",
    "test_duration_minutes": 10,
    "environment": "AWS EC2 t3.medium"
  }
}
```

**Required fields:**
- `schema`, `spec_id`, `suite_id`, `system`, `system_version`, `timestamp_utc`
- `verdict`: One of `production-ready`, `needs-improvement`, `failed`
- `gates`: All 5 gates with pass/fail and details
- `methodology`: How you tested

### Step 4: Sign Your Results

Generate an Ed25519 keypair:

```bash
python3 << 'EOF'
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder

sk = SigningKey.generate()
pk = sk.verify_key

print(f"Private key: {sk.encode(encoder=HexEncoder).decode()}")
print(f"Public key: {pk.encode(encoder=HexEncoder).decode()}")
EOF
```

Save your keys securely:
```bash
echo "YOUR_PRIVATE_KEY_HEX" > private_key.txt
chmod 600 private_key.txt
echo "YOUR_PUBLIC_KEY_HEX" > public_key.txt
```

Sign each result:
```bash
python3 << 'EOF'
import json
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder

# Load private key
with open('private_key.txt') as f:
    privkey_hex = f.read().strip()
signing_key = SigningKey(privkey_hex, encoder=HexEncoder)

# Sign result
with open('result.json', 'rb') as f:
    result_bytes = f.read()

signed = signing_key.sign(result_bytes)

# Create signed file
with open('result.json.signed', 'wb') as f:
    f.write(signed)

print("Created result.json.signed")
EOF
```

### Step 5: Submit a Pull Request

```bash
# Create your results directory
mkdir -p submissions/your_system_name/r1.0

# Copy all signed results
cp csv_validator_v2/result.json.signed submissions/your_system_name/r1.0/
# ... repeat for all 10 specs

# Add metadata
cat > submissions/your_system_name/SYSTEM.md << 'EOF'
# Your System Name

**Version:** 1.0
**Type:** [Transformer/Agent/Hybrid]
**Model:** [Base model used, if applicable]
**Website:** [URL]

## Methodology

[Describe how you generated and tested the code]

## Public Key

[Your Ed25519 public key in hex]

## Contact

[Email or GitHub]
EOF

# Create PR
git checkout -b submission-your-system-name
git add submissions/your_system_name/
git commit -m "Add benchmark results for YourSystem v1.0"
git push origin submission-your-system-name
```

Open a pull request with:
- **Title:** `[Submission] YourSystem v1.0 - X/10 production-ready`
- **Description:** Link to your SYSTEM.md and summary of results

---

## Verification Process

We will:

1. ✅ Verify all signatures using your public key
2. ✅ Check that all 10 specs are included
3. ✅ Validate JSON schema compliance
4. ✅ Review methodology for reasonableness
5. ✅ Spot-check claims (may regenerate with your system)

If everything checks out, we'll:
- Merge your PR
- Add you to the leaderboard in README.md
- Update comparative charts

---

## Best Practices

### DO:
- **Be honest:** Report actual results, not aspirational ones
- **Be thorough:** Test all specs, not just easy ones
- **Be reproducible:** Document methodology clearly
- **Be transparent:** Include failures and limitations

### DON'T:
- **Cherry-pick:** Submit only your best results
- **Game the benchmark:** Hardcode responses to test cases
- **Modify specs:** Use them exactly as provided
- **Fake signatures:** We'll catch it

---

## Scoring Interpretation

### Verdict Values

| Verdict | Meaning | Criteria |
|---------|---------|----------|
| `production-ready` | ✅ All 5 gates passed | Deploy with confidence |
| `needs-improvement` | ⚠️ Some gates failed | Works but has issues |
| `failed` | ❌ Major gate failures | Not usable |

### Gate Failures

Common failure patterns:

**Functional failures:**
- Incorrect output format
- Logic errors
- Edge case mishandling

**Security failures:**
- CSV injection not blocked
- Path traversal allowed
- SSRF vulnerabilities

**Limit failures:**
- No payload size limits
- Doesn't return 413
- Hangs on large inputs

**Performance failures:**
- Too slow (>500ms p95)
- Memory leaks
- Poor throughput

**Stability failures:**
- Non-deterministic outputs
- Flaky behavior
- Resource exhaustion

---

## Example Submissions

See `submissions/bauform/` for a complete example of:
- Result JSON format
- Signing process
- Methodology documentation
- SYSTEM.md structure

---

## Questions?

- **Technical issues:** Open a GitHub issue
- **Methodology questions:** Email gavinedwards1004@gmail.com
- **Clarifications:** Check README.md first

---

## Code of Conduct

Be professional. Be honest. Be respectful.

We reserve the right to reject submissions that:
- Violate academic integrity
- Use deceptive practices
- Game the benchmark
- Are not made in good faith

---

## Updates to Benchmark

When we release r2.0 with more specs, we'll:
- Maintain r1.0 results for historical comparison
- Accept new r2.0 submissions
- Not require resubmission of r1.0 results

---

**Thank you for contributing to rigorous evaluation of code generation systems!**

Last updated: 2025-10-27


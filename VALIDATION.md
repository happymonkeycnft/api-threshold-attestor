# Local validation report

### Architecture

Standalone zero-LLM contract. Each validator fetches HTTPS JSON, parses exact numeric tokens, compares scaled integers and hashes raw response bytes. Custom consensus requires exact material equality.

### Public interface

Exactly four methods: create_attestation and resolve_attestation (write); get_attestation and get_attestation_count (view). SDK schema and semantic validation confirm 2 write / 2 view.

### Storage model

TreeMap[u256, Attestation] plus u256 count. Records include every requested field, availability and condition_met. IDs start at 1. ATTESTED records have no mutation path.

### Numeric normalization

JSON parse_int/parse_float callbacks capture lexical tokens without creating floats. Reject numeric strings, booleans, null, exponents and nonfinite constants. Strip leading zeros, trailing fractional zeros and negative zero; compare exact integers scaled by 10^18. Duplicate JSON keys are rejected.

### Request commitment

SHA-256 over four-byte big-endian length-prefixed UTF-8 fields: api-threshold-attestor:v1, ID, lowercase creator wallet, normalized URL, accepted path, operator, normalized threshold, context. Independent reference and field-change tests pass.

### Response fingerprint

SHA-256 over exact bounded SDK response body bytes, before UTF-8 decoding; no JSON reserialization. Whitespace differences cause disagreement. Headers are not hashed.

### Availability semantics

Unavailable fetch, bad status/MIME/UTF-8/JSON/path/value/size returns UNAVAILABLE and preserves every field of the PENDING record. Retry succeeds in both direct tests and GLSim.

### Result semantics

ABOVE, BELOW, EQUAL express numeric relationship independently of the operator. UNAVAILABLE is transient and never a final stored classification.

### condition_met behavior

True exactly when the relationship matches >, < or ==. Defaults to false while PENDING and must be interpreted only with status ATTESTED.

### LLM calls

0, statically checked and dynamically guarded in tests.

### Response size bound

65,536 bytes accepted. Exact boundary and oversized cases pass. Limit is post-fetch; SDK buffering/download is not capped by this contract.

### Decimal precision limit

18 fractional digits, 60 integer digits, checked before zero normalization; no rounding.

### Direct tests

99 passed using the proven RC environment. Full suite: 104 passed including five GLSim scenarios. See reports/tests.txt.

### GLSim ABOVE

PASS: 125 vs 100, FINALIZED, five agree, ATTESTED / ABOVE.

### GLSim BELOW

PASS: 75 vs 100, FINALIZED, five agree, ATTESTED / BELOW.

### GLSim EQUAL

PASS: 100 vs 100, FINALIZED, five agree, ATTESTED / EQUAL.

### GLSim UNAVAILABLE

PASS: missing field, five agree, PENDING record byte-for-field unchanged; subsequent retry FINALIZED / ABOVE with five agree.

### Disagreement test

PASS: same numeric value with differing raw response whitespace produces five disagree votes, UNDETERMINED, and unchanged PENDING storage. Direct tests also reject different values and availability. GLSim uses a leader plus five checking validators, mocked HTTP, and no hosted RPC.

### GenVM lint

PASS: 3 checks with GENVM_VERSION=v0.6.0-rc6. SDK dependency pinned in source.

### Semantic/interface validation

PASS: APIThresholdAttestor; four methods confirmed by SDK semantic validator, schema extraction and independent AST audit.

### Closure/storage safety

PASS: copy_to_memory precedes nondeterministic work; callbacks capture primitive request strings, never self/row/storage. AST audit, direct check_pickling and actual GLSim execute successfully. Writes occur after accepted result validation.

### Source bytes

9608

### Source SHA-256

2716f8e6b116505a9bc006505c4cc2f983e706551782be8d0c913513e95820d0

### Candidate live APIs

1. https://api.frankfurter.dev/v1/2025-01-02?base=EUR&symbols=USD — rates.USD; JSON number; small historical central-bank-derived FX evidence. v1 is deprecated but documented to continue working. Source: https://frankfurter.dev/v1/

2. https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson — metadata.count; JSON integer; authoritative USGS count, typically small. Generated timestamps may prevent exact agreement. Source: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

Documentation reviewed; endpoints were not live-verified through GenVM. No rate-limit guarantee. Neither is hardcoded.

### README status

Complete: README.md covers methods, provenance, storage, determinism, limitations, test reproduction, candidates and later network target.

### Builder one-liner

A GenLayer Intelligent Contract that verifies numeric values from public APIs against on-chain thresholds with deterministic validator consensus.

### Builder description

API Threshold Attestor lets a wallet commit to a public HTTPS JSON endpoint, dictionary field path, operator and threshold. Independent GenLayer validators fetch the live public API data and use deterministic decimal comparison to agree on ABOVE, BELOW or EQUAL, whether the requested condition was met, and an exact response fingerprint. It has no LLM dependency.

Successful resolutions become immutable attestations with wallet-bound request provenance. Unavailable, malformed or unsupported data leaves the request PENDING for retry. This reusable primitive supports prices, supply, TVL, metrics and statistics wherever a compatible public JSON API exposes a numeric field.

### Expected verification outcome

Creating an attestation stores a wallet-bound commitment to the API, field path, operator, and threshold. Resolving causes GenLayer validators to fetch the JSON response, agree on the exact response fingerprint and normalized numeric value, and persist ABOVE, BELOW, or EQUAL plus whether the requested condition was met. Unavailable or invalid API data leaves the record PENDING for retry.

### Remaining limitations

Local validation uses HTTP fixtures; hosted compatibility and live access remain unverified. APIs may change; exact whole-body fingerprints can disagree despite identical selected values. URL checks enforce a public-looking hostname, not DNS rebinding/redirect protection. Response size is checked after fetch. No observed timestamp or raw response is persisted. Authority, accuracy, API ownership and historical permanence are not guaranteed. Dictionary paths only; numeric strings and exponent notation unsupported. Credential-pattern scan PASS; Python compile PASS under RC runtime; staged git diff --check PASS. Separate local repository initialized; no existing project edited. No faucet, signing, hosted deployment, push, frontend or Builder submission.

### Ready for Studio-dev deployment: YES / NO

YES — ready for a separately authorized Studio-dev validation deployment on chain 61997 at https://studio-dev.genlayer.com/api. This is local readiness, not a claim of hosted validation. Deployment has not been performed.

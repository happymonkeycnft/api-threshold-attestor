# API Threshold Attestor

## What it does

Verifies a numeric public HTTPS JSON API value against a wallet-committed threshold and stores an immutable attestation. Requests start PENDING and become ATTESTED only after successful consensus. IDs start at 1. Anyone may resolve a pending request.

## Why GenLayer

Independent validators fetch the live API and agree on the normalized observed value, relationship to threshold, condition result, and exact response fingerprint. No source is hardcoded.

## Zero-LLM design

No LLM is required: JSON parsing, fixed-point normalization, comparison, and evidence hashing are deterministic. JSON number tokens are captured as strings before any conversion, so binary floats never enter consensus material.

## Result semantics

- ABOVE: observed value exceeds threshold.
- BELOW: observed value is less than threshold.
- EQUAL: exact numeric equality.
- UNAVAILABLE: retry result only; all stored fields remain unchanged and status stays PENDING.

## condition_met

The relationship is independent of the requested operator. For value 120, threshold 100, and operator `<`, result is ABOVE and condition_met is false. Operators are exclusively `>`, `<`, and `==`. Before attestation, condition_met defaults to false and has no final meaning.

## Provenance

request_commitment is SHA-256 over UTF-8 fields, each prefixed by a four-byte unsigned big-endian byte length: version `api-threshold-attestor:v1`, decimal ID, lowercase creator wallet, normalized URL, exact accepted path, operator, normalized threshold, exact context. URL normalization trims ASCII outer spaces, lowercases scheme/host, removes :443 and fragments, and inserts a root slash when needed.

response_fingerprint is SHA-256 of the exact SDK response body bytes, before strict UTF-8 decoding. Whitespace and object ordering matter. This binds the entire JSON evidence, not just the extracted number; it does not bind HTTP headers. Duplicate keys and nonfinite JSON constants are rejected. Numeric strings, booleans, null, exponent notation, arrays in the selected path, and unsupported precision are unavailable.

## Limits and numeric normalization

Response acceptance limit: 65,536 bytes. HTTPS URL: 500 characters; path: 200; context: 500. Paths use dictionary keys matching `[A-Za-z_][A-Za-z0-9_]*` separated by dots. Arrays are unsupported. Decimal input allows an optional minus, integer digits and optional fractional digits. Limit: 60 integer digits and 18 fractional digits, checked before removing zeros. No exponent, plus sign, rounding, NaN or Infinity. Leading integer zeros, trailing fractional zeros and negative zero normalize away. Comparison uses arbitrary-precision integers scaled by 10^18.

## Limitations

The user chooses source authority. Commitments prove neither API ownership, accuracy, legal identity nor historical permanence. APIs can change or become unavailable. There is no historical guarantee unless the API supplies historical data. No observation timestamp or raw response is stored; transaction history supplies resolution ordering. Exact fingerprints may prevent agreement on APIs containing changing timestamps or unstable formatting, even when their selected values match.

The body bound is enforced after the SDK fetch: it bounds parsing, hashing and accepted evidence, not network download or SDK buffering. Hostname validation rejects credentials, literal IPs, custom ports and common private suffixes; it is a public-looking DNS check, not DNS rebinding or redirect protection. Network-level destination protection remains the GenVM host's responsibility. The successful Studio-dev lifecycle below verifies this source on chain 61997.

## Methods

| Method | Kind | Result |
|---|---|---|
| create_attestation(api_url: str, json_path: str, operator: str, threshold: str, context: str) | write | new u256 ID |
| resolve_attestation(attestation_id: u256) | write | ABOVE / BELOW / EQUAL / UNAVAILABLE |
| get_attestation(attestation_id: u256) | view | complete record dictionary |
| get_attestation_count() | view | u256 count |

Context may be empty. Missing IDs fail. Resolving an ATTESTED record fails. No edit/delete methods exist.

## Storage

A TreeMap of u256 IDs to typed dataclass records stores ID, creator Address, API URL, path, operator, normalized threshold, context, commitment, status, availability, observed value, fingerprint, result and condition_met. Count is u256. Pending result strings are empty. Storage is copied to memory before nondeterministic work; callbacks capture only primitive strings and functions. Storage updates occur only after validating accepted consensus material.

## Testing

99 direct cases and five real in-process GLSim scenarios with mocked HTTP: ABOVE, BELOW, EQUAL, UNAVAILABLE with successful retry, and fingerprint disagreement. Each scenario uses five checking validators plus the leader. Direct cases cover creation, commitments, numeric boundaries, exact comparison, immutability, retries, serialization, and material disagreement. Zero model calls.

Use Python 3.12 and `pip install -r requirements.lock` in a dedicated virtual environment. Existing proven tooling was reused read-only for this local run:

```sh
../web-claim-attestor/.venv/bin/pytest -q
GENVM_VERSION=v0.6.0-rc6 ../web-claim-attestor/.venv/bin/genvm-lint check contracts/api_threshold_attestor.py
python3 tools/audit.py
python3 -m compileall -q contracts tests tools
```

Pinned tooling: genlayer-py 0.19.0rc2, genlayer-test 0.30.0rc2, genvm-linter 0.11.1rc2, cloudpickle 3.1.2. Contract SDK dependency hash is embedded in the source header. See reports for actual results.

## Studio-dev deployment

Studio-dev, chain ID 61997, RPC https://studio-dev.genlayer.com/api. One deployment and the create/resolve lifecycle finalized on 21 October 2026. No GitHub push or Builder submission performed. Full receipts and fee estimates: [live report](reports/STUDIO-DEV-LIVE.md).

## Candidate APIs

Candidates are documentation-reviewed, not live-verified through GenVM. Recheck response MIME, size, numeric format and cross-validator stability before hosted use.

| Endpoint | json_path | Expected type | Rationale |
|---|---|---|---|
| https://api.frankfurter.dev/v1/2025-01-02?base=EUR&symbols=USD | rates.USD | JSON number | Small historical central-bank-derived FX payload; stable date is preferable for exact fingerprint agreement. |
| https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson | metadata.count | JSON integer | Authoritative USGS count, typically small; generated timestamps can cause fingerprint disagreement across updates. |

Sources: [Frankfurter v1 documentation](https://frankfurter.dev/v1/) (v1 deprecated but documented to continue working); [USGS GeoJSON specification](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php). Rate limits and availability are not guaranteed. These endpoints are examples, not contract defaults.

## Live attestation #1

- Contract address: `0xbF58d136AC6Cc65C8EC7dD9dda8f3BcFAbaA7aC8`
- Deployment tx: `0x8ec701d421c984d95c230a91b469cd1c59b98dbe314f5928cd60f4e1ee64e18f`
- Create tx: `0x7fd2c59d59bb86631dc746852fb887f98271f2ea0627598a5c48d796d53815a6`
- Resolve tx: `0xaf7d15f17b8854718abe6317e3c8cbd61b7e60316f1fa66602a52f610503d36c`
- Selected live API: `https://api.frankfurter.dev/v1/2025-01-02?base=EUR&symbols=USD`
- json_path: `rates.USD`
- Threshold: `0.5`
- Observed value: `1.0321`
- Result: `ABOVE`
- condition_met: `true`
- Request commitment: `6420107e77cd0caf2642a6c55dbc8131adac4782ea8db9e383ff3c8246b85c76`
- Response fingerprint: `194c38362924571d5ef104b75c76a3413452437a427a8627c7e85d46416b7884`

ATTESTED / AVAILABLE; operator `>`; creator `0x4eD1d43e060e220724EE96E9c177E7548735994d`; count 1. Two independent finalized-chain reads confirmed persistence. Final receipt: three agree, two idle.

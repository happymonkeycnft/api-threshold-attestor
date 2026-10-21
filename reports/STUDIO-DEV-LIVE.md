# Studio-dev live validation

Validated 21 October 2026, Asia/Kuala_Lumpur. One deployment, one create, one resolve; each broadcast exactly once. No transaction retry.

### Source SHA-256

2716f8e6b116505a9bc006505c4cc2f983e706551782be8d0c913513e95820d0

### Deployer balance

1999762687249997531 base units (before deployment)

### Deployment feeValue

100000000000010352

### Deployment tx

0x8ec701d421c984d95c230a91b469cd1c59b98dbe314f5928cd60f4e1ee64e18f

### Deployment result

FINALIZED / accepted / FINISHED_WITH_RETURN

### Contract address

0xbF58d136AC6Cc65C8EC7dD9dda8f3BcFAbaA7aC8

### Initial count

0

### Selected live API

https://api.frankfurter.dev/v1/2025-01-02?base=EUR&symbols=USD

### json_path

rates.USD

### Pre-create observed value

1.0321

### Threshold

0.5

### Create feeValue

378511200010352

### Create tx

0x7fd2c59d59bb86631dc746852fb887f98271f2ea0627598a5c48d796d53815a6

### Attestation ID

1

### Request commitment

6420107e77cd0caf2642a6c55dbc8131adac4782ea8db9e383ff3c8246b85c76

### Resolve feeValue

381705600010352

### Resolve tx

0xaf7d15f17b8854718abe6317e3c8cbd61b7e60316f1fa66602a52f610503d36c

### Consensus result

FINALIZED / accepted / FINISHED_WITH_RETURN; 3 agree, 2 idle; no disagree votes in the final receipt.

### Final status

ATTESTED

### Availability

AVAILABLE

### Observed value

1.0321

### Result

ABOVE

### condition_met

true

### Response fingerprint

194c38362924571d5ef104b75c76a3413452437a427a8627c7e85d46416b7884

### Final balance

1999526059499995062 base units

### README updated locally: YES / NO

YES

### Live report created: YES / NO

YES

### Contract source changed: YES / NO

NO

### Ready for GitHub push: YES / NO

YES — prepared locally; no push performed.

### Ready for Builder submission: YES / NO

YES — copy prepared; no submission performed.

## Network and lifecycle evidence

Preset studioDevnet, chain 61997, canonical RPC https://studio-dev.genlayer.com/api; no Bradbury configuration. Latest/pending nonce pairs were 4/4, 5/5 and 6/6 before deploy/create/resolve. Both write calls used fresh estimateTransactionFeesForWrite; deployment used fresh estimateTransactionFees. Each supplied its returned distribution and feeValue, leaderOnly false, consensusMaxRotations 3. Signing wallet matched 0x4eD1d43e060e220724EE96E9c177E7548735994d. Source size stayed 9,608 bytes, four public methods, zero LLM calls. Deployed bytecode SHA-256 was verified before creation.

The selected API returned HTTP JSON, 70 bytes, with a supported numeric token at rates.USD. Threshold 0.5 is comfortably below the fixed historical rate 1.0321. A second awareness-only fetch preceded resolve; chain state came exclusively from readContract against latest-final. Creation was verified PENDING with ID 1 and its independently recomputed length-prefixed commitment. Both final readbacks matched every persisted field and count 1.

Receipt vote entries are reported as returned: three agree and two idle, not five executed agreement votes. All three transactions finalized successfully. Estimates are fee reservations, not actual charges. Final balance reduction across the lifecycle: 236627750002469 base units.

## Full fee estimates and balances

### deploy

```json
{
  "balance": "1999762687249997531",
  "estimate": {
    "distribution": {
      "leaderTimeunitsAllocation": "100",
      "validatorTimeunitsAllocation": "200",
      "appealRounds": "0",
      "executionBudgetPerRound": "25000000000000000",
      "executionConsumed": "0",
      "totalMessageFees": "0",
      "rotations": [
        "3"
      ],
      "maxPriceGenPerTimeUnit": "2",
      "storageFeeMaxGasPrice": "300000000",
      "receiptFeeMaxGasPrice": "300000000"
    },
    "feeValue": "100000000000010352",
    "policy": {
      "enabled": true,
      "genPerTimeUnit": "1",
      "storageUnitPrice": "250000000",
      "receiptGasPrice": "250000000",
      "executionBudgetFloor": "76548000000000",
      "timeUnitOverlayBps": "1500"
    }
  }
}
```

### create

```json
{
  "balance": "1999683981999996708",
  "estimate": {
    "distribution": {
      "leaderTimeunitsAllocation": "100",
      "validatorTimeunitsAllocation": "200",
      "appealRounds": "0",
      "executionBudgetPerRound": "94627800000000",
      "executionConsumed": "0",
      "totalMessageFees": "0",
      "rotations": [
        "3"
      ],
      "maxPriceGenPerTimeUnit": "2",
      "storageFeeMaxGasPrice": "300000000",
      "receiptFeeMaxGasPrice": "300000000"
    },
    "feeValue": "378511200010352",
    "policy": {
      "enabled": true,
      "genPerTimeUnit": "1",
      "storageUnitPrice": "250000000",
      "receiptGasPrice": "250000000",
      "executionBudgetFloor": "76548000000000",
      "timeUnitOverlayBps": "1500"
    },
    "observed": {
      "executionFeeConsumed": "78632500000000",
      "executionFeeReportTotal": "78628000000000",
      "recommendedExecutionBudgetPerRound": "188712600000000",
      "genvmMessageFeeConsumed": "0",
      "messageFeeBudget": "0",
      "messageFeeConsumed": "0",
      "messageFeeRefunded": "0",
      "internalDeclaredBudget": "0",
      "externalMessageReserved": "0",
      "externalMessageReimbursed": "0",
      "externalMessageRemainder": "0",
      "recommendedTotalMessageFees": "0"
    }
  }
}
```

### resolve

```json
{
  "balance": "1999605349499995885",
  "estimate": {
    "distribution": {
      "leaderTimeunitsAllocation": "100",
      "validatorTimeunitsAllocation": "200",
      "appealRounds": "0",
      "executionBudgetPerRound": "95426400000000",
      "executionConsumed": "0",
      "totalMessageFees": "0",
      "rotations": [
        "3"
      ],
      "maxPriceGenPerTimeUnit": "2",
      "storageFeeMaxGasPrice": "300000000",
      "receiptFeeMaxGasPrice": "300000000"
    },
    "feeValue": "381705600010352",
    "policy": {
      "enabled": true,
      "genPerTimeUnit": "1",
      "storageUnitPrice": "250000000",
      "receiptGasPrice": "250000000",
      "executionBudgetFloor": "76548000000000",
      "timeUnitOverlayBps": "1500"
    },
    "observed": {
      "executionFeeConsumed": "79290000000000",
      "executionFeeReportTotal": "79288000000000",
      "recommendedExecutionBudgetPerRound": "190293600000000",
      "genvmMessageFeeConsumed": "0",
      "messageFeeBudget": "0",
      "messageFeeConsumed": "0",
      "messageFeeRefunded": "0",
      "internalDeclaredBudget": "0",
      "externalMessageReserved": "0",
      "externalMessageReimbursed": "0",
      "externalMessageRemainder": "0",
      "recommendedTotalMessageFees": "0"
    }
  }
}
```

## Persisted attestation

```json
{
  "api_url": "https://api.frankfurter.dev/v1/2025-01-02?base=EUR&symbols=USD",
  "attestation_id": 1,
  "availability": "AVAILABLE",
  "condition_met": true,
  "context": "Controlled Studio-dev validation of historical EUR/USD threshold.",
  "creator": "0x4eD1d43e060e220724EE96E9c177E7548735994d",
  "json_path": "rates.USD",
  "observed_value": "1.0321",
  "operator": ">",
  "request_commitment": "6420107e77cd0caf2642a6c55dbc8131adac4782ea8db9e383ff3c8246b85c76",
  "response_fingerprint": "194c38362924571d5ef104b75c76a3413452437a427a8627c7e85d46416b7884",
  "result": "ABOVE",
  "status": "ATTESTED",
  "threshold": "0.5"
}
```

## Local-only unavailable coverage

No broken API case was created live. Local direct and five-validator GLSim tests establish UNAVAILABLE preserves PENDING and supports retry. No source logic changes, optimization, faucet, additional deployments, GitHub push or Builder submission occurred. Historical FX validates a live fetch of historical data, not a current FX quote. SDK fetch buffering remains outside the post-fetch response-size check.

Raw operational receipts and wallet tooling are retained locally and excluded from this repository. This report contains the publishable lifecycle evidence and complete fee estimates.

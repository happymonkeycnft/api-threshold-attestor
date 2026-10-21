# Builder submission copy

Name: API Threshold Attestor

## One-liner

A GenLayer Intelligent Contract that verifies numeric values from public APIs against on-chain thresholds with deterministic validator consensus.

## Description

API Threshold Attestor is a reusable GenLayer Intelligent Contract for threshold verification using live public JSON APIs. A creator commits an API endpoint, deterministic field path, comparison operator, and decimal threshold on-chain.

GenLayer validators independently fetch the API response, extract and normalize the numeric value, agree on the exact response fingerprint, and persist ABOVE, BELOW, or EQUAL plus whether the requested condition was met. The design uses zero LLM calls; unavailable or invalid API data leaves the attestation PENDING for a safe retry.

## Expected verification outcome

Creating an attestation stores a wallet-bound commitment to the API, field path, operator, and threshold. Resolving causes GenLayer validators to fetch the JSON response, agree on the exact response fingerprint and normalized numeric value, and persist ABOVE, BELOW, or EQUAL plus whether the requested condition was met. Unavailable or invalid API data leaves the record PENDING for retry.

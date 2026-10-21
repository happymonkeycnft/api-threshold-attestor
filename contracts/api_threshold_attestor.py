# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }
from dataclasses import dataclass
from hashlib import sha256
import json
import re
import genlayer as gl
from genlayer import Address, u256
from genlayer.storage import TreeMap, allow as allow_storage

MAX_BODY = 65536
MAX_DECIMALS = 18
MAX_INTEGER = 60


@allow_storage
@dataclass
class Attestation:
    attestation_id: u256
    creator: Address
    api_url: str
    json_path: str
    operator: str
    threshold: str
    context: str
    request_commitment: str
    status: str
    availability: str
    observed_value: str
    response_fingerprint: str
    result: str
    condition_met: bool


def _url(value: str) -> str:
    if len(value) > 500:
        raise gl.vm.UserError("URL too long")
    value = value.strip(" ")
    if not value.lower().startswith("https://"):
        raise gl.vm.UserError("Public HTTPS URL required")
    if any(ord(c) <= 32 or ord(c) >= 127 for c in value) or "\\" in value:
        raise gl.vm.UserError("Malformed URL")
    value = value.split("#", 1)[0]
    match = re.fullmatch(r"https://([^/?]+)(.*)", "https://" + value[8:])
    if match is None:
        raise gl.vm.UserError("Malformed URL")
    host, suffix = match.groups()
    host = host.lower()
    if host.endswith(":443"):
        host = host[:-4]
    labels = host.split(".")
    if (len(host) > 253 or len(labels) < 2
        or not re.fullmatch(r"[a-z]{2,63}", labels[-1])
        or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", x) for x in labels)
        or labels[-1] in ("localhost", "local", "internal", "test", "invalid", "onion")
        or re.search(r"%(?![0-9a-fA-F]{2})", suffix)):
        raise gl.vm.UserError("Public DNS hostname required")
    return "https://" + host + (suffix if suffix.startswith("/") else "/" + suffix)



class _Number(str):
    pass


def _decimal(value: str) -> str:
    if len(value) > 80 or re.fullmatch(r"-?[0-9]+(?:\.[0-9]+)?", value) is None:
        raise ValueError("Unsupported decimal")
    negative = value.startswith("-")
    whole, _, fraction = value.lstrip("-").partition(".")
    if len(whole) > MAX_INTEGER or len(fraction) > MAX_DECIMALS:
        raise ValueError("Decimal precision exceeded")
    whole = whole.lstrip("0") or "0"
    fraction = fraction.rstrip("0")
    result = whole + ("." + fraction if fraction else "")
    return ("-" if negative and result != "0" else "") + result


def _scaled(value: str) -> int:
    whole, _, fraction = value.lstrip("-").partition(".")
    number = int(whole) * 10**MAX_DECIMALS + int(fraction.ljust(MAX_DECIMALS, "0"))
    return -number if value.startswith("-") else number


def _relationship(value: str, threshold: str, operator: str) -> tuple[str, bool]:
    a, b = _scaled(value), _scaled(threshold)
    result = "ABOVE" if a > b else "BELOW" if a < b else "EQUAL"
    return result, result == {">": "ABOVE", "<": "BELOW", "==": "EQUAL"}[operator]


def _commit(attestation_id: int, creator: str, url: str, path: str,
            operator: str, threshold: str, context: str) -> str:
    fields = ("api-threshold-attestor:v1", str(attestation_id), creator.lower(),
              url, path, operator, threshold, context)
    encoded = [s.encode("utf-8") for s in fields]
    return sha256(b"".join(len(s).to_bytes(4, "big") + s for s in encoded)).hexdigest()


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _constant(value):
    raise ValueError("Nonfinite JSON number")


def _observe(url: str, path: str, threshold: str, operator: str) -> dict:
    try:
        response = gl.nondet.web.get(url)
        content_type = next((v.decode("ascii").lower().split(";", 1)[0].strip()
                             for k, v in response.headers.items() if k.lower() == "content-type"), "")
        if not 200 <= response.status < 300 or not (content_type == "application/json"
                or (content_type.startswith("application/") and content_type.endswith("+json"))):
            return {"availability": "UNAVAILABLE"}
        body = response.body or b""
        if not body or len(body) > MAX_BODY:
            return {"availability": "UNAVAILABLE"}
        value = json.loads(body.decode("utf-8"), parse_int=_Number, parse_float=_Number,
                           parse_constant=_constant, object_pairs_hook=_pairs)
        for key in path.split("."):
            if not isinstance(value, dict):
                raise ValueError("Dictionary path required")
            value = value[key]
        if not isinstance(value, _Number):
            raise ValueError("JSON numeric token required")
        observed = _decimal(value)
        result, condition = _relationship(observed, threshold, operator)
        return {"availability": "AVAILABLE", "observed_value": observed, "result": result,
                "condition_met": condition, "response_fingerprint": sha256(body).hexdigest()}
    except Exception:
        return {"availability": "UNAVAILABLE"}


def _valid(value, threshold: str, operator: str) -> bool:
    if value == {"availability": "UNAVAILABLE"}:
        return True
    try:
        if not isinstance(value, dict) or set(value) != {
                "availability", "observed_value", "result", "condition_met", "response_fingerprint"}:
            return False
        observed = value["observed_value"]
        result, condition = _relationship(_decimal(observed), threshold, operator)
        return (value["availability"] == "AVAILABLE" and observed == _decimal(observed)
                and value["result"] == result and type(value["condition_met"]) is bool
                and value["condition_met"] == condition
                and re.fullmatch(r"[0-9a-f]{64}", value["response_fingerprint"]) is not None)
    except Exception:
        return False


class APIThresholdAttestor(gl.contract.Contract):
    attestations: TreeMap[u256, Attestation]
    count: u256

    def __init__(self):
        self.count = u256(0)

    def _get(self, attestation_id: u256) -> Attestation:
        if attestation_id not in self.attestations:
            raise gl.vm.UserError("Attestation not found")
        return self.attestations[attestation_id]

    @gl.public.write
    def create_attestation(self, api_url: str, json_path: str, operator: str,
                           threshold: str, context: str) -> u256:
        url = _url(api_url)
        if (len(json_path) > 200 or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", json_path) is None
                or operator not in (">", "<", "==") or len(context) > 500
                or any(ord(c) < 32 and c not in "\n\r\t" for c in context)):
            raise gl.vm.UserError("Invalid path/operator/context")
        try:
            normalized = _decimal(threshold)
        except Exception:
            raise gl.vm.UserError("Invalid threshold")
        creator = gl.message.sender_address
        attestation_id = self.count + u256(1)
        commitment = _commit(int(attestation_id), creator.as_hex, url, json_path, operator, normalized, context)
        self.attestations[attestation_id] = Attestation(attestation_id, creator, url, json_path,
            operator, normalized, context, commitment, "PENDING", "", "", "", "", False)
        self.count = attestation_id
        return attestation_id

    @gl.public.write
    def resolve_attestation(self, attestation_id: u256) -> str:
        row = self._get(attestation_id)
        if row.status != "PENDING":
            raise gl.vm.UserError("Already attested")
        memory = gl.storage.copy_to_memory(row)
        url, path, threshold, operator = memory.api_url, memory.json_path, memory.threshold, memory.operator

        def leader_fn() -> dict:
            return _observe(url, path, threshold, operator)

        def validator_fn(leader_result) -> bool:
            try:
                if not isinstance(leader_result, gl.vm.Return):
                    return False
                material = leader_result.calldata
                return _valid(material, threshold, operator) and material == leader_fn()
            except Exception:
                return False

        accepted = gl.vm.run_nondet(leader_fn, validator_fn)
        if not _valid(accepted, threshold, operator):
            raise gl.vm.UserError("Invalid consensus result")
        if accepted["availability"] == "UNAVAILABLE":
            return "UNAVAILABLE"
        row.observed_value = accepted["observed_value"]
        row.response_fingerprint = accepted["response_fingerprint"]
        row.result = accepted["result"]
        row.condition_met = accepted["condition_met"]
        row.availability = "AVAILABLE"
        row.status = "ATTESTED"
        return row.result

    @gl.public.view
    def get_attestation(self, attestation_id: u256) -> dict:
        row = self._get(attestation_id)
        return {"attestation_id": row.attestation_id, "creator": row.creator.as_hex,
                "api_url": row.api_url, "json_path": row.json_path, "operator": row.operator,
                "threshold": row.threshold, "context": row.context, "request_commitment": row.request_commitment,
                "status": row.status, "availability": row.availability, "observed_value": row.observed_value,
                "response_fingerprint": row.response_fingerprint, "result": row.result,
                "condition_met": row.condition_met}

    @gl.public.view
    def get_attestation_count(self) -> u256:
        return self.count

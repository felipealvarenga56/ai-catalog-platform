"""Parser for the dataAI_Contract text format.

Converts dataAI_Contract text files into ContractCreate Pydantic objects.
"""

import re
from api.models import ContractCreate, ContractInitiative, ContractStatus


def _read_multiline(lines: list[str], start_idx: int, base_indent: int) -> tuple[str, int]:
    """Read a multi-line value (after a `|` marker) from consecutive lines.

    Collects lines until we hit a line that is a key-value pair at or below
    the base_indent level, or reach end of input.

    Returns the joined text and the index of the next line to process.
    """
    collected: list[str] = []
    idx = start_idx

    while idx < len(lines):
        line = lines[idx]

        # Empty line: could be part of multi-line content or a section break.
        # Peek ahead to decide.
        if line.strip() == "":
            # Check if the next non-empty line is a key at base_indent or less
            peek = idx + 1
            while peek < len(lines) and lines[peek].strip() == "":
                peek += 1
            if peek >= len(lines):
                # End of file — stop collecting
                break
            next_line = lines[peek]
            next_stripped = next_line.lstrip()
            next_indent = len(next_line) - len(next_stripped)
            # If next non-empty line is a key at base_indent or less, stop
            if next_indent <= base_indent and ":" in next_stripped:
                break
            # Otherwise, include the blank line as part of the content
            collected.append("")
            idx += 1
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # If this line is at or below base_indent and looks like a key, stop
        if indent <= base_indent and ":" in stripped:
            break

        collected.append(line.rstrip())
        idx += 1

    # Strip trailing empty lines and join
    while collected and collected[-1].strip() == "":
        collected.pop()

    return "\n".join(collected).rstrip(), idx


def _parse_id_line(line: str) -> str:
    """Extract the business_map_id from an id: line like 'id: 556706 (businessMap)'."""
    match = re.match(r"id:\s*(\d+)", line.strip())
    if not match:
        raise ValueError(f"Invalid id line: '{line.strip()}'. Expected format: 'id: <number> (businessMap)'")
    return match.group(1)


def parse_contract(text: str) -> ContractCreate:
    """Parse a dataAI_Contract text block into a ContractCreate object.

    Raises ValueError with descriptive message on invalid input.
    """
    lines = text.split("\n")

    # Find first non-empty line and verify header
    idx = 0
    while idx < len(lines) and lines[idx].strip() == "":
        idx += 1

    if idx >= len(lines) or lines[idx].strip() != "dataAI_Contract":
        raise ValueError("Missing dataAI_Contract header")

    idx += 1

    # State tracking
    business_map_id: str | None = None
    info_fields: dict[str, str] = {}
    contact_fields: dict[str, str] = {}
    terms_fields: dict[str, str] = {}
    current_section: str | None = None  # "info" or "terms"

    while idx < len(lines):
        line = lines[idx]

        # Skip empty lines at top level
        if line.strip() == "":
            idx += 1
            continue

        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Top-level keys (indent 0)
        if indent == 0:
            if stripped.startswith("id:"):
                business_map_id = _parse_id_line(stripped)
                current_section = None
                idx += 1
                continue
            elif stripped.strip() == "info:":
                current_section = "info"
                idx += 1
                continue
            elif stripped.strip() == "terms:":
                current_section = "terms"
                idx += 1
                continue
            else:
                # Unknown top-level key, skip
                idx += 1
                continue

        # Section-level keys (indent 2 for info/terms)
        if current_section == "info" and indent == 2:
            if stripped.startswith("contact:"):
                # Enter contact sub-block
                idx += 1
                while idx < len(lines):
                    cline = lines[idx]
                    if cline.strip() == "":
                        idx += 1
                        continue
                    c_stripped = cline.lstrip()
                    c_indent = len(cline) - len(c_stripped)
                    if c_indent <= 2:
                        break  # Back to info level or above
                    if ":" in c_stripped:
                        key, _, val = c_stripped.partition(":")
                        contact_fields[key.strip()] = val.strip()
                    idx += 1
                continue

            if ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip()

                if val == "|":
                    # Multi-line value
                    idx += 1
                    val, idx = _read_multiline(lines, idx, 2)
                    info_fields[key] = val
                    continue
                else:
                    info_fields[key] = val
                    idx += 1
                    continue

        elif current_section == "terms" and indent == 2:
            if ":" in stripped:
                key, _, val = stripped.partition(":")
                key = key.strip()
                val = val.strip()

                if val == "|":
                    # Multi-line value
                    idx += 1
                    val, idx = _read_multiline(lines, idx, 2)
                    terms_fields[key] = val
                    continue
                else:
                    terms_fields[key] = val
                    idx += 1
                    continue

        # Lines that don't match any pattern — skip
        idx += 1

    # Validate required fields
    if business_map_id is None:
        raise ValueError("Missing required field: id (business_map_id)")

    missing = []
    for field in ("title", "area", "initiative", "description"):
        if field not in info_fields or not info_fields[field]:
            missing.append(field)
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Build the ContractCreate object
    return ContractCreate(
        business_map_id=business_map_id,
        title=info_fields["title"],
        area=info_fields["area"],
        initiative=ContractInitiative(info_fields["initiative"]),
        version=info_fields.get("version", "1.0.0"),
        description=info_fields["description"],
        owner=info_fields.get("owner", ""),
        status=ContractStatus(info_fields["status"]) if "status" in info_fields else ContractStatus.ACTIVE,
        contact_name=contact_fields.get("name"),
        contact_email=contact_fields.get("email"),
        sec_approval=info_fields.get("sec_approval"),
        docs_link=info_fields.get("docs_link"),
        cost=info_fields.get("cost (cloud)"),
        projected_return=info_fields.get("projected_return"),
        usage=terms_fields.get("usage"),
        limitations=terms_fields.get("limitations"),
    )

def _serialize_field(key: str, value: str, indent: str = "  ") -> str:
    """Serialize a single field, using | marker for multi-line values.

    Multi-line values get the | marker and each content line is indented
    with indent + 2 extra spaces (so 4 spaces total for info/terms fields).
    All leading whitespace is stripped from each line before re-indenting,
    ensuring uniform indentation in the output. This means that after one
    serialize -> parse cycle the content is normalized, and subsequent
    cycles are stable (idempotent).
    """
    if "\n" in value:
        content_indent = indent + "  "
        result = f"{indent}{key}: |\n"
        for line in value.split("\n"):
            stripped = line.strip()
            if stripped == "":
                result += "\n"
            else:
                result += f"{content_indent}{stripped}\n"
        return result
    return f"{indent}{key}: {value}\n"


def serialize_contract(contract: ContractCreate) -> str:
    """Serialize a ContractCreate object back to dataAI_Contract text format."""
    out = "dataAI_Contract\n"
    out += f"id: {contract.business_map_id} (businessMap)\n"
    out += "info:\n"

    out += f"  title: {contract.title}\n"
    out += f"  area: {contract.area}\n"
    out += f"  initiative: {contract.initiative.value}\n"
    out += f"  version: {contract.version}\n"
    out += _serialize_field("description", contract.description)
    out += f"  owner: {contract.owner}\n"
    out += f"  status: {contract.status.value}\n"

    if contract.contact_name is not None or contract.contact_email is not None:
        out += "  contact:\n"
        if contract.contact_name is not None:
            out += f"    name: {contract.contact_name}\n"
        if contract.contact_email is not None:
            out += f"    email: {contract.contact_email}\n"

    if contract.sec_approval is not None:
        out += f"  sec_approval: {contract.sec_approval}\n"
    if contract.docs_link is not None:
        out += f"  docs_link: {contract.docs_link}\n"
    if contract.cost is not None:
        out += f"  cost (cloud): {contract.cost}\n"
    if contract.projected_return is not None:
        out += f"  projected_return: {contract.projected_return}\n"

    # Terms section — only include if there's at least one terms field
    has_terms = contract.usage is not None or contract.limitations is not None
    if has_terms:
        out += "\nterms:\n"
        if contract.usage is not None:
            out += _serialize_field("usage", contract.usage)
        if contract.limitations is not None:
            out += _serialize_field("limitations", contract.limitations)

    return out


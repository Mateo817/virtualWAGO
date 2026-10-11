#!/usr/bin/env python3
"""Bounded static audit of XML device-description declarations; never contacts devices."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import xml.etree.ElementTree as ET
from typing import Any

SCHEMA_NAMESPACE = "http://www.3s-software.com/schemas/DeviceDescription-1.0.xsd"
MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_ELEMENTS = 100_000
MAX_DEPTH = 128
LOCAL_TYPE_NAMESPACES = {"local", "localTypes"}


class AuditError(ValueError):
    """The supplied file is not safe or unambiguous to audit."""


class _BoundedTreeBuilder(ET.TreeBuilder):
    def __init__(self) -> None:
        super().__init__()
        self.elements = 0
        self.depth = 0

    def start(self, tag: str, attrs: dict[str, str]):
        self.elements += 1
        self.depth += 1
        if self.elements > MAX_ELEMENTS:
            raise AuditError("XML exceeds the bounded element count")
        if self.depth > MAX_DEPTH:
            raise AuditError("XML exceeds the bounded nesting depth")
        return super().start(tag, attrs)

    def end(self, tag: str):
        self.depth -= 1
        return super().end(tag)

    def doctype(self, name: str, pubid: str | None, system: str | None) -> None:
        raise AuditError("DTD declarations are not accepted")


def _read_stable_regular_file(path_value: str) -> bytes:
    path = Path(path_value)
    try:
        initial = path.lstat()
    except OSError as exc:
        raise AuditError("input is unavailable") from exc
    if not stat.S_ISREG(initial.st_mode):
        raise AuditError("only explicit regular non-symlink files are accepted")
    if initial.st_size > MAX_INPUT_BYTES:
        raise AuditError("XML exceeds the 8 MiB input bound")
    try:
        metadata_fd = os.open(path, os.O_PATH | os.O_NOFOLLOW)
    except OSError as exc:
        raise AuditError("cannot pin a regular non-symlink input") from exc
    try:
        before = os.fstat(metadata_fd)
        if not stat.S_ISREG(before.st_mode):
            raise AuditError("only explicit regular non-symlink files are accepted")
        if (initial.st_dev, initial.st_ino) != (before.st_dev, before.st_ino):
            raise AuditError("source path changed while it was being pinned")
        if before.st_size > MAX_INPUT_BYTES:
            raise AuditError("XML exceeds the 8 MiB input bound")
        try:
            data_fd = os.open(f"/proc/self/fd/{metadata_fd}", os.O_RDONLY | os.O_NONBLOCK)
        except OSError as exc:
            raise AuditError("pinned input could not be safely reopened") from exc
        try:
            opened = os.fstat(data_fd)
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino) or not stat.S_ISREG(opened.st_mode):
                raise AuditError("input changed during safe open")
            chunks: list[bytes] = []
            size = 0
            while True:
                chunk = os.read(data_fd, min(64 * 1024, MAX_INPUT_BYTES + 1 - size))
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
                if size > MAX_INPUT_BYTES:
                    raise AuditError("XML exceeds the 8 MiB input bound")
            after = os.fstat(data_fd)
            fields = ("st_size", "st_mtime_ns", "st_ctime_ns")
            if any(getattr(before, field) != getattr(after, field) for field in fields):
                raise AuditError("source file changed while it was being read")
            if size != before.st_size:
                raise AuditError("source file length changed while it was being read")
            return b"".join(chunks)
        finally:
            os.close(data_fd)
    finally:
        os.close(metadata_fd)


def _tag(local: str) -> str:
    return f"{{{SCHEMA_NAMESPACE}}}{local}"


def _children(element: ET.Element, local: str) -> list[ET.Element]:
    return [child for child in element if child.tag == _tag(local)]


def _single_child(element: ET.Element, local: str) -> ET.Element | None:
    found = _children(element, local)
    if len(found) > 1:
        raise AuditError(f"ambiguous duplicate {local} element")
    return found[0] if found else None


def _field(element: ET.Element, name: str) -> str | None:
    """Read one exact-schema child or unqualified attribute, rejecting conflicts."""
    attr = element.attrib.get(name)
    child = _single_child(element, name)
    text = "" if child is None or child.text is None else child.text.strip()
    if attr is not None and text and attr.strip() != text:
        raise AuditError(f"ambiguous {name} declaration")
    if attr is not None and text == "":
        return attr.strip()
    if child is not None:
        return text
    return None if attr is None else attr.strip()


def _element_text(element: ET.Element | None) -> str | None:
    if element is None:
        return None
    return "" if element.text is None else element.text.strip()


def _attributes_from(parameter: ET.Element) -> dict[str, str | None]:
    result: dict[str, str | None] = {}
    attributes_node = _single_child(parameter, "Attributes")
    for name in ("channel", "onlineaccess", "offlineaccess"):
        value = parameter.attrib.get(name)
        nested = None if attributes_node is None else attributes_node.attrib.get(name)
        if value is not None and nested is not None and value != nested:
            raise AuditError(f"ambiguous Parameter {name} declaration")
        result[name] = nested if nested is not None else value
    return result


def _defaults(element: ET.Element) -> str | None:
    default = _single_child(element, "Default")
    return _element_text(default)


def _parse_local_types(root: ET.Element) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for types_node in root.iter(_tag("Types")):
        namespace = types_node.attrib.get("namespace")
        if namespace not in LOCAL_TYPE_NAMESPACES:
            continue
        for declaration in types_node:
            if declaration.tag == _tag("Type"):
                name = declaration.attrib.get("name")
                if not name:
                    raise AuditError("local Type declaration is missing its name")
                bitfield = _single_child(declaration, "BitfieldType")
                if bitfield is None:
                    # A declared local type may exist without a supported summary;
                    # do not infer a layout from its name or consumers.
                    summaries.append({"name": name, "namespace": namespace,
                                      "kind": "unresolved_or_unsupported", "layout_claim": False})
                    continue
            elif declaration.tag == _tag("BitfieldType"):
                # DeviceDescription 1.0 permits local bitfields directly under
                # Types; do not require an extra Type wrapper.
                name = declaration.attrib.get("name")
                bitfield = declaration
                if not name:
                    raise AuditError("local BitfieldType declaration is missing its name")
            else:
                continue
            base_type = bitfield.attrib.get("basetype")
            alternate_base_type = bitfield.attrib.get("baseType")
            if base_type is not None and alternate_base_type is not None and base_type != alternate_base_type:
                raise AuditError("ambiguous bitfield base type")
            if base_type is None:
                base_type = alternate_base_type
            components: list[dict[str, str | None]] = []
            seen_identifiers: set[str] = set()
            for component in _children(bitfield, "Component"):
                identifier = _field(component, "identifier")
                component_type = _field(component, "type")
                if identifier is None or component_type is None:
                    raise AuditError("Bitfield Component is missing identifier or type")
                if identifier in seen_identifiers:
                    raise AuditError("duplicate Bitfield Component identifier")
                seen_identifiers.add(identifier)
                components.append({"identifier": identifier, "type": component_type,
                                   "default": _defaults(component)})
            summaries.append({
                "name": name,
                "namespace": namespace,
                "kind": "bitfield",
                "base_type": base_type,
                "component_count": len(components),
                "std_bool_component_count": sum(c["type"] == "std:BOOL" for c in components),
                "components_with_default_count": sum(c["default"] is not None for c in components),
                "components": components,
                "layout_claim": False,
            })
    names = [(item["namespace"], item["name"]) for item in summaries]
    if len(names) != len(set(names)):
        raise AuditError("duplicate local type declaration name")
    return summaries


def _type_resolution(type_name: str | None, declared_types: set[tuple[str, str]]) -> str:
    if not type_name:
        return "UNRESOLVED"
    if ":" not in type_name:
        return "UNRESOLVED"
    namespace, name = type_name.split(":", 1)
    if namespace not in LOCAL_TYPE_NAMESPACES:
        return "NONLOCAL_OR_BUILTIN"
    if (namespace, name) in declared_types:
        return "RESOLVED_LOCAL_DECLARATION"
    return "UNRESOLVED"


def audit_bytes(data: bytes, *, display_name: str | None = None) -> dict[str, Any]:
    if len(data) > MAX_INPUT_BYTES:
        raise AuditError("XML exceeds the 8 MiB input bound")
    builder = _BoundedTreeBuilder()
    parser = ET.XMLParser(target=builder)
    try:
        parser.feed(data)
        root = parser.close()
    except AuditError:
        raise
    except (ET.ParseError, ValueError) as exc:
        raise AuditError("malformed or unsupported XML") from exc
    if root.tag != _tag("DeviceDescription"):
        raise AuditError("root must be a DeviceDescription 1.0 schema element")
    devices = _children(root, "Device")
    if len(devices) != 1:
        raise AuditError("expected exactly one schema-qualified Device")
    device = devices[0]
    identification = _single_child(device, "DeviceIdentification")
    info = _single_child(device, "DeviceInfo")
    if identification is None:
        raise AuditError("DeviceIdentification is missing")
    if info is None:
        raise AuditError("DeviceInfo is missing")

    identification_fields = {name: _field(identification, name) for name in ("Type", "Id", "Version")}
    info_fields = {name: _field(info, name) for name in ("OrderNumber", "Name", "Vendor")}

    connectors: list[dict[str, str | None]] = []
    for connector in device.iter(_tag("Connector")):
        fields = ("moduleType", "role", "interface", "connectorId", "hostpath")
        connectors.append({name: connector.attrib.get(name) for name in fields})

    parameter_sets = list(device.iter(_tag("HostParameterSet")))
    if len(parameter_sets) > 1:
        raise AuditError("ambiguous duplicate HostParameterSet")
    parameters: list[dict[str, Any]] = []
    if parameter_sets:
        for parameter in parameter_sets[0].iter(_tag("Parameter")):
            parameter_id = _field(parameter, "ParameterId")
            parameter_type = _field(parameter, "type")
            parameters.append({
                "parameter_id": parameter_id,
                "type": parameter_type,
                "type_resolution": "PENDING",
                "attributes": _attributes_from(parameter),
                "default": _defaults(parameter),
            })
    ids = [row["parameter_id"] for row in parameters]
    if any(value is None for value in ids) or len(ids) != len(set(ids)):
        raise AuditError("HostParameterSet ParameterId is missing or duplicated")

    local_types = _parse_local_types(root)
    declared_types = {(row["namespace"], row["name"]) for row in local_types}
    for parameter in parameters:
        parameter["type_resolution"] = _type_resolution(parameter["type"], declared_types)

    return {
        "status": "PASS",
        "display_name": display_name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "schema_namespace": SCHEMA_NAMESPACE,
        "device_identification": identification_fields,
        "device_info": info_fields,
        "connectors": connectors,
        "host_parameters": parameters,
        "local_type_summaries": local_types,
        "scope": "static XML declarations only; no offsets, bus mapping, C ABI, runtime, or hardware claim",
        "xsd_validation": "NOT_RUN",
        "network_access": "NOT_ATTEMPTED",
        "device_access": "NOT_ATTEMPTED",
    }


def inspect(path_value: str) -> dict[str, Any]:
    data = _read_stable_regular_file(path_value)
    return audit_bytes(data, display_name=Path(path_value).name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="explicit DeviceDescription XML files to audit")
    args = parser.parse_args(argv)
    rows: list[dict[str, Any]] = []
    failed = False
    for path in args.files:
        try:
            rows.append(inspect(path))
        except (OSError, AuditError) as exc:
            failed = True
            rows.append({"status": "FAIL", "display_name": Path(path).name, "reason": str(exc),
                         "network_access": "NOT_ATTEMPTED", "device_access": "NOT_ATTEMPTED"})
    print(json.dumps(rows, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

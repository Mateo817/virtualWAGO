"""Bounded standalone signal models for two WAGO module candidates.

These classes model inputs and physical output reactions only. They do not
implement PLC decisions, module identification, status generation, register
communication, or original-runtime behavior. Their packing/timing policies
are research-model contracts and are not claims about native ADI frames.
"""
from __future__ import annotations

from collections.abc import Sequence

from .vio import (ContractError, Unsupported, decode_ao550_standard_word,
                  decode_pwm677_frq, encode_ai466_standard)

_NANOSECONDS_PER_SECOND = 1_000_000_000
_MAX_TIME_NS = 2**63 - 1


def _four_frequencies(values: Sequence[int], name: str) -> tuple[int, int, int, int]:
    if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
        raise ContractError(f"{name}: expected a sequence of exactly four integer frequencies")
    if len(values) != 4:
        raise ContractError(f"{name}: expected exactly four frequencies")
    result: list[int] = []
    for value in values:
        if type(value) is not int or not 0 <= value <= 20_000:
            raise ContractError(f"{name}: frequencies must be integers in [0, 20000] Hz")
        result.append(value)
    return tuple(result)  # type: ignore[return-value]


class Analog466:
    """Two-channel 750-466 normal-range signal source.

    ``input_bytes`` uses this project's explicit RESEARCH layout:
    ``status0, word0 little-endian, status1, word1 little-endian``. Status
    bytes are fixed at zero; this is not asserted to be native ADI packing.
    The codec's documented normal 4-20 mA conversion and its floor
    quantization assumption are reused. Under-range diagnostics are rejected.
    """

    def __init__(self) -> None:
        self._currents_uA = (4000, 4000)

    def set_currents_uA(self, currents_uA: Sequence[int]) -> None:
        if (isinstance(currents_uA, (str, bytes, bytearray)) or
                not isinstance(currents_uA, Sequence) or len(currents_uA) != 2):
            raise ContractError("currents_uA: expected exactly two integer currents")
        checked: list[int] = []
        for value in currents_uA:
            if type(value) is not int or not 4000 <= value <= 20_000:
                raise ContractError("currents_uA: expected integers in [4000, 20000] uA")
            # Keep codec validation/encoding contract authoritative for the range.
            encode_ai466_standard(value)
            checked.append(value)
        self._currents_uA = (checked[0], checked[1])

    def input_bytes(self) -> bytes:
        """Compatibility alias for the explicitly research-only six-byte layout."""
        return self.research_input_bytes()

    def descriptor_input_words(self) -> tuple[int, int]:
        """The two descriptor-shaped WORD values, without invented status bytes."""
        words = tuple(encode_ai466_standard(value) for value in self._currents_uA)
        return words[0], words[1]

    def descriptor_word_payload(self) -> bytes:
        """Four-byte little-endian model serialization of the two WORD fields.

        This follows the manual's word byte order and the local descriptor's
        two-WORD width. It is not an observed native ADI or hardware payload.
        """
        return b"".join(word.to_bytes(2, "little") for word in self.descriptor_input_words())

    def research_input_bytes(self) -> bytes:
        """Historical research-only status0/word0LE/status1/word1LE layout."""
        words = self.descriptor_input_words()
        return bytes((0,)) + words[0].to_bytes(2, "little") + bytes((0,)) + words[1].to_bytes(2, "little")


class AnalogOutput550:
    """Two-channel standard 750-550 voltage output reaction.

    The input process model accepts exactly two little-endian standard output
    WORDs (four bytes). Voltage scaling follows the WAGO normal-range table;
    rounded millivolt interpolation and the independent closed-by-default
    permit are own model rules. Permit/fault loss clears the output arm while
    retaining requested words for inspection. Reopening a gate needs a fresh
    complete output frame. This is a standalone backend model, not original
    runtime, ADI, register communication, or an electrical-load simulation.
    """

    def __init__(self) -> None:
        self._requested_words = (0, 0)
        self._requested_mV = (0, 0)
        self._permit = False
        self._fault = False
        self._armed = False

    @staticmethod
    def _words(values: Sequence[int]) -> tuple[int, int]:
        if (isinstance(values, (str, bytes, bytearray)) or
                not isinstance(values, Sequence) or len(values) != 2):
            raise ContractError("output words: expected exactly two unsigned 16-bit words")
        checked: list[int] = []
        for word in values:
            if type(word) is not int or not 0 <= word <= 0xFFFF:
                raise ContractError("output words: expected exactly two unsigned 16-bit words")
            if word > 0x7FFF:
                raise Unsupported("750-550 standard normal output words stop at 0x7fff")
            checked.append(word)
        return checked[0], checked[1]

    def set_output_words(self, words: Sequence[int]) -> None:
        checked = self._words(words)
        millivolts = tuple(decode_ao550_standard_word(word) for word in checked)
        self._requested_words = checked
        self._requested_mV = (millivolts[0], millivolts[1])
        self._armed = self._permit and not self._fault

    def set_output_payload(self, payload: bytes) -> None:
        if type(payload) is not bytes or len(payload) != 4:
            raise ContractError("750-550 model payload must be exactly four bytes")
        words = (int.from_bytes(payload[0:2], "little"),
                 int.from_bytes(payload[2:4], "little"))
        self.set_output_words(words)

    def set_channel_word(self, channel: int, word: int) -> None:
        if type(channel) is not int or channel not in (0, 1):
            raise ContractError("channel must be integer 0 or 1")
        replacement = list(self._requested_words)
        replacement[channel] = word
        self.set_output_words(replacement)

    def set_permit(self, permitted: bool) -> None:
        if type(permitted) is not bool:
            raise ContractError("permit must be bool")
        self._permit = permitted
        if not permitted:
            self._armed = False

    def set_fault(self, active: bool) -> None:
        if type(active) is not bool:
            raise ContractError("fault must be bool")
        self._fault = active
        if active:
            self._armed = False

    def observe(self) -> dict[str, object]:
        effective_words = self._requested_words if self._armed else (0, 0)
        effective_mV = self._requested_mV if self._armed else (0, 0)
        return {
            "requested_word": list(self._requested_words),
            "effective_word": list(effective_words),
            "requested_voltage_mV": list(self._requested_mV),
            "effective_voltage_mV": list(effective_mV),
            "requested_payload_hex": b"".join(w.to_bytes(2, "little") for w in self._requested_words).hex(),
            "effective_payload_hex": b"".join(w.to_bytes(2, "little") for w in effective_words).hex(),
            "permit": self._permit,
            "fault": self._fault,
            "armed": self._armed,
            "scope": "OWN standalone 750-550 normal-range signal model; NOT original runtime/ADI or electrical behavior",
        }


class Pwm677:
    """Bounded 750-677 PWM Frq output reaction with a deterministic own clock.

    Configuring frequencies requests both output pairs enabled. A complete
    decoded output frame replaces those frequencies and pair-enable requests;
    disabled raw frequency words are retained for observation. A permit and
    absence of fault are required before ``start`` latches running. Losing
    either gate stops the run and discards fractional pulse phase; restoring
    the gate never resumes automatically, so call ``start`` again.

    Counts are cumulative pulses. Integral accumulation uses exact integer
    frequency-nanosecond products, so splitting an advance does not change
    counts. Stop, gate loss, pair disable, and a channel retune discard only
    that channel's fractional phase. There is no edge phase, electrical,
    load, jitter, or real-time guarantee. Register communication and modes
    outside the decoder's PWM Frq subset remain unsupported.
    """

    def __init__(self) -> None:
        self._time_ns = 0
        self._running = False
        self._permit = False
        self._fault = False
        self._requested_hz = (0, 0, 0, 0)
        self._pair_enabled = (False, False)
        self._pulse_count = [0, 0, 0, 0]
        self._phase = [0, 0, 0, 0]

    def _retune(self, frequencies: tuple[int, int, int, int]) -> None:
        for channel, (old, new) in enumerate(zip(self._requested_hz, frequencies)):
            if old != new:
                self._phase[channel] = 0
        self._requested_hz = frequencies

    def configure(self, frequencies_hz: Sequence[int]) -> None:
        frequencies = _four_frequencies(frequencies_hz, "frequencies_hz")
        # Validate first, then atomically replace channel requests and open the
        # requested pair gates. The independent permit/fault gates still apply.
        self._retune(frequencies)
        self._pair_enabled = (True, True)

    def start(self) -> None:
        self._running = self._permit and not self._fault
        if not self._running:
            self._discard_phase()

    def stop(self) -> None:
        self._running = False
        self._discard_phase()

    def _discard_phase(self, channels: tuple[int, ...] = (0, 1, 2, 3)) -> None:
        for channel in channels:
            self._phase[channel] = 0

    def apply_output_frame(self, data: bytes) -> None:
        # Decode before touching state: malformed frames are fully atomic.
        decode_pwm677_frq(data)
        raw_frequencies = tuple(int.from_bytes(data[i + 1:i + 3], "little")
                                for i in (0, 3, 6, 9))
        pair_enabled = (bool(data[0] & 1), bool(data[6] & 1))
        self._retune(raw_frequencies)
        for pair, enabled in enumerate(pair_enabled):
            if self._pair_enabled[pair] and not enabled:
                self._discard_phase((pair * 2, pair * 2 + 1))
        self._pair_enabled = pair_enabled

    def set_permit(self, permitted: bool) -> None:
        if type(permitted) is not bool:
            raise ContractError("permit must be bool")
        self._permit = permitted
        if not permitted:
            self._running = False
            self._discard_phase()

    def set_fault(self, active: bool) -> None:
        if type(active) is not bool:
            raise ContractError("fault must be bool")
        self._fault = active
        if active:
            self._running = False
            self._discard_phase()

    def advance(self, dt_ns: int) -> None:
        if type(dt_ns) is not int or dt_ns < 0:
            raise ContractError("dt_ns: expected a nonnegative integer")
        if self._time_ns + dt_ns > _MAX_TIME_NS:
            raise ContractError("logical clock overflow")

        if self._running and self._permit and not self._fault:
            for channel, frequency in enumerate(self._effective_frequencies()):
                if frequency:
                    total = self._phase[channel] + frequency * dt_ns
                    pulses, self._phase[channel] = divmod(total, _NANOSECONDS_PER_SECOND)
                    self._pulse_count[channel] += pulses
        self._time_ns += dt_ns

    def _effective_pair_enabled(self) -> tuple[bool, bool]:
        open_gate = self._running and self._permit and not self._fault
        return tuple(enabled and open_gate for enabled in self._pair_enabled)  # type: ignore[return-value]

    def _effective_frequencies(self) -> tuple[int, int, int, int]:
        pairs = self._effective_pair_enabled()
        return tuple(freq if pairs[channel // 2] else 0
                     for channel, freq in enumerate(self._requested_hz))  # type: ignore[return-value]

    def observe(self) -> dict[str, object]:
        effective = self._effective_frequencies()
        return {
            "mode": "PWM Frq",
            "running": self._running,
            # frequency_hz is the effective output, matching pulse_count.
            "frequency_hz": list(effective),
            "requested_frequency_hz": list(self._requested_hz),
            "effective_frequency_hz": list(effective),
            "requested_pair_enabled": list(self._pair_enabled),
            "effective_pair_enabled": list(self._effective_pair_enabled()),
            "permit": self._permit,
            "fault": self._fault,
            "pulse_count": list(self._pulse_count),
            "time_ns": self._time_ns,
            "scope": "OWN deterministic standalone PWM Frq signal model; NOT native runtime or electrical timing",
        }

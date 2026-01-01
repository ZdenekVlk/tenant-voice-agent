from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Iterable


def _escape_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


def _format_labels(labels: dict[str, str]) -> str:
    pairs = [f'{key}="{_escape_label(value)}"' for key, value in labels.items()]
    return "{" + ",".join(pairs) + "}"


@dataclass
class MetricsStore:
    _lock: Lock = field(default_factory=Lock)
    _request_counts: dict[tuple[str, str, str], int] = field(
        default_factory=lambda: defaultdict(int)
    )
    _request_duration_sum: dict[tuple[str, str, str], float] = field(
        default_factory=lambda: defaultdict(float)
    )
    _request_duration_count: dict[tuple[str, str, str], int] = field(
        default_factory=lambda: defaultdict(int)
    )

    def record_request(self, method: str, path: str, status_code: int, duration_ms: float) -> None:
        key = (method, path, str(status_code))
        with self._lock:
            self._request_counts[key] += 1
            self._request_duration_sum[key] += duration_ms
            self._request_duration_count[key] += 1

    def render_prometheus(self) -> str:
        with self._lock:
            counts = dict(self._request_counts)
            durations_sum = dict(self._request_duration_sum)
            durations_count = dict(self._request_duration_count)

        lines: list[str] = []
        lines.extend(
            _metric_header(
                "http_requests_total",
                "Total number of HTTP requests.",
                "counter",
            )
        )
        for (method, path, status_code), value in counts.items():
            labels = _format_labels(
                {"method": method, "path": path, "status_code": status_code}
            )
            lines.append(f"http_requests_total{labels} {value}")

        lines.extend(
            _metric_header(
                "http_request_duration_ms_sum",
                "Sum of HTTP request durations in milliseconds.",
                "counter",
            )
        )
        for (method, path, status_code), value in durations_sum.items():
            labels = _format_labels(
                {"method": method, "path": path, "status_code": status_code}
            )
            lines.append(f"http_request_duration_ms_sum{labels} {value:.3f}")

        lines.extend(
            _metric_header(
                "http_request_duration_ms_count",
                "Count of HTTP request durations in milliseconds.",
                "counter",
            )
        )
        for (method, path, status_code), value in durations_count.items():
            labels = _format_labels(
                {"method": method, "path": path, "status_code": status_code}
            )
            lines.append(f"http_request_duration_ms_count{labels} {value}")

        lines.append("")
        return "\n".join(lines)


def _metric_header(name: str, description: str, metric_type: str) -> Iterable[str]:
    return [
        f"# HELP {name} {description}",
        f"# TYPE {name} {metric_type}",
    ]


metrics = MetricsStore()

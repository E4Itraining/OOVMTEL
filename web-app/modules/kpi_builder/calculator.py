"""
KPI Calculator - Calculate KPI values from formulas
"""

import logging
import re
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
import operator

from .models import (
    KPIDefinition,
    KPIResult,
    KPIFormula,
    KPIDataSource,
    KPIThreshold,
    AggregationType,
    DataSourceType,
)

logger = logging.getLogger(__name__)


class KPICalculator:
    """
    Calculate KPI values from definitions and data.

    Features:
    - Formula parsing and evaluation
    - Multiple aggregation types
    - Safe expression evaluation
    - Caching for performance
    - Threshold evaluation
    """

    def __init__(self):
        self._data_fetchers: Dict[str, Callable] = {}
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl_seconds = 60

        # Safe operators for expression evaluation
        self._operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': self._safe_divide,
            '^': operator.pow,
            '%': operator.mod,
            '>': operator.gt,
            '<': operator.lt,
            '>=': operator.ge,
            '<=': operator.le,
            '==': operator.eq,
            '!=': operator.ne,
        }

        self._functions = {
            'min': min,
            'max': max,
            'avg': lambda *args: sum(args) / len(args) if args else 0,
            'sum': sum,
            'abs': abs,
            'sqrt': math.sqrt,
            'log': math.log10,
            'ln': math.log,
            'round': round,
            'floor': math.floor,
            'ceil': math.ceil,
            'if': lambda cond, true_val, false_val: true_val if cond else false_val,
        }

        logger.info("KPI Calculator initialized")

    def register_data_fetcher(
        self,
        source_type: str,
        fetcher: Callable[[KPIDataSource], float]
    ) -> None:
        """Register a data fetcher for a source type."""
        self._data_fetchers[source_type] = fetcher
        logger.info(f"Registered data fetcher for: {source_type}")

    def calculate(
        self,
        kpi: KPIDefinition,
        metrics_data: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
        group_values: Optional[Dict[str, str]] = None
    ) -> KPIResult:
        """
        Calculate KPI value.

        Args:
            kpi: KPI definition
            metrics_data: Optional metrics data for calculation
            timestamp: Calculation timestamp
            group_values: Optional grouping values

        Returns:
            KPI calculation result
        """
        start_time = time.time()
        timestamp = timestamp or datetime.utcnow()

        try:
            # Fetch input values
            input_values = self._fetch_inputs(kpi.formula, metrics_data)

            # Evaluate formula
            value = self._evaluate_formula(kpi.formula.expression, input_values)

            # Apply bounds
            if kpi.formula.min_result is not None:
                value = max(value, kpi.formula.min_result)
            if kpi.formula.max_result is not None:
                value = min(value, kpi.formula.max_result)

            # Evaluate thresholds
            threshold_status, threshold_color = self._evaluate_thresholds(
                value, kpi.thresholds
            )

            # Calculate target deviation
            target_deviation = None
            if kpi.target_value is not None and kpi.target_value != 0:
                target_deviation = ((value - kpi.target_value) / kpi.target_value) * 100

            # Get previous value for trend
            previous_value = self._get_previous_value(kpi.kpi_id)
            trend = self._calculate_trend(value, previous_value)
            change_percent = None
            if previous_value is not None and previous_value != 0:
                change_percent = ((value - previous_value) / previous_value) * 100

            result = KPIResult(
                kpi_id=kpi.kpi_id,
                kpi_name=kpi.name,
                value=round(value, kpi.visualization.decimal_places),
                unit=kpi.unit,
                timestamp=timestamp,
                group_values=group_values or {},
                threshold_status=threshold_status,
                threshold_color=threshold_color,
                target_deviation=target_deviation,
                trend=trend,
                input_values=input_values,
                formula_used=kpi.formula.expression,
                calculation_time_ms=(time.time() - start_time) * 1000,
                previous_value=previous_value,
                change_percent=change_percent,
            )

            # Cache result
            self._cache_value(kpi.kpi_id, value)

            return result

        except Exception as e:
            logger.error(f"KPI calculation error for {kpi.kpi_id}: {e}")
            return KPIResult(
                kpi_id=kpi.kpi_id,
                kpi_name=kpi.name,
                value=0.0,
                threshold_status="error",
                threshold_color="#dc3545",
                calculation_time_ms=(time.time() - start_time) * 1000,
            )

    def _fetch_inputs(
        self,
        formula: KPIFormula,
        metrics_data: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Fetch input values for formula variables."""
        inputs = {}

        for var_name, source in formula.variables.items():
            value = self._fetch_single_input(source, metrics_data)
            inputs[var_name] = value

        return inputs

    def _fetch_single_input(
        self,
        source: KPIDataSource,
        metrics_data: Optional[Dict[str, Any]]
    ) -> float:
        """Fetch a single input value."""
        if source.source_type == DataSourceType.CONSTANT:
            return source.constant_value or 0.0

        if source.source_type == DataSourceType.METRIC:
            if metrics_data:
                return self._extract_metric(source, metrics_data)

            # Try registered fetcher
            if source.source_type.value in self._data_fetchers:
                fetcher = self._data_fetchers[source.source_type.value]
                return fetcher(source)

        return 0.0

    def _extract_metric(
        self,
        source: KPIDataSource,
        metrics_data: Dict[str, Any]
    ) -> float:
        """Extract metric value from metrics data."""
        metric_name = source.metric_name
        if not metric_name:
            return 0.0

        # Try business metrics
        business = metrics_data.get("business", {})
        if metric_name in business:
            return float(business[metric_name])

        # Try tech metrics
        tech = metrics_data.get("tech", {})
        if metric_name in tech:
            return float(tech[metric_name])

        # Try equipment
        for eq in business.get("equipment", []):
            if source.equipment_filter and source.equipment_filter not in eq.get("name", ""):
                continue

            # Map common metric names
            field_map = {
                "temperature": "temp",
                "temp": "temp",
                "vibration": "vibration",
                "power": "power",
            }
            field = field_map.get(metric_name, metric_name)

            if field in eq:
                return float(eq[field])

        return 0.0

    def _evaluate_formula(
        self,
        expression: str,
        variables: Dict[str, float]
    ) -> float:
        """
        Safely evaluate a formula expression.

        Uses a simple recursive descent parser for safety.
        """
        # Replace variables with values
        expr = expression
        for var_name, value in variables.items():
            expr = re.sub(rf'\b{var_name}\b', str(value), expr)

        # Evaluate expression
        return self._eval_expr(expr)

    def _eval_expr(self, expr: str) -> float:
        """Evaluate expression safely."""
        expr = expr.strip()

        # Handle functions
        func_match = re.match(r'(\w+)\s*\((.*)\)', expr)
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2)

            if func_name in self._functions:
                # Parse arguments
                args = self._parse_args(args_str)
                return self._functions[func_name](*args)

        # Handle parentheses
        while '(' in expr:
            expr = re.sub(r'\(([^()]+)\)', lambda m: str(self._eval_simple(m.group(1))), expr)

        return self._eval_simple(expr)

    def _eval_simple(self, expr: str) -> float:
        """Evaluate simple expression without parentheses."""
        expr = expr.strip()

        # Try to parse as number
        try:
            return float(expr)
        except ValueError:
            pass

        # Handle binary operators (order of operations)
        for ops in [['+', '-'], ['*', '/', '%'], ['^']]:
            for op in ops:
                # Find rightmost operator (for left-to-right evaluation)
                idx = expr.rfind(op)
                if idx > 0:
                    left = expr[:idx]
                    right = expr[idx + 1:]
                    left_val = self._eval_simple(left)
                    right_val = self._eval_simple(right)
                    return self._operators[op](left_val, right_val)

        return 0.0

    def _parse_args(self, args_str: str) -> List[float]:
        """Parse function arguments."""
        args = []
        depth = 0
        current = ""

        for char in args_str + ',':
            if char == '(':
                depth += 1
                current += char
            elif char == ')':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                if current.strip():
                    args.append(self._eval_expr(current.strip()))
                current = ""
            else:
                current += char

        return args

    def _safe_divide(self, a: float, b: float) -> float:
        """Safe division that handles zero."""
        if b == 0:
            return 0.0
        return a / b

    def _evaluate_thresholds(
        self,
        value: float,
        thresholds: List[KPIThreshold]
    ) -> tuple:
        """Evaluate value against thresholds."""
        status = "normal"
        color = "#808080"

        for threshold in sorted(thresholds, key=lambda t: t.value, reverse=True):
            comparison = threshold.comparison
            threshold_value = threshold.value

            matches = False
            if comparison == "gt" and value > threshold_value:
                matches = True
            elif comparison == "gte" and value >= threshold_value:
                matches = True
            elif comparison == "lt" and value < threshold_value:
                matches = True
            elif comparison == "lte" and value <= threshold_value:
                matches = True
            elif comparison == "eq" and value == threshold_value:
                matches = True

            if matches:
                status = threshold.name.lower()
                color = threshold.color
                break

        return status, color

    def _get_previous_value(self, kpi_id: str) -> Optional[float]:
        """Get previous cached value for trend calculation."""
        cache_entry = self._cache.get(kpi_id)
        if cache_entry:
            return cache_entry.get("value")
        return None

    def _cache_value(self, kpi_id: str, value: float) -> None:
        """Cache calculated value."""
        self._cache[kpi_id] = {
            "value": value,
            "timestamp": datetime.utcnow(),
        }

    def _calculate_trend(
        self,
        current: float,
        previous: Optional[float]
    ) -> str:
        """Calculate trend direction."""
        if previous is None:
            return "stable"

        diff = current - previous
        threshold = abs(previous * 0.01) if previous != 0 else 0.01

        if diff > threshold:
            return "up"
        elif diff < -threshold:
            return "down"
        return "stable"

    def aggregate_values(
        self,
        values: List[float],
        aggregation: AggregationType,
        percentile: float = 50.0
    ) -> float:
        """Aggregate a list of values."""
        if not values:
            return 0.0

        if aggregation == AggregationType.SUM:
            return sum(values)
        elif aggregation == AggregationType.AVG:
            return sum(values) / len(values)
        elif aggregation == AggregationType.MIN:
            return min(values)
        elif aggregation == AggregationType.MAX:
            return max(values)
        elif aggregation == AggregationType.COUNT:
            return float(len(values))
        elif aggregation == AggregationType.FIRST:
            return values[0]
        elif aggregation == AggregationType.LAST:
            return values[-1]
        elif aggregation == AggregationType.MEDIAN:
            sorted_vals = sorted(values)
            n = len(sorted_vals)
            mid = n // 2
            if n % 2 == 0:
                return (sorted_vals[mid - 1] + sorted_vals[mid]) / 2
            return sorted_vals[mid]
        elif aggregation == AggregationType.STDDEV:
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            return math.sqrt(variance)
        elif aggregation == AggregationType.PERCENTILE:
            sorted_vals = sorted(values)
            k = (len(sorted_vals) - 1) * percentile / 100
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_vals[int(k)]
            return sorted_vals[int(f)] * (c - k) + sorted_vals[int(c)] * (k - f)

        return sum(values) / len(values)

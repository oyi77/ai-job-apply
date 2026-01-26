"""
Data Processing Utilities for Analytics

Provides data processing, transformation, and statistical utilities for:
- Time series data processing
- Statistical calculations
- Data normalization and aggregation
- Trend analysis helpers
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


def normalize_data(values: List[float], method: str = "min_max") -> List[float]:
    """
    Normalize data using specified method.

    Args:
        values: List of values to normalize
        method: Normalization method ('min_max' or 'z_score')

    Returns:
        List of normalized values
    """
    if not values:
        return []

    if method == "min_max":
        min_val = min(values)
        max_val = max(values)

        if max_val == min_val:
            return [0.5] * len(values)

        return [(v - min_val) / (max_val - min_val) for v in values]

    elif method == "z_score":
        if len(values) < 2:
            return [0.0] * len(values)

        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)

        if std_dev == 0:
            return [0.0] * len(values)

        return [(v - mean) / std_dev for v in values]

    else:
        raise ValueError(f"Unknown normalization method: {method}")


def calculate_moving_average(values: List[float], window_size: int = 3) -> List[float]:
    """
    Calculate moving average of values.

    Args:
        values: List of values
        window_size: Size of moving window

    Returns:
        List of moving averages
    """
    if not values or window_size < 1:
        return []

    if window_size > len(values):
        window_size = len(values)

    result = []
    for i in range(len(values)):
        start_idx = max(0, i - window_size + 1)
        window = values[start_idx : i + 1]
        result.append(statistics.mean(window))

    return result


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.

    Args:
        old_value: Original value
        new_value: New value

    Returns:
        Percentage change
    """
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0

    return ((new_value - old_value) / abs(old_value)) * 100


def aggregate_by_time_period(
    data: List[Dict[str, Any]],
    date_field: str,
    value_field: str,
    period: str = "week",
    aggregation: str = "sum",
) -> List[Dict[str, Any]]:
    """
    Aggregate data by time period.

    Args:
        data: List of data dictionaries
        date_field: Name of date field
        value_field: Name of value field to aggregate
        period: Time period ('day', 'week', 'month')
        aggregation: Aggregation method ('sum', 'avg', 'count')

    Returns:
        List of aggregated data by period
    """
    if not data:
        return []

    period_data = defaultdict(list)

    for item in data:
        date_value = item.get(date_field)
        if not isinstance(date_value, datetime):
            continue

        # Determine period key
        if period == "day":
            period_key = date_value.strftime("%Y-%m-%d")
        elif period == "week":
            week_start = date_value - timedelta(days=date_value.weekday())
            period_key = week_start.strftime("%Y-%m-%d")
        elif period == "month":
            period_key = date_value.strftime("%Y-%m")
        else:
            raise ValueError(f"Unknown period: {period}")

        value = item.get(value_field, 0)
        period_data[period_key].append(value)

    # Aggregate values
    result = []
    for period_key, values in sorted(period_data.items()):
        if aggregation == "sum":
            agg_value = sum(values)
        elif aggregation == "avg":
            agg_value = statistics.mean(values) if values else 0
        elif aggregation == "count":
            agg_value = len(values)
        else:
            raise ValueError(f"Unknown aggregation: {aggregation}")

        result.append({"period": period_key, "value": agg_value, "count": len(values)})

    return result


def calculate_growth_rate(values: List[float], periods: int = 1) -> List[float]:
    """
    Calculate period-over-period growth rate.

    Args:
        values: List of values
        periods: Number of periods to look back

    Returns:
        List of growth rates
    """
    if len(values) < periods + 1:
        return []

    growth_rates = []
    for i in range(periods, len(values)):
        old_value = values[i - periods]
        new_value = values[i]

        if old_value == 0:
            growth_rate = 100.0 if new_value > 0 else 0.0
        else:
            growth_rate = ((new_value - old_value) / abs(old_value)) * 100

        growth_rates.append(growth_rate)

    return growth_rates


def detect_outliers(
    values: List[float], method: str = "iqr", threshold: float = 1.5
) -> List[int]:
    """
    Detect outliers in data.

    Args:
        values: List of values
        method: Detection method ('iqr' or 'z_score')
        threshold: Threshold for outlier detection

    Returns:
        List of indices of outliers
    """
    if len(values) < 4:
        return []

    outlier_indices = []

    if method == "iqr":
        # Interquartile range method
        sorted_values = sorted(values)
        n = len(sorted_values)

        q1_idx = n // 4
        q3_idx = 3 * n // 4

        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1

        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr

        for i, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                outlier_indices.append(i)

    elif method == "z_score":
        # Z-score method
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        if std_dev == 0:
            return []

        for i, value in enumerate(values):
            z_score = abs((value - mean) / std_dev)
            if z_score > threshold:
                outlier_indices.append(i)

    else:
        raise ValueError(f"Unknown outlier detection method: {method}")

    return outlier_indices


def calculate_correlation(x_values: List[float], y_values: List[float]) -> float:
    """
    Calculate Pearson correlation coefficient.

    Args:
        x_values: First set of values
        y_values: Second set of values

    Returns:
        Correlation coefficient (-1 to 1)
    """
    if len(x_values) != len(y_values) or len(x_values) < 2:
        return 0.0

    n = len(x_values)

    # Calculate means
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(y_values)

    # Calculate correlation
    numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(n))

    x_variance = sum((x - x_mean) ** 2 for x in x_values)
    y_variance = sum((y - y_mean) ** 2 for y in y_values)

    denominator = (x_variance * y_variance) ** 0.5

    if denominator == 0:
        return 0.0

    return numerator / denominator


def smooth_data(
    values: List[float], method: str = "moving_average", window_size: int = 3
) -> List[float]:
    """
    Smooth data using specified method.

    Args:
        values: List of values to smooth
        method: Smoothing method ('moving_average' or 'exponential')
        window_size: Window size for smoothing

    Returns:
        List of smoothed values
    """
    if not values:
        return []

    if method == "moving_average":
        return calculate_moving_average(values, window_size)

    elif method == "exponential":
        # Exponential smoothing
        alpha = 2 / (window_size + 1)
        smoothed = [values[0]]

        for i in range(1, len(values)):
            smoothed_value = alpha * values[i] + (1 - alpha) * smoothed[-1]
            smoothed.append(smoothed_value)

        return smoothed

    else:
        raise ValueError(f"Unknown smoothing method: {method}")


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate comprehensive statistics for a dataset.

    Args:
        values: List of values

    Returns:
        Dictionary with statistical measures
    """
    if not values:
        return {
            "count": 0,
            "mean": 0.0,
            "median": 0.0,
            "std_dev": 0.0,
            "min": 0.0,
            "max": 0.0,
            "range": 0.0,
        }

    return {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "std_dev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "range": max(values) - min(values),
        "q1": statistics.quantiles(values, n=4)[0] if len(values) >= 4 else min(values),
        "q3": statistics.quantiles(values, n=4)[2] if len(values) >= 4 else max(values),
    }


def group_by_category(
    data: List[Dict[str, Any]],
    category_field: str,
    value_field: str,
    aggregation: str = "sum",
) -> Dict[str, Any]:
    """
    Group data by category and aggregate values.

    Args:
        data: List of data dictionaries
        category_field: Field to group by
        value_field: Field to aggregate
        aggregation: Aggregation method ('sum', 'avg', 'count', 'min', 'max')

    Returns:
        Dictionary with aggregated values by category
    """
    if not data:
        return {}

    category_data = defaultdict(list)

    for item in data:
        category = item.get(category_field, "Unknown")
        value = item.get(value_field, 0)
        category_data[category].append(value)

    result = {}
    for category, values in category_data.items():
        if aggregation == "sum":
            agg_value = sum(values)
        elif aggregation == "avg":
            agg_value = statistics.mean(values) if values else 0
        elif aggregation == "count":
            agg_value = len(values)
        elif aggregation == "min":
            agg_value = min(values) if values else 0
        elif aggregation == "max":
            agg_value = max(values) if values else 0
        else:
            raise ValueError(f"Unknown aggregation: {aggregation}")

        result[category] = {"value": agg_value, "count": len(values)}

    return result


def calculate_trend_line(values: List[float]) -> Tuple[float, float]:
    """
    Calculate linear trend line (slope and intercept).

    Args:
        values: List of values

    Returns:
        Tuple of (slope, intercept)
    """
    if len(values) < 2:
        return 0.0, values[0] if values else 0.0

    n = len(values)
    x_values = list(range(n))

    # Calculate means
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(values)

    # Calculate slope
    numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x - x_mean) ** 2 for x in x_values)

    if denominator == 0:
        return 0.0, y_mean

    slope = numerator / denominator
    intercept = y_mean - slope * x_mean

    return slope, intercept


def filter_by_date_range(
    data: List[Dict[str, Any]],
    date_field: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """
    Filter data by date range.

    Args:
        data: List of data dictionaries
        date_field: Name of date field
        start_date: Start date (inclusive)
        end_date: End date (inclusive)

    Returns:
        Filtered list of data
    """
    if not data:
        return []

    filtered = []
    for item in data:
        date_value = item.get(date_field)

        if not isinstance(date_value, datetime):
            continue

        if start_date and date_value < start_date:
            continue

        if end_date and date_value > end_date:
            continue

        filtered.append(item)

    return filtered


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    Calculate percentile value.

    Args:
        values: List of values
        percentile: Percentile to calculate (0-100)

    Returns:
        Percentile value
    """
    if not values:
        return 0.0

    if percentile < 0 or percentile > 100:
        raise ValueError("Percentile must be between 0 and 100")

    sorted_values = sorted(values)
    n = len(sorted_values)

    if percentile == 0:
        return sorted_values[0]
    if percentile == 100:
        return sorted_values[-1]

    # Linear interpolation
    index = (percentile / 100) * (n - 1)
    lower_index = int(index)
    upper_index = min(lower_index + 1, n - 1)

    if lower_index == upper_index:
        return sorted_values[lower_index]

    fraction = index - lower_index
    return sorted_values[lower_index] + fraction * (
        sorted_values[upper_index] - sorted_values[lower_index]
    )

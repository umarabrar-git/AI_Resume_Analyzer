from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from threading import RLock
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ModelPricing:
    provider: str
    model: str

    input_per_million: Decimal
    output_per_million: Decimal

    cached_input_per_million: Optional[
        Decimal
    ] = None

    currency: str = "USD"


@dataclass
class CostRecord:
    provider: str
    model: str

    input_tokens: int
    output_tokens: int
    cached_input_tokens: int

    input_cost: Decimal
    output_cost: Decimal
    cached_input_cost: Decimal

    total_cost: Decimal

    currency: str = "USD"

    run_id: Optional[str] = None
    request_id: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "provider": self.provider,
            "model": self.model,

            "input_tokens":
                self.input_tokens,

            "output_tokens":
                self.output_tokens,

            "cached_input_tokens":
                self.cached_input_tokens,

            "input_cost":
                str(self.input_cost),

            "output_cost":
                str(self.output_cost),

            "cached_input_cost":
                str(
                    self.cached_input_cost
                ),

            "total_cost":
                str(self.total_cost),

            "currency":
                self.currency,

            "run_id":
                self.run_id,

            "request_id":
                self.request_id,

            "metadata":
                self.metadata,
        }


class CostTracker:
    """
    Calculates and records AI inference costs.

    Pricing is injected rather than hard-coded so model pricing
    can be changed without modifying application logic.
    """

    MILLION = Decimal(
        "1000000"
    )

    def __init__(self) -> None:

        self._pricing: Dict[
            tuple[str, str],
            ModelPricing
        ] = {}

        self._records: List[
            CostRecord
        ] = []

        self._lock = RLock()

    def register_pricing(
        self,
        pricing: ModelPricing,
    ) -> None:

        key = (
            pricing.provider.casefold(),
            pricing.model.casefold(),
        )

        with self._lock:
            self._pricing[key] = (
                pricing
            )

    def calculate(
        self,
        *,
        provider: str,
        model: str,

        input_tokens: int,
        output_tokens: int,

        cached_input_tokens: int = 0,

        run_id: Optional[str] = None,
        request_id: Optional[str] = None,

        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> CostRecord:

        pricing = self._get_pricing(
            provider,
            model,
        )

        input_tokens = max(
            int(input_tokens),
            0,
        )

        output_tokens = max(
            int(output_tokens),
            0,
        )

        cached_input_tokens = max(
            int(cached_input_tokens),
            0,
        )

        # Cached tokens are assumed to be included in total
        # input usage, so charge regular input rate only for
        # the non-cached portion.

        billable_regular_input = max(
            input_tokens
            - cached_input_tokens,
            0,
        )

        input_cost = (
            Decimal(
                billable_regular_input
            )
            / self.MILLION
            * pricing.input_per_million
        )

        output_cost = (
            Decimal(
                output_tokens
            )
            / self.MILLION
            * pricing.output_per_million
        )

        if (
            pricing.cached_input_per_million
            is not None
        ):

            cached_cost = (
                Decimal(
                    cached_input_tokens
                )
                / self.MILLION
                * pricing
                .cached_input_per_million
            )

        else:

            cached_cost = (
                Decimal(
                    cached_input_tokens
                )
                / self.MILLION
                * pricing.input_per_million
            )

        total = (
            input_cost
            + output_cost
            + cached_cost
        )

        record = CostRecord(
            provider=provider,
            model=model,

            input_tokens=input_tokens,
            output_tokens=output_tokens,

            cached_input_tokens=(
                cached_input_tokens
            ),

            input_cost=input_cost,
            output_cost=output_cost,

            cached_input_cost=(
                cached_cost
            ),

            total_cost=total,

            currency=pricing.currency,

            run_id=run_id,
            request_id=request_id,

            metadata=metadata or {},
        )

        with self._lock:
            self._records.append(
                record
            )

        return record

    def summary(
        self,
        *,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:

        with self._lock:

            records = [
                record
                for record in self._records
                if (
                    run_id is None
                    or record.run_id
                    == run_id
                )
            ]

        currencies = {
            record.currency
            for record in records
        }

        totals: Dict[
            str,
            Decimal
        ] = {}

        for record in records:

            totals[
                record.currency
            ] = (
                totals.get(
                    record.currency,
                    Decimal("0")
                )
                + record.total_cost
            )

        return {
            "request_count":
                len(records),

            "total_cost_by_currency":
                {
                    currency: str(amount)
                    for currency, amount
                    in totals.items()
                },

            "single_currency":
                (
                    next(iter(currencies))
                    if len(currencies) == 1
                    else None
                ),
        }

    def _get_pricing(
        self,
        provider: str,
        model: str,
    ) -> ModelPricing:

        key = (
            provider.casefold(),
            model.casefold(),
        )

        with self._lock:
            pricing = (
                self._pricing.get(
                    key
                )
            )

        if pricing is None:

            raise KeyError(
                "Pricing is not configured for "
                f"{provider}/{model}."
            )

        return pricing
from dataclasses import dataclass
from typing import Any, Dict, Optional
from app.core.exceptions import ValidationException
from app.models.compensation import CompensationRule


@dataclass
class CompensationCalculationResult:
    """Breakdown of statutory compensation calculated according to RFCTLARR Act 2013."""

    land_area_acres: float
    market_value_per_acre: float
    multiplier_factor: float
    asset_valuation: float
    basic_land_value: float
    multiplied_land_value: float
    market_value_plus_assets: float
    solatium_percentage: float
    solatium_amount: float
    interest_percentage: float
    interest_amount: float
    total_compensation: float
    rule_id: str
    rule_version: str


class CompensationRulesEngine:
    """Decoupled, versioned statutory calculation engine.
    
    Ensures legal formulas (Section 26-30 of the RFCTLARR Act, 2013) are NOT hardcoded
    into API route handlers. Formulas are driven dynamically by CompensationRule entities.
    """

    def __init__(self, rule: CompensationRule):
        self.rule = rule

    def calculate(
        self,
        *,
        land_area_acres: float,
        market_value_per_acre: float,
        multiplier_factor: Optional[float] = None,
        asset_valuation: float = 0.0,
        custom_solatium_pct: Optional[float] = None,
        custom_interest_pct: Optional[float] = None,
    ) -> CompensationCalculationResult:
        """Execute formula according to Section 26-30 of RFCTLARR Act 2013."""
        if land_area_acres <= 0:
            raise ValidationException("Land area in acres must be greater than zero.")
        if market_value_per_acre <= 0:
            raise ValidationException("Market value per unit (₹/acre) must be greater than zero.")

        # Default multiplier to urban (1.0) if omitted
        multiplier = multiplier_factor if multiplier_factor is not None else self.rule.urban_multiplier
        if multiplier < 1.0 or multiplier > 2.0:
            raise ValidationException(
                f"Statutory multiplier factor must be between 1.0 (urban) and 2.0 (rural). Received: {multiplier}"
            )

        solatium_pct = custom_solatium_pct if custom_solatium_pct is not None else self.rule.solatium_percentage
        interest_pct = custom_interest_pct if custom_interest_pct is not None else self.rule.additional_interest_percentage

        # 1. Section 26: Basic Land Value
        basic_land_value = round(land_area_acres * market_value_per_acre, 2)

        # 2. Section 26(2) & First Schedule: Multiplier factor applied to basic land value
        multiplied_land_value = round(basic_land_value * multiplier, 2)

        # 3. Section 29: Valuation of assets attached to land (structures, trees, crops, wells)
        clean_asset_valuation = max(0.0, float(asset_valuation))
        market_value_plus_assets = round(multiplied_land_value + clean_asset_valuation, 2)

        # 4. Section 30(1): Solatium (100% on total market value of land + assets)
        solatium_amount = round(market_value_plus_assets * (solatium_pct / 100.0), 2)

        # 5. Section 30(3): Additional Interest (12% per annum on multiplied land value)
        interest_amount = round(multiplied_land_value * (interest_pct / 100.0), 2)

        # 6. Section 31: Total Statutory Award Compensation
        total_compensation = round(market_value_plus_assets + solatium_amount + interest_amount, 2)

        return CompensationCalculationResult(
            land_area_acres=land_area_acres,
            market_value_per_acre=market_value_per_acre,
            multiplier_factor=multiplier,
            asset_valuation=clean_asset_valuation,
            basic_land_value=basic_land_value,
            multiplied_land_value=multiplied_land_value,
            market_value_plus_assets=market_value_plus_assets,
            solatium_percentage=solatium_pct,
            solatium_amount=solatium_amount,
            interest_percentage=interest_pct,
            interest_amount=interest_amount,
            total_compensation=total_compensation,
            rule_id=self.rule.id,
            rule_version=self.rule.version,
        )


def get_default_statutory_rule() -> CompensationRule:
    """Return default in-memory statutory rule object for fallback or initial bootstrap."""
    return CompensationRule(
        id="RULE-RFCTLARR-2013-V1",
        name="RFCTLARR Standard Statutory Rule 2013",
        version="v1.0",
        is_active=True,
        state=None,
        solatium_percentage=100.0,
        additional_interest_percentage=12.0,
        urban_multiplier=1.0,
        rural_multiplier_min=1.5,
        rural_multiplier_max=2.0,
        description="Standard statutory compensation formulation under Sections 26-30 of the RFCTLARR Act 2013.",
    )


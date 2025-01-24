from dataclasses import dataclass

from aisle.parser.nodes.legend import LegendSelector


@dataclass(init=False)
class StylingAttributes:
    bg: str | None = None
    fg: str | None = None

    def __init__(self, **kwargs):
        for kw_k, kw_v in kwargs.items():
            setattr(self, kw_k, kw_v)


@dataclass
class LegendStyling:
    selector: LegendSelector
    attrs: StylingAttributes
    description: str

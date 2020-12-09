from dataclasses import dataclass
from typing import Optional, Iterator, Union, Tuple
from collections.abc import MutableMapping

from arrowhead_client.system import ArrowheadSystem
from arrowhead_client.service import Service

OrchestrationRuleTuple = Tuple[Service, ArrowheadSystem, str, Optional[str]]

@dataclass(frozen=True)
class OrchestrationRule:
    consumed_service: Service
    provider_system: ArrowheadSystem
    method: str
    authorization_token: Optional[str] = None

class OrchestrationRuleContainer(MutableMapping):
    def __init__(self):
        self._rulecontainer = {}

    def __getitem__(self, key: str) -> OrchestrationRule:
        return self._rulecontainer[key]

    def __setitem__(
            self,
            key: str,
            item: Union[OrchestrationRule, OrchestrationRuleTuple]) -> None:
        if isinstance(item, OrchestrationRule):
            self._rulecontainer[key] = item
        else:
            # If given a tuple of values, create the orchestrationrule
            # TODO: This may not be necessary
            self._rulecontainer[key] = OrchestrationRule(*item)

    def __delitem__(self, key: str) -> None:
        del self._rulecontainer[key]

    def __iter__(self) -> Iterator:
        return iter(self._rulecontainer)

    def __len__(self) -> int:
        return len(self._rulecontainer)

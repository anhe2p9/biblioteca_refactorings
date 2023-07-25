from abc import abstractmethod, ABC
from typing import Any

from flamapy.metamodels.fm_metamodel.models import FeatureModel


class FMRefactoring(ABC):

    @staticmethod
    @abstractmethod
    def get_name() -> str:
        """Name of the refactoring."""
        pass

    @staticmethod
    @abstractmethod
    def get_description() -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_language_construct_name() -> str:
        pass

    @staticmethod
    @abstractmethod
    def transform(model: FeatureModel, instance: Any) -> FeatureModel:
        """Apply the refactoring to the given instance."""
        pass

    @staticmethod
    @abstractmethod
    def get_instances(model: FeatureModel) -> list[Any]:
        """Return the instances of the refactoring that can be applied to the source model."""
        pass

    @staticmethod
    @abstractmethod
    def is_applicable(model: FeatureModel) -> bool:
        """Return whether the refactoring is applicable to the given model."""
        pass

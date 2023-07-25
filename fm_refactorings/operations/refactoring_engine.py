import inspect
import importlib

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Constraint

from fm_refactorings.models import FMRefactoring
from fm_refactorings import transformations as REFACTORINGS
from fm_refactorings.transformations import __all__ as REFACTORINGS_NAMES


class RefactoringEngine():

    def __init__(self) -> None:
        pass

    def get_refactorings(self) -> list[FMRefactoring]:
        """Return the list of all refactorings available."""
        return [self.get_refactoring_from_name(ref_name) for ref_name in REFACTORINGS_NAMES]

    def get_refactoring_for_instance(self, fm: FeatureModel, instance: Feature | Constraint) -> FMRefactoring:
        """Given a FM and an instance (feature or constraint), returns the applicable refactoring of the instance."""
        for refactoring_name in REFACTORINGS_NAMES:
            refactoring = self.get_refactoring_from_name(refactoring_name)
            if instance in refactoring.get_instances(fm):
                return refactoring
        return None
    
    def apply_refactoring(self, refactoring: FMRefactoring, fm: FeatureModel, instance: Feature | Constraint) -> FeatureModel:
        """Apply the given refactoring to the given instance (feature or constraint) of the given FM."""
        return refactoring.transform(fm, instance)

    def apply_refactorings(self, refactoring: FMRefactoring, fm: FeatureModel) -> FeatureModel:
        """Apply the given refactoring to all instances (features or constraints) of the given FM."""
        instances = refactoring.get_instances(fm)
        for instance in instances:
            print(f'|->Applying {refactoring.get_name()} to instance {str(instance)}...')
            fm = self.apply_refactoring(refactoring, fm, instance)
        return fm
    
    def simplify_model(self, fm: FeatureModel) -> FeatureModel:
        """Apply all possible refactorings to all instances (features or constraints) of the given FM."""
        refactorings = self.get_refactorings()
        for refactoring in refactorings:
            fm = self.apply_refactorings(refactoring, fm)
        return fm

    def get_refactoring_from_name(self, refactoring_name: str) -> FMRefactoring:
        """Given the name of a refactoring class, return the instance class of the refactoring."""
        modules = inspect.getmembers(REFACTORINGS)
        modules = filter(lambda x: inspect.ismodule(x[1]), modules)
        modules = [importlib.import_module(m[1].__name__) for m in modules]
        class_ = next((getattr(m, refactoring_name) for m in modules if hasattr(m, refactoring_name)), None)
        return class_

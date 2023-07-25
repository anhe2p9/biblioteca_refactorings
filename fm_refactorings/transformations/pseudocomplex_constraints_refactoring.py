from flamapy.metamodels.fm_metamodel.models import FeatureModel, Constraint

from fm_refactorings.models import FMRefactoring
from fm_refactorings.utils import constraints_utils


class PseudoComplexConstraintRefactoring(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Pseudo-complex constraint refactoring'

    @staticmethod
    def get_description() -> str:
        return ("It splits a pseudo-complex constraint in multiple constraints dividing it "
                "by the AND operator when possible.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Pseudo-complex constraint'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Constraint]:
        # TODO: re-implement for efficiency
        return [ctc for ctc in model.get_constraints() if constraints_utils.is_pseudo_complex_constraint(ctc)]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        # TODO: re-implement for efficiency
        return len(PseudoComplexConstraintRefactoring.get_instances(model)) > 0

    @staticmethod
    def transform(model: FeatureModel, instance: Constraint) -> FeatureModel:
        model.ctcs.remove(instance)
        for ctc in constraints_utils.split_constraint(instance):
            model.ctcs.append(ctc)
        return model
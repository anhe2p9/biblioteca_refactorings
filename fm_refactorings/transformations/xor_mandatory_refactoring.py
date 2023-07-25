from typing import Any

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature

from fm_refactorings.models import FMRefactoring


class XorMandatoryRefactoring(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Xor-group with mandatory subfeature refactoring'
    
    @staticmethod
    def get_description() -> str:
        return ("It transforms the xor-group with a mandatory subfeature into an or-group "
                "with cardinality <0..0> (dead features) and a mandatory subfeature.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Xor-group with mandatory subfeature'

    @staticmethod
    def get_name() -> str:
        return 'Xor-group with mandatory subfeature refactoring'
    
    @staticmethod
    def get_instances(model: FeatureModel) -> list[Any]:
        return [f for f in model.get_features() if is_xor_group_with_mandatory(f)]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return True

    @staticmethod
    def transform(model: FeatureModel, instance: Feature) -> FeatureModel:
        if instance is None:
            raise Exception(f'There is not feature with name "{instance.name}".')
        if not is_xor_group_with_mandatory(instance):
            raise Exception(f'Feature "{instance.name}" is not a cardinality group.')
        
        xor_group = next((r for r in instance.get_relations() if r.is_alternative()), None)
        if xor_group is not None:    
            mandatory_feature = next((c for c in xor_group.children if c.is_mandatory()), None)
            if mandatory_feature is not None:
                xor_group.card_min = 0
                xor_group.card_max = 0
                xor_group.children.remove(mandatory_feature)
        return model


def is_xor_group_with_mandatory(feature: Feature) -> bool:
    xor_group = next((r for r in feature.get_relations() if r.is_alternative()), None)
    return (xor_group is not None and 
            any(r.children[0] in xor_group.children for r in feature.get_relations() 
                if r.is_mandatory()))

from typing import Any

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from fm_refactorings.models import FMRefactoring


class OrMandatoryRefactoring(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Or-group with mandatory subfeature refactoring'
    
    @staticmethod
    def get_description() -> str:
        return ("It transforms the or-group with mandatory subfeatures into an and-group "
                "with mandatory and optional subfeatures.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Or-group with mandatory subfeature'
    
    @staticmethod
    def get_instances(model: FeatureModel) -> list[Any]:
        return [f for f in model.get_features() if is_or_group_with_mandatory(f)]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return True

    @staticmethod
    def transform(model: FeatureModel, instance: Feature) -> FeatureModel:
        if instance is None:
            raise Exception(f'There is not feature with name "{instance.name}".')
        if not is_or_group_with_mandatory(instance):
            raise Exception(f'Feature "{instance.name}" is not an or group with mandatory features.')

        or_group = next((r for r in instance.get_relations() if r.is_or()), None)
        if or_group is not None:
            for child in or_group.children:
                if not child.is_mandatory():
                    r_opt = Relation(instance, [child], 0, 1)  # optional
                    instance.add_relation(r_opt)
            instance.get_relations().remove(or_group)        
        return model


def is_or_group_with_mandatory(feature: Feature) -> bool:
    or_group = next((r for r in feature.get_relations() if r.is_or()), None)
    return (or_group is not None and 
            any(r.children[0] in or_group.children for r in feature.get_relations() 
                if r.is_mandatory()))

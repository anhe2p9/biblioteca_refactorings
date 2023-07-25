from typing import Any

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation

from fm_refactorings.models import FMRefactoring
from fm_refactorings.utils import fm_utils


class MutexGroupRefactoring(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Mutex group refactoring'

    @staticmethod
    def get_description() -> str:
        return ("It changes the mutex group to an and-group with one optional abstract "
                "sub-feature f which becomes an alternative-group with the original sub-features.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Mutex group'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Feature]:
        return [f for f in model.get_features() if f.is_mutex_group()]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return True

    @staticmethod
    def transform(model: FeatureModel, instance: Feature) -> FeatureModel:
        if instance is None:
            raise Exception(f'There is not feature with name "{instance.name}".')
        if not instance.is_mutex_group():
            raise Exception(f'Feature {instance.name} is not a mutex group.')
    
        new_name = fm_utils.get_new_feature_name(model, instance.name)
        f_p = Feature(name=new_name, parent=instance, is_abstract=True)
        r_opt = Relation(instance, [f_p], 0, 1)  # optional
        r_mutex = next((r for r in instance.get_relations() if r.is_mutex()), None)
        r_mutex.parent = f_p
        r_mutex.card_min = 1  # xor
    
        for child in r_mutex.children:
            child.parent = f_p

        instance.get_relations().remove(r_mutex)

        # Add relations to features
        instance.add_relation(r_opt)
        f_p.add_relation(r_mutex)
        return model

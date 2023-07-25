from flamapy.core.models.ast import AST, ASTOperation, Node
from flamapy.metamodels.fm_metamodel.models import (
    FeatureModel,
    Feature, 
    Relation, 
    Constraint,
)

from fm_refactorings.models import FMRefactoring
from fm_refactorings.utils import fm_utils, constraints_utils


class StrictComplexConstraintRefactoring(FMRefactoring):

    ABSTRACT_AUX_OR_FEATURE_NAME = 'OR_FEATURE'

    @staticmethod
    def get_name() -> str:
        return 'Strict-complex constraint refactoring'

    @staticmethod
    def get_description() -> str:
        return ("It transforms a strict-complex constraint to an additional abstract feature tree "
                "and a new set of simple constraints.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Strict-complex constraint'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Constraint]:
        return [ctc for ctc in model.get_constraints() 
                if constraints_utils.is_complex_constraint(ctc)]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return len(StrictComplexConstraintRefactoring.get_instances(model)) > 0

    @staticmethod
    def transform(model: FeatureModel, instance: Constraint) -> FeatureModel:
        model.ctcs.remove(instance)
        ctcs_names = [ctc.name for ctc in model.get_constraints()]
        features_dict = get_features_clauses(instance)  # NOT before negatives (dict)
        if len(features_dict) == 1:
            feature_name = list(features_dict.keys())[0]
            if features_dict[feature_name]:
                model = fm_utils.commitment_feature(model, feature_name)
            else:
                model = fm_utils.deletion_feature(model, feature_name)
        else:
            new_or = Feature(fm_utils.get_new_feature_name(model, 
                             StrictComplexConstraintRefactoring.ABSTRACT_AUX_OR_FEATURE_NAME), 
                             is_abstract=True)
            fm_utils.add_auxiliary_feature_attribute(new_or)
            features = []
            for f in features_dict.keys():
                new_feature = Feature(fm_utils.get_new_feature_name(model, f), 
                                      parent=new_or, is_abstract=True)
                fm_utils.add_auxiliary_feature_attribute(new_feature)
                features.append(new_feature)
                ast_op = ASTOperation.REQUIRES if features_dict[f] else ASTOperation.EXCLUDES
                ctc = Constraint(constraints_utils.get_new_ctc_name(ctcs_names, 'CTC'), 
                                 AST.create_binary_operation(ast_op, 
                                 Node(new_feature.name), Node(f)))
                ctcs_names.append(ctc.name)
                model.ctcs.append(ctc)

            # New branch with OR as root
            rel_or = Relation(new_or, features, 1, len(features))  # OR
            new_or.add_relation(rel_or)
        
            # New root (only needed if the root feature is a group)
            if model.root.is_group():
                new_root = Feature(fm_utils.get_new_feature_name(model, 'root'), is_abstract=True)
                fm_utils.add_auxiliary_feature_attribute(new_root)
                rel_1 = Relation(new_root, [model.root], 1, 1)  # mandatory
                new_root.add_relation(rel_1)
                model.root.parent = new_root
            else:
                new_root = model.root
            rel_2 = Relation(new_root, [new_or], 1, 1)  # mandatory
            new_root.add_relation(rel_2)
            new_or.parent = new_root
            model.root = new_root

        return model


def get_features_clauses(instance: Constraint) -> dict[str, bool]:
    """Returns a dictionary of 'feature name -> bool', 
    that sets 'bool' to 'false' if the feature has a negation."""
    features = {}
    clauses = instance.ast.to_cnf()
    stack = [clauses.root]
    while stack:
        node = stack.pop()
        if node.is_unique_term():
            features[node.data] = True
        elif node.is_unary_op():
            features[node.left.data] = False
        elif node.is_binary_op():
            stack.append(node.right)
            stack.append(node.left)
    return features

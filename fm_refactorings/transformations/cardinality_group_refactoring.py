import itertools
import functools

from flamapy.metamodels.fm_metamodel.models import FeatureModel, Feature, Relation, Constraint
from flamapy.core.models.ast import AST, ASTOperation, Node

from fm_refactorings.models import FMRefactoring


class CardinalityGroupRefactoring(FMRefactoring):

    @staticmethod
    def get_name() -> str:
        return 'Cardinality group refactoring'

    @staticmethod
    def get_description() -> str:
        return ("It changes the cardinality group to an and-group where all sub-features are "
                "optionals and add a new complex constraint with all feature combinations of the "
                "sub-features where each combination has at least 'a' and at most 'b' elements.")

    @staticmethod
    def get_language_construct_name() -> str:
        return 'Cardinality group'

    @staticmethod
    def get_instances(model: FeatureModel) -> list[Feature]:
        return [f for f in model.get_features() if f.is_cardinality_group()]

    @staticmethod
    def is_applicable(model: FeatureModel) -> bool:
        return True

    @staticmethod
    def transform(model: FeatureModel, instance: Feature) -> FeatureModel:
        if instance is None:
            raise Exception(f'There is not feature with name "{instance.name}".')
        if not instance.is_cardinality_group():
            raise Exception(f'Feature {instance.name} is not a cardinality group.')
    
        r_card = next((r for r in instance.get_relations() if r.is_cardinal()), None)
        instance.get_relations().remove(r_card)

        for child in r_card.children:
            r_opt = Relation(instance, [child], 0, 1)  # optional
            instance.add_relation(r_opt)
    
        constraint = get_constraint_for_cardinality_group(instance, r_card)
        model.ctcs.append(constraint)
        return model


def create_and_constraints_for_cardinality_group(positives: list[Feature], negatives: list[Feature]) -> Node:
    elements = [Node(f.name) for f in positives]
    elements += [AST.create_unary_operation(ASTOperation.NOT, Node(f.name)).root for f in negatives]
    result = functools.reduce(lambda left, right: AST.create_binary_operation(ASTOperation.AND, left, right).root, elements)
    return result


def get_or_constraints_for_cardinality_group(feature: Feature, relation: Relation) -> Node:
    card_min = relation.card_min
    card_max = relation.card_max
    children = set(relation.children)
    and_nodes = []
    for k in range(card_min, card_max + 1):
        combi_k = list(itertools.combinations(relation.children, k))
        for positives in combi_k:
            negatives = children - set(positives)
            and_ctc = create_and_constraints_for_cardinality_group(positives, negatives)
            and_nodes.append(and_ctc)
    result = functools.reduce(lambda left, right: Node(ASTOperation.OR, left, right), and_nodes)
    return result

def get_constraint_for_cardinality_group(feature: Feature, relation: Relation) -> Constraint:
    ast = AST.create_binary_operation(ASTOperation.IMPLIES,
                                      Node(feature.name),
                                      get_or_constraints_for_cardinality_group(feature, relation))
    return Constraint('CG', ast)
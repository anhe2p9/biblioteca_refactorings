import copy
from collections.abc import Callable

from flamapy.metamodels.fm_metamodel.models import (
    FeatureModel, 
    Feature, 
    Relation, 
    Constraint, 
    Attribute
)

from flamapy.core.models.ast import ASTOperation


def get_right_feature_name(instance: Constraint) -> str:
    if instance.ast.root.right.data is ASTOperation.NOT:
        not_operation = instance.ast.root.right
        right_feature_name_ctc = not_operation.left.data
    else:
        right_feature_name_ctc = instance.ast.root.right.data
    return right_feature_name_ctc


def get_left_feature_name(instance: Constraint) -> str:
    if instance.ast.root.left.data is ASTOperation.NOT:
        not_operation = instance.ast.root.left
        left_feature_name_ctc = not_operation.left.data
    else:
        left_feature_name_ctc = instance.ast.root.left.data
    return left_feature_name_ctc


def remove_abstract_leaf_without_reference(model: FeatureModel) -> FeatureModel:
    '''Removes all abstract LEAF which richt feature is not in tree (before joining subtrees)'''
    model_if_none = model
    if model is not None:
        for feat in model.get_features():
            ctc = next((c for c in model.get_constraints() if get_left_feature_name(c) == feat.name), None)
            if feat.is_leaf() and feat.is_abstract:
                if ctc is not None:
                   if model.get_feature_by_name(get_right_feature_name(ctc)) not in model.get_features():
                        model = eliminate_node_from_tree(model, feat)
    if model is None:
        model = model_if_none
    return model


def get_new_feature_name(fm: FeatureModel, name: str) -> str:
    count = 1
    new_name = f'{name}'
    while fm.get_feature_by_name(new_name) is not None:
        new_name = f'{name}{count}'
        count += 1
    return new_name


def get_new_feature_complex_name(fm: FeatureModel, name: str) -> str:
    count = 1
    new_name = f'{name}'
    while fm.get_feature_by_name(new_name) is not None:
        new_name = f'{name}_{count}'
        count += 1
    return new_name


def get_new_ctc_name(ctcs_names: list[str], name: str) -> str:
    count = 1
    new_name = f'{name}'
    while new_name in ctcs_names:
        new_name = f'{name}{count}'
        count += 1
    return new_name


def get_new_attr_name(header: list, name: str) -> str:
    count = 1
    new_name = f'{name}'
    while new_name in header:
        new_name = f'{name}{count}'
        count += 1
    return new_name


def remove_abstract_child(fm: FeatureModel, feature: Feature) -> FeatureModel:
    feature_relations = feature.get_relations()
    feature_next_rel = next(r for r in feature_relations)
    feature_next_abstract = next(c for c in feature.get_children())
    if len(feature_relations)==1 and feature_next_rel.is_mandatory() and feature_next_abstract.is_abstract:
            feature.get_relations().remove(feature_next_rel)
            fm.root = feature_next_abstract
            fm = remove_abstract_child(fm, feature_next_abstract)
    return fm


def is_there_node(parent: Feature, child_node: Feature) -> Feature:
    result = ''
    for child in parent.get_children():
        if child==child_node:
            result = child
    return result


def convert_parent_to_mandatory(fm: FeatureModel, f: Feature) -> FeatureModel:
    parent = f.get_parent()
    if parent is not None:
        rel_mand = next((r for r in parent.relations if f in r.children), None)
        if rel_mand is not None:
            rel_mand.card_min = 1
        fm = convert_parent_to_mandatory(fm, parent)
    return fm

def get_model_plus(model: FeatureModel, f_list: list[Feature]) -> FeatureModel:
    for f in f_list:
        if model is not None:
            model = add_node_to_tree(model, f)
    return model

def get_model_less(model: FeatureModel, f_list: list[Feature]) -> FeatureModel:
    for f_left_less in f_list:
        if model is not None:
            model = eliminate_node_from_tree(model, f_left_less)
    return model


def add_node_to_tree(model: FeatureModel, node: Feature) -> FeatureModel:
    if node not in model.get_features(): 
        #  If model does not contain F (node), the result is None
        return None
    elif model.root==node:
        # If F (node) is the root of model, the result is model. 
        return model
    else:
        parent = node.parent  # Let the parent feature of F (node) be P (parent).
        if (not parent.is_group()) and node.is_optional():  # parent.is_root() or parent.is_mandatory() or parent.is_optional()
            # If P is a MandOpt feature and F is an optional subfeature, make F a mandatory subfeature of P
            rel_mand = next((r for r in parent.get_relations() if node in r.children), None)
            rel_mand.card_min = 1
        elif parent.is_alternative_group() and (len(parent.get_children()) > 2 or (parent.get_children()[0].name != 
                                                parent.get_children()[1].name)):
            # If P is an Xor feature, make P a MandOpt feature which has F as single
            # mandatory subfeature and has no optional subfeatures. All other
            # subfeatures of P are removed from the tree.
            rel = next((r for r in parent.get_relations()), None)
            parent.get_relations().remove(rel)
            r_mand = Relation(parent, [node], 1, 1)  # mandatory
            parent.add_relation(r_mand)
        elif parent.is_or_group():
            # If P is an Or feature, make P a MandOpt feature which has F as single
            # mandatory subfeature, and has all other subfeatures of P as optional subfeatures. 
            relations = [r for r in parent.get_relations()]
            r_mand = Relation(parent, [node], 1, 1)  # mandatory
            parent.add_relation(r_mand)
            for child in parent.get_children():
                if child!=node:
                    r_opt = Relation(parent, [child], 0, 1)  # optional
                    parent.add_relation(r_opt)
            for rel in relations:
                parent.get_relations().remove(rel)

        # Convert P to mandatory.
        model = convert_parent_to_mandatory(model, parent)

    # GOTO step 2 with P instead of F.
    model = add_node_to_tree(model, parent)
    # print(f'NEW MODEL PLUS after: {model}')
    return model


def eliminate_node_from_tree(model: FeatureModel, node: Feature) -> FeatureModel:
    if node not in model.get_features():
        # If model does not contain node, the result is model.
        return model
    elif model.root==node:
        # If F is the root of T, the result is NIL.
        print(f'model.root: {model.root}')
        return None
    else:
        parent = node.parent  # Let the parent feature of F be P.
        if node.is_mandatory() and not parent.is_group():  # parent.is_root() or parent.is_mandatory() or parent.is_optional()
            # If P is a MandOpt feature and F is a mandatory subfeature of P, GOTO
            # step 2 with P instead of F.
            print(f'node mandatory: {node.name}')
            model = eliminate_node_from_tree(model, parent)
        elif not parent.is_group() and node.is_optional():  # parent.is_root() or parent.is_mandatory() or parent.is_optional()
            # If P is a MandOpt feature and F is an optional subfeature of P, delete F.
            r_opt = next((r for r in parent.get_relations() if r.is_optional() 
                                                               and node in r.children), None)
            parent.get_relations().remove(r_opt)
            print(f'node optional: {node.name}')
        elif parent.is_alternative_group() and len(parent.get_children()) == 2 and parent.get_children()[0].name == parent.get_children()[1].name:
            print(f'node xor iguales: {node.name}')
            node1 = parent.get_children()[0]
            node2 = parent.get_children()[1]
            rel = next((r for r in parent.get_relations()), None)

            fm1 = FeatureModel(node1, None)
            fm = FeatureModel(node, None)

            node_to_maintain = None  # the other will be eliminated
            if fm1 == fm:
                node_to_maintain = node2
            else:
                node_to_maintain = node1
            rel.children = [node_to_maintain]
            rel.card_min = 1
            rel.card_max = 1
            print(f'Relation: {str(rel)}')
        elif parent.is_or_group() or parent.is_alternative_group():
            print(f'node group: {node.name}')
            # If P is an Xor feature or an Or feature, delete F; if P has only one
            # remaining subfeature, make P a MandOpt feature and
            # its subfeature a mandatory subfeature. 
            rel = next((r for r in parent.get_relations()), None)
            rel.children.remove(node)  # Be careful!! Dangerous because features can be duplicated and they are only compared by names. Solution is to compare the whole FM as in the previous case.
            if rel.card_max > 1:
                rel.card_max -= 1
            if len(rel.children) == 1:
                rel.card_min = 1
    return model


def to_unique_features(fm: FeatureModel) -> FeatureModel:
    """Replace duplicated features names."""
    if not hasattr(fm, 'dict_references'):
            fm.dict_references = {}
    unique_features_names = []
    for f in fm.get_features():
        if f.name not in unique_features_names:
            unique_features_names.append(f.name)
        else:
            new_name = get_new_feature_name(fm, f.name)
            fm.dict_references[new_name] = f.name
            f.name = new_name
            unique_features_names.append(f.name)
    return fm


def add_auxiliary_feature_attribute(feature: Feature) -> Feature:
    aux_attribute = Attribute(name='aux', domain=None, default_value=None, null_value=None)
    aux_attribute.set_parent(feature)
    feature.add_attribute(aux_attribute)
    return feature 


def is_auxiliary_feature(feature: Feature) -> bool:
    return any(a for a in feature.get_attributes() if a.name == 'aux')
    

def commitment_feature(fm: FeatureModel, feature_name: str) -> FeatureModel:
    """Given a feature diagram T and a feature F, this algorithm computes T(+F) 
    whose products are precisely those products of T with contain F.

    The algorithm is an adaptation from:
        [Broek2008 @ SPLC: Elimination of constraints from feature trees].
    """
    feature = fm.get_feature_by_name(feature_name) 
    # Step 1. If T does not contain F, the result is NIL.
    if feature is None:
        fm.root = None  # Clear model
        return None
    else:
        feature_to_commit = feature
        while feature_to_commit != fm.root:  # Step 2. If F is the root of T, the result is T.
            parent = feature_to_commit.get_parent()  # Step 3. Let the parent feature of F be P.
            # If P is a MandOpt feature and F is an optional subfeature, 
            # make F a mandatory subfeature of P.
            if not parent.is_group() and feature_to_commit.is_optional():  
                rel = next((r for r in parent.get_relations() if feature_to_commit in r.children), None)
                rel.card_min = 1
            # If P is an Xor feature, 
            # make P a MandOpt feature which has F as single mandatory subfeature 
            # and has no optional subfeatures. All other subfeatures of P are removed from the tree.
            elif parent.is_alternative_group(): 
                for child in parent.get_children():
                    if child != feature_to_commit:
                        child.get_relations().clear()
                parent.get_relations()[0].children = [feature_to_commit]
            # If P is an Or feature, 
            # make P a MandOpt feature which has F as single mandatory subfeature, 
            # and has all other subfeatures of P as optional subfeatures.
            elif parent.is_or_group():  
                parent_relations = parent.get_relations()
                or_relation = parent_relations[0]
                or_relation.children.remove(feature_to_commit)
                parent_relations.remove(or_relation)
                new_mandatory_rel = Relation(parent, [feature_to_commit], 1, 1)
                parent_relations.append(new_mandatory_rel)
                for child in or_relation.children:
                    new_optional_rel = Relation(parent, [child], 0, 1)
                    parent_relations.append(new_optional_rel)
            # Step 4. GOTO step 2 with P instead of F.
            feature_to_commit = parent
    return fm


def deletion_feature(fm: FeatureModel, feature_name: str) -> FeatureModel:
    """Given a feature diagram T and a feature F, this algorithm computes T(-F) 
    whose products are precisely those products of T with do not contain F.

    The algorithm is an adaptation from:
        [Broek2008 @ SPLC: Elimination of constraints from feature trees].
    """
    feature = fm.get_feature_by_name(feature_name)
    if feature is not None:  # Step 1. If T does not contain F, the result is T.
        feature_to_delete = feature
        parent = feature_to_delete.get_parent()  # Step 2. Let the parent feature of F be P.
        # Step 3. If P is a MandOpt feature and F is a mandatory subfeature of P, 
        # GOTO step 4 with P instead of F.
        while feature_to_delete != fm.root and not parent.is_group() and feature_to_delete.is_mandatory():
            feature_to_delete = parent
            parent = feature_to_delete.get_parent()
        if feature_to_delete == fm.root:  # If F is the root of T, the result is NIL.
            fm.root = None  # Clear model
            return None
        # If P is a MandOpt feature and F is an optional subfeature of P, delete F.
        elif not parent.is_group() and feature_to_delete.is_optional():
            rel = next((r for r in parent.get_relations() if feature_to_delete in r.children), None)
            parent.get_relations().remove(rel)
            feature_to_delete.get_relations().clear()
        # If P is an Xor feature or an Or feature, delete F; if P has only one remaining subfeature, 
        # make P a MandOpt feature and its subfeature a mandatory subfeature.
        elif parent.is_alternative_group() or parent.is_or_group():
            rel = parent.get_relations()[0]
            if feature_to_delete in rel.children:
                rel.children.remove(feature_to_delete)
            feature_to_delete.get_relations().clear()
            if rel.card_max > 1:
                rel.card_max -= 1
    return fm


def transform_tree(functions: list[Callable], fm: FeatureModel, features: list[str], copy_tree: bool) -> FeatureModel:
    """Apply a list of functions (commitment_feature or deletion_feature) 
    to the tree of the feature model. 
    
    For each function, it uses each feature (in order) in the provided list as argument.
    """
    if copy_tree:
        tree = FeatureModel(copy.deepcopy(fm.root), fm.get_constraints())
    else:
        tree = fm
    for func, feature in zip(functions, features):
        if tree is not None:
            tree = func(tree, feature)
    return tree


def get_trees_from_original_root(fm: FeatureModel) -> list[FeatureModel]:
    """Given a feature model with non-unique features, 
    returns the subtrees the root of which are the original root of the feature model.
    
    The original root of the feature model is the most top feature 
    that is not a XOR group with two or more identical children.
    """
    root = fm.root
    if root.is_alternative_group():
        child_name = root.get_children()[0].name
        if all(child.name == child_name for child in root.get_children()):
            trees = []
            for child in root.get_children():
                subtrees = get_trees_from_original_root(FM(child, fm.get_constraints()))
                trees.extend(subtrees)
            return trees
    return [fm]


def filter_products(fm: FeatureModel, configurations: list[list[str]]) -> list[list[str]]:
    """Given a list of configurations return it with the configurations filtered.
    
    This method takes into account that the features in the FM can be not unique. 
    That is, features can have its corresponding features in a dictionary
    indicating that the feature is non-unique and appears in other part of the FM.
    The corresponding value in the dictionary points to the original feature.

    The filters performed are the following:
      a) Remove abstract features.
      b) Substitute non-unique features with the original one.
      c) Remove duplicate features.
    """
    filtered_configs = set()
    for config in configurations:
        c = set()
        for f in config:
            feature = fm.get_feature_by_name(f)
            if not feature.is_abstract:
                #original_feature_name = get_original_feature_from_duplicates(f, fm.get_features())
                original_feature_name = feature.name
                c.add(original_feature_name)
        filtered_configs.add(frozenset(c))
    return filtered_configs


def get_original_feature_from_duplicates(feature_name: str, features: list[Feature]) -> str:
    names = [f.name for f in features if f.name.startswith(feature_name) or feature_name.startswith(f.name)]
    names.sort(key=len)
    return names[0]
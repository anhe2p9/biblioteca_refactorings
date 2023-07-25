import os
import sys
import argparse

from flamapy.metamodels.fm_metamodel.transformations import UVLReader, UVLWriter

from fm_refactorings.operations import RefactoringEngine
from fm_refactorings.transformations import __all__ as REFACTORINGS_NAMES


def main(fm_filepath: str, instance_identifier: str = None, refactoring_name: str = None):
    # Get feature model name
    path, filename = os.path.split(fm_filepath)
    filename = ''.join(filename.split('.')[:-1])

    # Load the feature model
    print(f'Reading feature model from {fm_filepath}...')
    fm = UVLReader(fm_filepath).transform()

    refactoring_engine = RefactoringEngine()
    if instance_identifier:
        # Get feature from feature name
        feature = fm.get_feature_by_name(instance_identifier)
        if feature is None:
            try:
                instance_identifier = int(instance_identifier)
                if instance_identifier < 0 or instance_identifier >= len(fm.get_constraints()):
                    sys.exit(f'The instance {instance_identifier} is not a valid constraint in the given FM.')
                constraint = fm.get_constraints()[instance_identifier]
            except ValueError:
                sys.exit(f'The instance {instance_identifier} is not a valid feature in the given FM.')

        # Get appropriate refactoring
        instance = feature if feature is not None else constraint
        refactoring = refactoring_engine.get_refactoring_for_instance(fm, instance)
        if refactoring is None:
            sys.exit(f'There is not applicable refactoring for instance {instance} in the given FM.')
        
        # Apply refactoring
        print(f'Applying {refactoring.get_name()} to instance {instance}...')
        fm_refactored = refactoring_engine.apply_refactoring(refactoring, fm, instance)
    elif refactoring_name:
        refactoring = refactoring_engine.get_refactoring_from_name(refactoring_name)
        if refactoring is None:
            sys.exit(f'There is not a valid refactoring for name {refactoring_name} in the library.')
        print(f'Applying {refactoring.get_name()} to all instances...')    
        fm_refactored = refactoring_engine.apply_refactorings(refactoring, fm)
    else:
        # Simply model
        fm_refactored = refactoring_engine.simplify_model(fm)


    # Output file for generated FM
    output_file = os.path.join(path, f'{filename}_refactored.uvl')

    # Serializing the feature model
    print(f'Serializing FM refactored model in {output_file} ...')
    UVLWriter(path=output_file, source_model=fm_refactored).transform()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Refactoring engine. Given a FM and optionally a feature/constraint i or a refactoring r, apply the appropriate refactoring (if any) to i, and generate the new FM. If not instance or refactoring is provided, all available refactorings are applied.')
    parser.add_argument('-fm', '--featuremodel', dest='feature_model', type=str, required=True, help='Input feature model in UVL format.')
    parser.add_argument('-i', '--instance', dest='instance', type=str, required=False, help='Instance to be refactored (name of the feature or number of constraint [0..n-1]).')
    parser.add_argument('-r', '--refactoring', dest='refactoring', type=str, required=False, help=f'Refactoring to be applied to all instances {[r for r in REFACTORINGS_NAMES]}.')
    args = parser.parse_args()

    if not args.feature_model.endswith('.uvl'):
        sys.exit(f'The FM must be in UVL format (.uvl).')
    main(args.feature_model, args.instance, args.refactoring)
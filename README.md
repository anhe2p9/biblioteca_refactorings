# Table of Contents
- [Table of Contents](#table-of-contents)
- [Biblioteca de refactorings para modelos de características](#biblioteca-de-refactorings-para-modelos-de-características)
  - [Requirements](#requirements)
  - [Download and installation](#download-and-installation)
  - [Execution of the refactoring engine](#execution-of-the-refactoring-engine)
  - [Execution of the tests](#execution-of-the-tests)
  
# Biblioteca de refactorings para modelos de características

## Requirements
- [Python 3.9+](https://www.python.org/)
- [Flama](https://flamapy.github.io/)

The library has been tested in Linux (Mint and Ubuntu) and Windows 11.


## Download and installation
1. Install [Python 3.9+](https://www.python.org/)
2. Download/Clone this repository and enter into the main directory.
3. Create a virtual environment: `python -m venv env`
4. Activate the environment: 
   
   In Linux: `source env/bin/activate`

   In Windows: `.\env\Scripts\Activate`

   ** In case that you are running Ubuntu, please install the package python3-dev with the command `sudo apt update && sudo apt install python3-dev` and update wheel and setuptools with the command `pip  install --upgrade pip wheel setuptools` right after step 4.
   
5. Install the dependencies: `pip install -r requirements.txt`


## Execution of the refactoring engine
You can use any feature model in the [models folder](models/) or in the [tests folder](tests/) to execute and test the library.

- **Help:** Provide help to execute the refactoring engine.
    `python main.py -h`

- **Apply a refactoring over an instance:** Apply a refactoring to the given instance (feature or constraint) of the provided feature model.
  
  - Execution: `python main.py -fm FEATURE_MODEL -i INSTANCE`
  - Inputs: 
    - The `FEATURE_MODEL` parameter specifies the file path of the feature model in UVL format.
    - The `INSTANCE` parameter specifies the name of feature or the number of the contraints (starting in 0) over which the appropriate refactoring will be applied.
  - Outputs:
    - A feature model file in UVL format with the given instance refactored.
  - Example: `python main.py -fm models/Pizzas_complex.uvl -i Specials`
  
- **Refactoring a variability language construct:** Apply a given refactoring to all instances in the provided feature model.
  
  - Execution: `python main.py -fm FEATURE_MODEL -r REFACTORING`
  - Inputs: 
    - The `FEATURE_MODEL` parameter specifies the file path of the feature model in UVL format.
    - The `REFACTORING` parameter specifies the name of the refactoring. This can be one of the available refactorings in the library: ['MutexGroupRefactoring', 'CardinalityGroupRefactoring', 'MultipleGroupDecompositionRefactoring', 'OrMandatoryRefactoring', 'XorMandatoryRefactoring', 'PseudoComplexConstraintRefactoring', 'StrictComplexConstraintRefactoring', 'RequiresConstraintRefactoring', 'ExcludesConstraintRefactoring'].

  - Outputs:
    - A feature model file in UVL format with all the instances of the given refactoring refactored.
  - Example: `python main.py -fm models/Pizzas_complex.uvl -r MutexGroupRefactoring`

- **Simplify feature model:** Apply all possible refactoring to all instance in the given feature model.
  
  - Execution: `python main.py -fm FEATURE_MODEL`
  - Inputs: 
    - The `FEATURE_MODEL` parameter specifies the file path of the feature model in UVL format.
  - Outputs:
    - A feature model file in UVL format with all the instances of all possible refactoring refactored.
  - Example: `python main.py -fm models/Pizzas_simple.uvl`

## Execution of the tests
`pytest -v tests/Test_refactorings.py`

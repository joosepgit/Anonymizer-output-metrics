# Anonymizer output validation
This project acts as a separate software component that can be integrated into larger anonymization tools. The main purpose is to measure the quality of anonymization in terms of analyzing the remaining risks and changes in the output dataset. Some calculations rely on comparing the raw input dataset to the presumably anonymized output dataset. The metrics implemented assume that the anonymization has been performed using hierarchy based generalization techniques and at least either k-anonymization or l-diversity has been enforced as the main privacy model. It can be used with either the input or the output dataset, both are not assumed for the software to work. However as some operations rely on comparison, results may be much less meaningful using only one dataset.

The project was created as a practical part of my bachelor's thesis and is therefore publicly available.

# Local setup
1. Clone the project into some arbitrary location.
2. Set the PYTHONPATH environment variable to the parent directory, where the projects root directory is.
For example say that you cloned the project into a folder '~/projects/'. Then you would have the projects
root directory 'output_validation' in your projects folder. In order for Python to find modules correctly
you would have to set PYTHONPATH equal to ~/projects/, **not ~/projects/output_validation/**.
Assuming that the directory projects exists in your users home directory,
in linux distributions, this can be done using the following command:
```
$ export PYTHONPATH=$HOME/projects
```
And in windows, this can be done through administrator powershell using the following command:
```
$env:PYTHONPATH = C:\Users\<youruser>\projects
```
3. Navigate into the projects root folder
```
$ cd output_validation
```
4. Install the necessary requirements
```
$ pip install -r requirements.txt
```
5. Add some input data to the inp/ directory, by default indata.csv and outdata.csv are looked for. 
Additionally, the configuration file conf.txt should be modified according to the privacy models and
anonymization methods used.
6. Run the code
```
$ python Validator.py
```


That's it on running the program with custom input. Additionally, there are tests that can be run
using the pytest framework. For simply running the test, run
```
$ pytest -v tests/
```
For running all tests with code coverage, run
```
$ coverage run --source . -m pytest -v tests/ && coverage report -m
```

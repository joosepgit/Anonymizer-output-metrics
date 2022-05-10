# Anonymizer output validation
This project acts as a separate software component that can be integrated into larger anonymization tools. The main purpose is to measure the quality of anonymization in terms of analyzing the remaining risks and changes in the output dataset. Some calculations rely on comparing the raw input dataset to the presumably anonymized output dataset. The metrics implemented assume that the anonymization has been performed using hierarchy based generalization techniques and at least either k-anonymization or l-diversity has been enforced as the main privacy model. It can be used with either the input or the output dataset, both are not assumed for the software to work. However as some operations rely on comparison, results may be much less meaningful using only one dataset.

The project was created as a practical part of my bachelor's thesis and is therefore publicly available.

# Local setup (tested on Ubuntu 20.04 LTS)
0. Create a directory called projects in your user home directory (Recommended if you are unsure where to clone it). Navigate into the directory before cloning.
1. Clone the project into some arbitrary location (or the created projects directory).
2. Install Python 3.8.10. (https://www.python.org/downloads/release/python-3810/)
3. Create a Python virtual environment:
Run the following command in the directory where you cloned this project **not in the projects root directory, but one directory above**.
```
~/projects$ python -m venv environment
```
A directory named environment is then generated.
4. Activate the environment
on linux based systems
```
~/projects$ source environment/bin/activate
```
or, if you have an existing conda installation
```
~/projects$ conda environment/bin/activate
```
or, on windows
```
C:\Users\Joosep\projects> environment\Scripts\activate.bat
```

After this step, your command line should look something like this:
```
(environment) jtavits@DESKTOP-XXXXXXX:~/projects$
```

5. Set the PYTHONPATH environment variable to point to the current working directory.
In order for Python to find modules correctly in linux based systems run the following command:
```
$ export PYTHONPATH=$HOME/projects
```
And in windows, this can be done through administrator powershell using the following command:
```
$env:PYTHONPATH = C:\Users\<youruser>\projects
```
6. Navigate into the projects root folder
```
$ cd output_validation
```
7. Install the necessary requirements
```
$ python -m pip install -r requirements.txt
```
8. (OPTIONAL) Investigate the default input files and the input subdirectory. There are three files:
indata.csv, outdata.csv and conf.txt. The program can run with either input or output file only. It
cannot run without the configuration file or when nothing other than the configuration file is passed.
The program takes arguments as command line parameters, -i for input, -o for output and -c for the
configuration file. All of these parameters are expected to be paths to the desired files.
9. Run the code with default test data and configuration
```
$ python Validator.py -i input/indata.csv -o input/outdata.csv -c input/conf.txt
```


That's it on running the program with custom input. Additionally, there are tests that can be run
using the pytest framework. For simply running the test, run
```
$ pytest -vv tests/
```
For running all tests with code coverage, run
```
$ coverage run --source . -m pytest -vv tests/ && coverage report -m
```

Happy testing.

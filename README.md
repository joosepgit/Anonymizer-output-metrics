# Anonymizer-output-metrics
This project acts as a separate software component that can be integrated into larger anonymization tools. The main purpose is to measure the quality of anonymization in terms of analyzing the remaining risks and changes in the output dataset. Some calculations rely on comparing the raw input dataset to the presumably anonymized output dataset. The metrics implemented assume that the anonymization has been performed using hierarchy based generalization techniques and at least either k-anonymization or l-diversity has been enforced as the main privacy model. It can be used with either the input or the output dataset, both are not assumed for the software to work. However as some operations rely on comparison, results may be much less meaningful using only one dataset.

The project was created as a practical part of my bachelor's thesis and is therefore publicly available for use under the MIT license. Further development is encouraged!

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

# LICENSE

Copyright 2022 Joosep Tavits

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# swatplus-calibration-test-suite
 This repository hosts code that aims to check the parameters that are sensitive when changed directly in their parameter files or calibration.cal file and whether the results are similar in both cases.

## For users
There have been cases where parameter change does not affect the model in any way such that one may spend time trying to change parameters that are not sensitive. In some cases, a parameter might be sensitive when changed in the original parameter file but not sensitive when changed in calibration.cal. This software will produce a report on what works and what does not in your version of the SWAT+ executable.

## To install
You will need to install a python package `cjfx` using this.
```
pip install cjfx
```

If you are on linux, you might need to replace `pip` with `pip3`. In addition, make sure you are using a linux version of the SWAT+ executable. Feel free to submit a pull request if you want to contribute. In that case, please, check our GitHub documentation at [swat-model.github.io](https://swat-model.github.io/collaborating/).

## Bug reports
If you notice a bug, please open a new issue and we will work on it.

## Versions
Version 0.1.0 - September 2023  

## Authors
- [Celray James CHAWANDA](https://celray.chawanda.com)

## License
This project is licensed under the MIT License. See also the [LICENSE](/LICENSE) file.

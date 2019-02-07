# Fetching speeches from Babel

This repository contains a CLI to retrieve speech data from Babel API.

## Requirements

* Python3
* Latest `pip` installed

## Install

```
sudo pip install pipenv # Install pipenv on your system
pipenv install # Install all requirements on a virtual environment
pipenv shell # Enter into the virtualenv created before
```

## Usage

```
speeches.py [OPTIONS] INITIAL_DATE END_DATE

Options:
  -s, --stage TEXT  Initials from speech stage. For example, PE to 'Pequeno
                    Expediente'
  --help            Show this message and exit.
```

* `INITIAL_DATE` and `END_DATE` must be on `yyyy-mm-dd` format.

After retrieve and process all speech data in the informed time, this scripts will create a csv called `speeches.csv`.
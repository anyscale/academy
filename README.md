# Anyscale Academy - Ray Tutorials

© 2019-2020, Anyscale. All Rights Reserved

Welcome to the [Anyscale Academy](https://anyscale.com/academy) tutorials on [Ray](https://ray.io), the system for scaling your applications from a laptop to a cluster.

> **Note:** This is an early release of these tutorials. Please report any issues 

## Setup

### Prerequisite Software

The following must be installed on your machine:

* Python 3.6 to 3.8 (3.8 recommended)
    * The version of Python that comes with your operating system is probably too old. Try `python --version` to see what you have.
* Pip (recent version)

#### Using Anaconda

We recommend using [Anaconda](https://www.anaconda.com/), especially if you do lots of Python development and you need to define different environments for different projects. However, Anaconda isn't required.

To install Anaconda, follow the instructions [here](https://www.anaconda.com/distribution/).
Then run the following Pip command to install the other dependencies, including Ray:

```
conda env create -f environment.yml
```

This creates an environment with the name `anyscale-academy`. Use the following command to activate it:

```
conda activate anyscale-academy
```

#### Using Pip

If you don't use Anaconda, first install a version of Python 3.6 to 3.8 (3.8 recommended). Instructions are at [python.org](https://www.python.org/downloads/). 

Then install `pip` using the instructions at [pip.pypa.io](https://pip.pypa.io/en/stable/installing/).


Now you can run the following `pip` command to install the rest of the libraries required for these tutorials, including Ray:

```
pip install -r requirements.txt
```

## Launching the Tutorials

The previous steps installed [Jupyter Lab](https://jupyterlab.readthedocs.io/en/stable/), the notebook-based environment we'll use for all the lessons. To start, make sure you are in the project root directory (i.e., the same directory as this README) and run the following command:

```
jupyter lab
```

It should automatically open a browser window with the lab environment, but if not, the console output will show the URL you should use.

## Tutorial Modules

The rest of this information can also be found in the [Overview](./Overview.ipynb) notebook. 

This directory contains files for setting up your environment (`README.md` - this file, `environment.yml`, and `requirements.txt`), which were discussed above, and the Apache license file (`LICENSE`).

The `util` directory contains library code used in the notebooks and the `images` directory contains images used in the notebooks.

Each tutorial _module_ is contained in a dedicated directory. Each  [Jupyter](https://jupyterlab.readthedocs.io/en/stable/) notebook in a module is a _lesson_. The notebooks follow the naming convention `NN-name.ipynb`, where `NN` is a number that indicates the ordering of lessons. 

> **Note:** If two or more notebooks have the same `NN` number, it indicates they can be studied an arbitrary order.

Let's discuss the modules. in this project, organized in subdirectories. 

### Ray Core

Directory: `ray-core`

This is the place to start. This module introduces you to Ray, why it was created, what problems it solves, how to use it, and how it works behind the scenes.

Once you've completed the Ray core material, you can explore the rest of the modules in any order.

### Ray RLlib

Directory: `ray-rllib`

_Ray RLlib_ is Ray's system for _reinforcement learning_. This module begins with a "crash course" in RL concepts. It then explores several of the commonly-used algorithms and approaches for different applications.

### Ray Tune and Ray SGD

Directory: `ray-tune`

_Ray Tune_ is Ray's system for _hyperparameter tuning_. This module starts with an explanation of what hyperparameter tuning is for and the performances challenges doing it for many applications. Then the module explores how to use _Tune_, how it integrates with several popular ML frameworks, and the algorithms supported in _Tune_. The new _Ray SGD_ module is also covered.

### Ray Serve

Directory: `ray-serve`

_Ray Serve_ is Ray's system for scalable _model serving_, with capabilities that also make it suitable for other web server applications. This module starts with an explanation of what's required in model serving, followed by a tour of the API with examples.


## Troubleshooting

When you first start Ray in the very first lesson (i.e., use `ray.init()`), you may run into a few issues:

1. If you get an error like `... INFO services.py:... -- Failed to connect to the redis server, retrying.`, it probably means you are running a VPN on your machine. [At this time](https://github.com/ray-project/ray/issues/6573), you can't use `ray.init()` with a VPN running. You'll have to stop your VPN for now.

2. If `ray.init()` worked (for example, you see a message like _View the Ray dashboard at localhost:8265_) and you're using a Mac, you may get several annoying dialogs asking you if you want to allow incoming connections for Python and/or Redis. Click "Accept" for each one and they shouldn't appear again during this tutorial. MacOS is trying to verify if these executables have been properly signed. Ray uses Redis. If you installed Python using Anaconda or other mechanism, then it probably isn't properly signed from the point of view of MacOS. To permanently fix this problem, [see this StackExchange post](https://apple.stackexchange.com/questions/3271/how-to-get-rid-of-firewall-accept-incoming-connections-dialog). 
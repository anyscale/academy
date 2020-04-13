# Anyscale Academy - Tutorials on Ray and Ray-based Libraries

© 2018-2020, Anyscale. All Rights Reserved

Welcome to the [Anyscale Academy](https://anyscale.com/academy) tutorials on [Ray](https://ray.io), the system for scaling your applications from a laptop to a cluster.

This README tells you how to set up the tutorials and it provides a quick overview of its contents.

> **Tips:**
>
> 1. This is an early release of these tutorials. Please report any issues:
>    * [GitHub issues](https://github.com/anyscale/academy/issues)
>    * The [#tutorial channel](https://ray-distributed.slack.com/archives/C011ML23W5B) on the [Ray Slack](https://ray-distributed.slack.com)
>    * [Email](mailto:academy@anyscale.com)
> 2. If you are attending a live tutorial event, please follow the setup instructions well in advance, as some of the downloads and installation processes can take a while.
> 3. There is a Troubleshooting section at the end of this README.

## Setup

> **WARNING:** Ray does not currently run on Windows (we're close...). You have two alternative options:
>
> 1. Click the _run on Colab_ links shown below in the descriptions of each tutorial. However, some of the graphics used in the notebooks may not work.
> 2. Read the notebooks as rendered by GitHub: https://github.com/anyscale/academy

> **Tip:** If you use Colab, make sure you download your notebooks to save any changes.

If you aren't installing the tutorials and the Python dependencies, skip ahead to _Tutorial Modules_.

If you are using MacOS or Linux, follow these instructions. Note that the setup commands can take a while to finish.

Clone the [Academy GitHub repo](https://github.com/anyscale/academy) or [download the latest release](https://github.com/anyscale/academy/releases).

#### Using Anaconda

We recommend using [Anaconda](https://www.anaconda.com/), especially if you do lots of Python development and you need to define different environments for different projects. However, Anaconda isn't required.

To install Anaconda, follow the instructions [here](https://www.anaconda.com/distribution/). If you already have Anaconda installed, consider running `conda upgrade --all`.

Then run the following commands in the root directory of this project. First,  use `conda` to install the other dependencies, including Ray. Then "activate" the newly-created environment, named `anyscale-academy`. Finally, use the `jupyter` commands to set up the graphing library extensions in Jupyter Lab that we'll use. The last command just lists the extensions.

```
conda env create -f environment.yml
conda activate anyscale-academy
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter labextension install @pyviz/jupyterlab_pyviz
jupyter labextension install @bokeh/jupyter_bokeh
jupyter labextension list
```

Note that Python 3.7 is used. While Ray supports Python 3.8, some dependencies used in `RLlib` (the Ray reinforcement library) are not yet supported for 3.8.

You can delete the environment later with the following command:

```
conda env remove --name anyscale-academy
```

You are ready to go!

#### Using Pip

If you don't use Anaconda, you'll have to install prerequisites first:

* Python 3.6 or 3.7. While Ray supports Python 3.8, some dependencies used in `RLlib` (the Ray reinforcement library) are not yet supported for 3.8.
    * The version of Python that comes with your operating system is probably too old. Try `python --version` to see what you have.
    * Installation instructions are at [python.org](https://www.python.org/downloads/).
* Pip (a recent version - consider upgrading if it's not the latest version)
	* Installation instructions are at [pip.pypa.io](https://pip.pypa.io/en/stable/installing/).

Now run the following commands in the root directory of this project to complete the setup. First, run a `pip` command to install the rest of the libraries required for these tutorials, including Ray. Then, use the `jupyter` commands to set up the graphing library extensions in Jupyter Lab that we'll use. The last command just lists the extensions.

```
pip install -r requirements.txt
jupyter labextension install @jupyter-widgets/jupyterlab-manager
jupyter labextension install @pyviz/jupyterlab_pyviz
jupyter labextension install @bokeh/jupyter_bokeh
jupyter labextension list
```

You are ready to go!

## Launching the Tutorials

The previous steps installed [Jupyter Lab](https://jupyterlab.readthedocs.io/en/stable/), the notebook-based environment we'll use for all the lessons. To start, make sure you are in the project root directory and run the following command:

```
jupyter lab
```

It should automatically open a browser window with the lab environment, but if not, the console output will show the URL you should use.

> **Tips:**
>
> 1. If you get an error that `jupyter` can't be found and you are using the Anaconda setup, make sure you activated the `anyscale-academy` environment, as shown above.
> 2. If you accidentally close the lab browser window, just use the same URL to reopen it.

## Tutorial Modules

The rest of this information can also be found in the [Overview](./Overview.ipynb) notebook.

This directory contains files for setting up your environment (`README.md` - this file, `environment.yml`, and `requirements.txt`), which were discussed above, and the Apache license file (`LICENSE`).

The `util` directory contains library code used in the notebooks and the `images` directory contains images used in the notebooks.

Each tutorial _module_ is contained in a dedicated directory. Each  [Jupyter](https://jupyterlab.readthedocs.io/en/stable/) notebook in a module is a _lesson_. The notebooks follow the naming convention `NN-name.ipynb`, where `NN` is a number that indicates the ordering of lessons.

> **Note:** If two or more notebooks have the same `NN` number, it indicates they can be studied in arbitrary order.

Let's discuss the modules in this project, organized in subdirectories.

### Ray Core

Directory: `ray-core`

This is the place to start. This module introduces you to Ray, why it was created, what problems it solves, how to use it, and how it works behind the scenes.

| Lesson | Open in Colab | Description |
| :----- | :------------ | :---------- |
| [01 Introduction](ray-core/01-Introduction.ipynb) | <a href="https://colab.research.google.com/github/anyscale/academy/blob/master/ray-core/01-Introduction.ipynb" target="_01-Introduction"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Ray Tutorial - 01-Introduction"/></a> | Start in this notebook, which introduces Ray. |
| [02 Task Parallelism - Part1](ray-core/02-TaskParallelism-Part1.ipynb) | <a href="https://colab.research.google.com/github/anyscale/academy/blob/master/ray-core/02-TaskParallelism-Part1.ipynb" target="_02-TaskParallelism-Part1"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Ray Tutorial - 02-TaskParallelism-Part1"/></a> | Part 1 of the introduction to several of the Ray API calls and how to use them to turn synchronous python _functions_ into asynchronous Ray _tasks_. |
| [03 Task Parallelism - Part2](ray-core/03-TaskParallelism-Part2.ipynb) | <a href="https://colab.research.google.com/github/anyscale/academy/blob/master/ray-core/03-TaskParallelism-Part2.ipynb" target="_03-TaskParallelism-Part2"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Ray Tutorial - 03-TaskParallelism-Part2"/></a> | Part 2 of the exploration of Ray _tasks_. |
| [04 Distributed State with Actors](ray-core/04-DistributedStateWithActors.ipynb) | <a href="https://colab.research.google.com/github/anyscale/academy/blob/master/ray-core/04-DistributedStateWithActors.ipynb" target="_04-DistributedStateWithActors"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Ray Tutorial - 04-DistributedStateWithActors"/></a> | Ray _actors_ are the asynchronous analog of Python classes, used to extend the concept of a _task_ to support management of distributed state. |
| [05 Exploring Ray API Calls](ray-core/05-ExploringRayAPICalls.ipynb) | <a href="https://colab.research.google.com/github/anyscale/academy/blob/master/ray-core/05-ExploringRayAPICalls.ipynb" target="_05-ExploringRayAPICalls"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Ray Tutorial - 05-ExploringRayAPICalls"/></a> | The Ray API has other API calls for more advanced scenarios, which are surveyed in this optional module. We'll also look at options you can pass to the API calls we've already learned. |
| [06-Recap Tips and Tricks](ray-core/06-RecapAndTipsTricks.ipynb) | <a href="https://colab.research.google.com/github/anyscale/academy/blob/master/ray-core/06-RecapAndTipsTricks.ipynb" target="_06-RecapAndTipsTricks"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Ray Tutorial - 06-RecapAndTipsTricks"/></a> | The final lesson recaps what we've learned and summarizes the tips and tricks we've covered, plus adds a few more. |

Once you've completed the Ray core material, you can explore the rest of the modules in any order.

### Ray RLlib

Directory: `ray-rllib`

_Ray RLlib_ is Ray's system for _reinforcement learning_. This module begins with a "crash course" in RL concepts. It then explores several of the commonly-used algorithms and approaches for different applications.

This module will be released soon.

### Ray Tune and Ray SGD

Directory: `ray-tune`

_Ray Tune_ is Ray's system for _hyperparameter tuning_. This module starts with an explanation of what hyperparameter tuning is for and the performances challenges doing it for many applications. Then the module explores how to use _Tune_, how it integrates with several popular ML frameworks, and the algorithms supported in _Tune_. The new _Ray SGD_ module is also covered.

This module will be released soon.

### Ray Serve

Directory: `ray-serve`

_Ray Serve_ is Ray's system for scalable _model serving_, with capabilities that also make it suitable for other web server applications. This module starts with an explanation of what's required in model serving, followed by a tour of the API with examples.

This module will be released soon.

## Notes

* We're currently using Python 3.7, because a dependency of `RLlib`, `atari-py`, doesn't have a wheel available for Python 3.8.

## Troubleshooting

When you first start Ray in a notebook (i.e., use `ray.init()`), you may run into a few issues:

1. If you get an error like `... INFO services.py:... -- Failed to connect to the redis server, retrying.`, it probably means you are running a VPN on your machine. [At this time](https://github.com/ray-project/ray/issues/6573), you can't use `ray.init()` with a VPN running. You'll have to stop your VPN to run `ray.init()`, then once it finishes, you can restart your VPN.

2. If `ray.init()` worked (for example, you see a message like _View the Ray dashboard at localhost:8265_) and you're using a Mac, you may get several annoying dialogs asking you if you want to allow incoming connections for Python and/or Redis (used internally by Ray). Click "Accept" for each one and they shouldn't appear again during this tutorial. For security reasons, MacOS is complaining that it can't verify these executables have been properly signed. If you installed Python using Anaconda or other mechanism, then it probably isn't properly signed from the point of view of MacOS. To permanently fix this problem, [see this StackExchange post](https://apple.stackexchange.com/questions/3271/how-to-get-rid-of-firewall-accept-incoming-connections-dialog).
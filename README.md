# Anyscale Academy - Tutorials on Ray and Ray-based Libraries

© 2018-2020, Anyscale. All Rights Reserved

Welcome to the [Anyscale Academy](https://anyscale.com/academy) tutorials on [Ray](https://ray.io), the system for scaling your applications from a laptop to a cluster.

This README tells you how to set up the tutorials, it provides a quick overview of its contents, and it recommends which tutorials to go through depending on your interests.

> **Tips:**
>
> 1. If you just want to read the tutorials, GitHub renders notebooks.
> 2. This is an early release of these tutorials. Please report any issues:
>    * [GitHub issues](https://github.com/anyscale/academy/issues)
>    * The [#tutorial channel](https://ray-distributed.slack.com/archives/C011ML23W5B) on the [Ray Slack](https://ray-distributed.slack.com)
>    * [Email](mailto:academy@anyscale.com)
> 3. If you are attending a live tutorial event, please follow the setup instructions well in advance, as some of the downloads and installation processes can take a while.
> 4. There is a Troubleshooting section at the end of this README.

## Setup

> **WARNING:** Ray does not currently run on Windows (we're close...). We're working on a hosted option, but for now, you have two alternative options:
>
> 1. Use a virtual machine environment like VMWare with Linux, a cloud instance in AWS, etc., or a local Docker image.
> 2. Read the notebooks as rendered by GitHub: https://github.com/anyscale/academy

> **Tip:** If you use option #1, make sure you download your notebooks to save any changes. Most local options, like VMWare and Docker allow you to mount a local directory, which is where you could keep the tutorial materials.

If you aren't installing the tutorials and the Python dependencies, skip ahead to [**Tutorial Descriptions**](#tutorial-descriptions).

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

> **Tip:** If you get an error that `jupyter` can't be found and you are using the Anaconda setup, make sure you activated the `anyscale-academy` environment, as shown above.

The rest of the information in this README can also be found in the [Overview](./Overview.ipynb) notebook.

## Which Tutorials Are Right for Me?

Here is a recommended reading list, based on your interests:

| You Are... | Best Tutorials |
| :--------- | :------------- |
| A developer who is new to Ray | First, [_Ray Crash Course_](#user-content-ray-crash-course), then [_Advanced Ray_](#user-content-advanced-ray) |
| A developer who is experienced with Ray | [_Advanced Ray_](#user-content-advanced-ray) |
| A developer or data scientist interested in Reinforcement Learning | [_Ray RLlib_](#user-content-ray-rllib) |
| A developer or data scientist interested in Hyperparameter Tuning  | [_Ray Tune_](#user-content-ray-tune) |
| A developer or data scientist interested in accelerated model training with PyTorch  | [_Ray SGD_](#user-content-ray-sgd) |
| A developer or data scientist interested in model serving | [_Ray Serve_](#user-content-ray-serve) |

See also the [_Troubleshooting, Tips, and Tricks notebook_](reference/Troubleshooting-Tips-Tricks.ipynb). For the details of the Ray API and the ML libraries, see the [Ray Docs](https://docs.ray.io/en/latest/).

> **Note:** Older Ray tutorials can be found in the [this repo](https://github.com/ray-project/tutorial). They cover topics not yet covered by the Anyscale Academy.

## Tutorial Descriptions

Let's explore each tutorial.

### This Directory

First, the root directory contains files for setting up your environment (`README.md` - this file, `environment.yml`, and `requirements.txt`), as discussed previoiusly, and the Apache license file (`LICENSE`). The `util` and the `images` directories contain library code and images used in the notebooks, respectively. (Each tutorial directory discussed below may also have supporting code files.) There is also a `reference` directory with notebooks and other materials you might find useful.

Each tutorial is contained in a dedicated directory. Each [Jupyter](https://jupyterlab.readthedocs.io/en/stable/) notebook is a _lesson_. The notebooks follow the naming convention `NN-name.ipynb`, where `NN` is a number that indicates the ordering of the lessons.

> **Note:** If two or more notebooks have the same `NN` number, it indicates they can be studied in arbitrary order.

The tutorials are organized in subdirectories.

### Reference

Directory: `reference`

The notebooks here provide reference material, like general tips and tricks, how to get help, and troubleshooting issues.

| Lesson (Notebook) | Description |
| :---------------- | :---------- |
| [Troubleshooting, Tips, and Tricks](reference/Troubleshooting-Tips-Tricks.ipynb) | How to troubleshoot common problems and other useful tips and tricks. |

### Ray Crash Course

| About | Details |
| :----- | :------------ |
| _Directory:_ | `ray-crash-course` |
| _Audience:_ | You are a developer who wants a fast introduction to the core Ray API. Experienced developers should go to [_Advanced Ray_](#user-content-advanced-ray). Data scientists may wish to skip to [_Ray RLlib_](#user-content-ray-rllib), [_Ray Tune_](#user-content-ray-tune), [_Ray SGD_](#user-content-ray-sgd), or [_Ray Serve_](#user-content-ray-serve). |


This is the place to start if you are new to Ray and you plan to use it to scale Python applications to a cluster. Data scientists working with Ray-based toolkits, like _RLlib_, don't need this knowledge to get started.

The _crash course_ is intended to focus on learning the core API as quickly as possible, but using nontrivial examples. In contrast, the [_Advanced Ray_](#user-content-advanced-ray) tutorial begins with an explanation of why Ray was created, what problems it solves, and then dives into more advanced API usage, profiling and debugging applications, and how Ray works behind the scenes.

| #  | Lesson | Description |
| :- | :----- | :---------- |
| 00 | [Overview](ray-crash-course/00-Ray-Crash-Course-Overview.ipynb) | A _table of contents_ for this tutorial. |
| 01 | [Ray Crash Course: Tasks](ray-crash-course/01-Ray-Crash-Course-Tasks.ipynb) | Understanding how Ray converts normal Python functions into distributed _stateless tasks_. |
| 02 | [Ray Crash Course: Actors](ray-crash-course/02-Ray-Crash-Course-Actors.ipynb) | Understanding how Ray converts normal Python classes into distributed, _stateful actors_. |
| 03 | [Adopting Ray](03-Adopting-Ray.ipynb)             | Ray drop-in replacements for common parallelism APIs, about the Ray community, etc. |
| 04 | [Running Ray Clusters](04-Running-Ray-Clusters.ipynb) | How to run Ray in a clustered environment, submit your work to it, and integrate with your local development process. |

Once you've completed this tutorial, go through [_Advanced Ray_](#user-content-advanced-ray) or explore one of the ML-related library tutorials, in any order.

### Advanced Ray

Directory: `advanced-ray`

Go through the [_Crash Course_](#ray-crash-course) first if you are new to Ray. Then return to this tutorial, which begins with an explanation of why Ray was created, what problems it solves, and then dives into more advanced API usage, profiling and debugging applications, and how Ray works behind the scenes.

This is the place to start. This tutorial introduces you to Ray, why it was created, what problems it solves, how to use it, and how it works behind the scenes.

| #  | Lesson | Description |
| :- | :----- | :---------- |
| 00 | [Overview](advanced-ray/00-Overview.ipynb) | A _table of contents_ for this tutorial. |
| 01 | [Why Ray?](advanced-ray/01-Why-Ray.ipynb) | Start in this notebook if you want an explanation of the origin and motivations for Ray. |
| 02 | [Ray Tasks Revisited](advanced-ray/02-Ray-Tasks-Revisited.ipynb) | More exploration of `ray.wait()` usage patterns, task dependencies and their management, task profiling techniques, and task scheduling. |
| 03 | [Ray Actors Revisited](advanced-ray/03-Ray-Actors-Revisited.ipynb) | A more in-depth look at Actor scheduling under the hood and profiling performance using the _Ray Dashboard_. |
| 04 | [Exploring Ray API Calls](advanced-ray/04-Exploring-Ray-API-Calls.ipynb) | The Ray API has other API calls for more advanced scenarios, which are surveyed in this optional lesson. Options you can pass to the API calls already learned are explored. |

Once you've completed the Ray core material, you can explore the rest of the tutorials in any order.

### Ray RLlib

Directory: `ray-rllib`

_Ray RLlib_ is Ray's system for _reinforcement learning_. This tutorial begins with a "crash course" in RL concepts. It then explores several of the commonly-used algorithms and approaches for different applications.

Here are the lessons. Note that the `04a-04c` lessons can be studied in any order.

| #   | Lesson | Description |
| :-- | :----- | :---------- |
| 00 | Ray RLlib Overview](rllib/00-Ray-RLlib-Overview.iypnb) | Overview of this tutorial. |
| 01 | Introduction to Reinforcement Learning](rllib/01-Introduction-to-Reinforcement-Learning.ipynb) | A quick introduction to the concepts of reinforcement learning, adapted from [`rllib_exercises`](https://github.com/ray-project/tutorial/blob/master/rllib_exercises/rllib_colab.ipynb) by @edoakes. You can skim or skip this lesson if you already understand RL concepts. |
| 02 | About RLlib](rllib/02-About-RLlib.ipynb) | An introduction to RLlib, its goals and the capabilities it provides. |
| 03 | Application Cart Pole](rllib/03-Application-Cart-Pole.ipynb) | The best starting place for learning how to use RL, in this case to train a moving car to balance a vertical pole. Based on the `CartPole-v0` environment from OpenAI Gym, combined with RLlib. |
| 04a | Application Mountain Car](rllib/04a-Application-Mountain-Car.ipynb) | Based on the `MountainCar-v0` environment from OpenAI Gym. |
| 04b | Application Taxi](rllib/04b-Application-Taxi.ipynb) | Based on the `Taxi-v3` environment from OpenAI Gym. |
| 04c | Application Frozen Lake](rllib/04c-Application-Frozen-Lake.ipynb) | Based on the `FrozenLake-v0` environment from OpenAI Gym. |

### Ray Tune

Directory: `ray-tune`

_Ray Tune_ is Ray's system for _hyperparameter tuning_. This tutorial starts with an explanation of what hyperparameter tuning is for and the performances challenges doing it for many applications. Then the tutorial explores how to use _Tune_, how it integrates with several popular ML frameworks, and the algorithms supported in _Tune_.

This tutorial will be released soon.

### Ray SGD

Directory: `ray-sgd`

_Ray SGD_ is a tool to more easily exploit a cluster to perform training with _Stochastic Gradient Descent_ using PyTorch (TensorFlow support forthcoming).

This tutorial will be released soon.

### Ray Serve

Directory: `ray-serve`

_Ray Serve_ is Ray's system for scalable _model serving_, with capabilities that also make it suitable for other web server applications. This tutorial starts with an explanation of what's required in model serving, followed by a tour of the API with examples.

This tutorial will be released soon.

## Notes

* We're currently using Python 3.7, because a dependency of `RLlib`, `atari-py`, doesn't have a wheel available for Python 3.8.

## Troubleshooting

When you first start Ray in a notebook (i.e., use `ray.init()`), you may run into a few issues:

### Ray.init() Fails

If you get an error like `... INFO services.py:... -- Failed to connect to the redis server, retrying.`, it probably means you are running a VPN on your machine. [At this time](https://github.com/ray-project/ray/issues/6573), you can't use `ray.init()` with a VPN running. You'll have to stop your VPN to run `ray.init()`, then once it finishes, you can restart your VPN.

### MacOS - Prompts to Allow Python, etc.

If `ray.init()` worked (for example, you see a message like _View the Ray dashboard at localhost:8265_) and you're using a Mac, you may get several annoying dialogs asking you if you want to allow incoming connections for Python and/or Redis (used internally by Ray). Click "Accept" for each one and they shouldn't appear again during this tutorial. For security reasons, MacOS is complaining that it can't verify these executables have been properly signed. If you installed Python using Anaconda or other mechanism, then it probably isn't properly signed from the point of view of MacOS. To permanently fix this problem, [see this StackExchange post](https://apple.stackexchange.com/questions/3271/how-to-get-rid-of-firewall-accept-incoming-connections-dialog).

### Profiling Actors with Ray Dashboard - Bug

3. A lesson in [_Advanced Ray_](#user-content-advanced-ray) shows you how to profile actors using the Ray Dashboard, but there is currently a bug in Ray 0.8.4 that prevents Ray from generating valid data. [There is the one line fix](https://github.com/ray-project/ray/pull/8013/files) you can do to your Ray installation.

You need to edit your local copy of `dashboard.py`, `.../lib/python3.X/site-packages/ray/dashboard/dashboard.py`. If you don't know where Ray is installed, start iPython and enter `sys.path`.

Change line 332,

```python
return aiohttp.web.json_response(self.is_dev, profiling_info)
```

to this (where the original line is commented out, in case you change your mind later...):

```python
return aiohttp.web.json_response(profiling_info)
# return aiohttp.web.json_response(self.is_dev, profiling_info)
```

If you make this change after starting Jupyter Lab, you'll need to restart.

This bug is fixed in the forthcoming Ray 0.8.5 release.

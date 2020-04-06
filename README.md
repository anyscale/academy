# Ray Tutorials

The second-generation tutorials for the [Ray Project](https://ray.io) ([GitHub](https://github.com/ray-project)).

## Setup

### Prerequisite Software

The following must be installed on your machine:

* Python 3.8
* Pip (recent version)

We recommend using [Anaconda](https://www.anaconda.com/), especially if you do lots of Python development and you need to define different environments for different projects.

Then run the following Pip command to install the other dependencies, including Ray:

```
pip install -r environment.yml
```

## Tutorial Modules

There are many modules in this project, organized in subdirectories. Lessons are provided as [Jupyter Lab](https://jupyterlab.readthedocs.io/en/stable/) notebooks. A number is embedded in the name to indicate the sequence you should follow when going through the lessons. In the cases where some notebooks can be studied in an arbitrary order, they are indicated with a letter, such as `A`. For example, `algorithm04A.ipynb` and `algorithm04B.ipynb` would indicate that you can go through either or both of these notebooks in any order, after going through the first through third lessons.

Here are the modules.

### Ray Core

Directory: `ray-core`

This is the place to start. This module introduces you to Ray, why it was created, what problems it solves, how to use it, and how it works behind the scenes.

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
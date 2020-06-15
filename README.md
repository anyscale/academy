# Anyscale Academy - Tutorials on Ray and Ray-based Libraries

© 2018-2020, Anyscale. All Rights Reserved

Welcome to the [Anyscale Academy](https://anyscale.com/academy) tutorials on [Ray](https://ray.io), the system for scaling your applications from a laptop to a cluster.

This README tells you how to set up the tutorials, it provides a quick overview of its contents, and it recommends which tutorials to go through depending on your interests.

> **Tips:**
>
> 1. Anyscale is developing a free, hosted version of these tutorials. [Contact us](mailto:academy@anyscale.com) for more information.
> 2. This is an early release of these tutorials. Please report any issues:
>    * [GitHub issues](https://github.com/anyscale/academy/issues)
>    * The [#tutorial channel](https://ray-distributed.slack.com/archives/C011ML23W5B) on the [Ray Slack](https://ray-distributed.slack.com)
>    * [Email](mailto:academy@anyscale.com)
> 3. If you are attending a live tutorial event, please follow the setup instructions provided well in advance.
> 4. There is a Troubleshooting section at the end of this README and also in this [Troubleshooting, Tips, and Tricks](reference/Troubleshooting-Tips-Tricks.ipynb) notebook.

Read one of the following setup sections, as appropriate, then jump to [**Launching the Tutorials**](#user-content-launching-the-tutorials).

## Setup for Anyscale Academy Hosted Sessions

There is nothing you need to setup, as the hosted environment will provide everything.

However, consider cloning or downloading a release of the tutorial notebooks and supporting software from the [Academy repo](https://github.com/anyscale/academy), so you have a local copy of everything. The `README` provides instruction for local setup, if desired.

> **Tip:** Make sure you download the notebooks you modified during the session to save those changes.

## Setup for a Local Machine

> **WARNING:** Ray does not currently run on Windows (we're close...). [Contact Anyscale](mailto:academy@anyscale.com) for a free hosted option.

If you are using MacOS or Linux, follow these instructions. Note that the setup commands can take a while to finish.

Clone the [Academy GitHub repo](https://github.com/anyscale/academy) or [download the latest release](https://github.com/anyscale/academy/releases).

Now install the dependencies using either [Anaconda](https://www.anaconda.com/) or `pip` in your Python environment. We recommend using Anaconda.

### Using Anaconda

If you need to install Anaconda, follow the instructions [here](https://www.anaconda.com/distribution/). If you already have Anaconda installed, consider running `conda upgrade --all`.

Run the following commands in the root directory of this project. First,  use `conda` to install the other dependencies, including Ray. Then activate the newly-created environment, named `anyscale-academy`. Finally, run a provided script to install a graphing library extension in Jupyter Lab and perform other tasks.

```shell
conda env create -f environment.yml
conda activate anyscale-academy
tools/fix-jupyter.sh
```

Note that Python 3.7 is used. While Ray supports Python 3.8, some dependencies used in `RLlib` (the Ray reinforcement library) are not yet supported for 3.8.

You can delete the environment later with the following command:

```
conda env remove --name anyscale-academy
```

### Using Pip

If you don't use Anaconda, you'll have to install these prerequisites first:

* Python 3.6 or 3.7: While Ray supports Python 3.8, some dependencies used in `RLlib` (the Ray reinforcement library) and other dependencies are not yet supported for 3.8.
    * The version of Python that comes with your operating system is probably too old. Try `python --version` to see what you have.
    * Installation instructions are at [python.org](https://www.python.org/downloads/).
* Pip: A recent version - consider upgrading if it's not the latest version.
	* Installation instructions are at [pip.pypa.io](https://pip.pypa.io/en/stable/installing/).
* Node.js: Required for some of the Jupyter Lab graphics extensions we use.
	* Installation instructions are [here](https://nodejs.org/en/).

Now run the following commands in the root directory of this project to complete the setup. First, run a `pip` command to install the rest of the libraries required for these tutorials, including Ray. Then, run a provided script to install a graphing library extension in Jupyter Lab and perform other tasks.

```shell
pip install -r requirements.txt
tools/fix-jupyter.sh
```

## Final Notes for Local Installation

The lessons will start a local Ray "cluster" (one node) on your machine. When you are finished with the tutorials, run the following command to shut down Ray:

```shell
ray stop
```

## Launching the Tutorials

The previous steps installed [Jupyter Lab](https://jupyterlab.readthedocs.io/en/stable/), the notebook-based environment we'll use for all the lessons. To start run the following command in the project root directory:

```shell
jupyter lab
```

It should automatically open a browser window with the lab environment, but if not, the console output will show the URL you should use.

> **Tip:** If you get an error that `jupyter` can't be found and you are using the Anaconda setup, make sure you activated the `anyscale-academy` environment, as shown above.

## Which Tutorials Are Right for Me?

Here is a recommended reading list, based on your interests:

| You Are... | Best Tutorials |
| :--------- | :------------- |
| A developer who is new to Ray | First, [_Ray Crash Course_](ray-crash-course/00-Overview-Ray-Crash-Course.ipynb), then [_Advanced Ray_](advanced-ray/00-Overview-Advanced-Ray.ipynb) |
| A developer who is experienced with Ray | [_Advanced Ray_](advanced-ray/00-Overview-Advanced-Ray.ipynb) (_alpha_ release) |
| A developer or data scientist interested in Reinforcement Learning | [_Ray RLlib_](rllib/00-Overview-Ray-RLlib.ipynb) |
| A developer or data scientist interested in Hyperparameter Tuning  | _Ray Tune_ (forthcoming) |
| A developer or data scientist interested in accelerated model training with PyTorch  | _Ray SGD_ (forthcoming) |
| A developer or data scientist interested in model serving | _Ray Serve_ (forthcoming) |

See also the [_Troubleshooting, Tips, and Tricks notebook_](reference/Troubleshooting-Tips-Tricks.ipynb). For the details of the Ray API and the ML libraries, see the [Ray Docs](https://docs.ray.io/en/latest/).

> **Note:** Older Ray tutorials can be found in the [this repo](https://github.com/ray-project/tutorial). They cover topics not yet covered by the Anyscale Academy.

### Tutorial Descriptions

See the [Overview notebook](Overview.ipynb) for detailed, up-to-date descriptions for each tutorial and the lessons it contains.

## Notes

* We use Python 3.7, because a dependency of `RLlib`, `atari-py`, doesn't have a wheel available for Python 3.8 at this time.

## Troubleshooting

When you first start Ray in a notebook through one of several means, you may run into a few issues:

### Ray.init() Fails - "Failed to Connect to Redis..."

Suppose you get an error like this:

```
... INFO services.py:... -- Failed to connect to the redis server, retrying.
```

It probably means you are running a VPN on your machine. [At this time](https://github.com/ray-project/ray/issues/6573), you can't use `ray.init()` with a VPN running. You'll have to stop your VPN to run `ray.init()`, then once it finishes, you can restart your VPN.

Suppose you successfully executed one of the notebook cells with this shell command: `!../tools/start-ray.sh`, but then when you execute `ray.init(adress='auto', ...)` you get the following error for some `IP` address and `PORT`:

```
ConnectionError: Error 61 connecting to IP:PORT. Connection refused.
```

If the output of `../tools/start-ray.sh` includes instructions for passing a Redis password, e.g., `redis_password='5241590000000000'`, add this argument to the `ray.init()` call and try again.

If that fails, it may be necessary to use a terminal to kill any old Redis processes that are running. You can start a terminal in Jupyter by clicking the "+" under the _Edit_ menu.

On MacOS and Linux systems, try the following commands, shown with some of the possible output:

```shell
$ ray stop
$ ray stop  # repeated

$ ps -ef | grep redis
501 36029     1   0  1:53PM ??         0:00.03 .../lib/python3.7/site-packages/ray/core/src/ray/thirdparty/redis/src/redis-server *:48044
501 36030     1   0  1:53PM ??         0:00.02 .../lib/python3.7/site-packages/ray/core/src/ray/thirdparty/redis/src/redis-server *:42902

$ kill 36029 36039

$ ray start --head
```

### tools/start-ray.sh or Other Shell Script Fails - "Multiple Ray Clusters Running..."

Several notebook cells run `bash` shell scripts, .e.g., to verify the Ray cluster is running, we use a cell like this:

|  |
|:-|
|`tools/start-ray.sh --check --verbose`|

Other cells run commands like `rllib rollout ...`

It's possible that some of these commands will fail with an error that multiple Ray clusters are running. You'll be asked to specify which one to use.

Please report this issue to academy@anyscale.com. We are trying to ensure this never happens. Tell us which notebook you were using when it happened.

Here's how to fix the issue if it does happen.

1. Run `ray stop` **several times** in a terminal window. You can start a terminal in Jupyter by clicking the "+" under the _Edit_ menu.
2. Run `ray start --head` in the terminal window to restart Ray.
2. Try rerunning the cell that ran the command that failed. It should now work without reporting the same error.

If it still throws the same error, then do these additional steps and try again:

1. Save your work in any other open notebooks.
2. Close all the other notebooks.
3. Shutdown their kernels using the Jupyter tab on the left-hand side that shows the
   running kernels.
4. Repeat the `ray stop` and `ray start --head` commands again.


### MacOS - Prompts to Allow Python, etc.

If `ray.init()` worked (for example, you see a message like _View the Ray dashboard at localhost:8265_) and you're using a Mac, you may get several annoying dialogs asking you if you want to allow incoming connections for Python and/or Redis (used internally by Ray). Click "Accept" for each one and they shouldn't appear again during this tutorial. For security reasons, MacOS is complaining that it can't verify these executables have been properly signed. If you installed Python using Anaconda or other mechanism, then it probably isn't properly signed from the point of view of MacOS. To permanently fix this problem, [see this StackExchange post](https://apple.stackexchange.com/questions/3271/how-to-get-rid-of-firewall-accept-incoming-connections-dialog).


# Anyscale Academy - Tutorials on Ray and Ray-based Libraries

© 2018-2021, Anyscale. All Rights Reserved

Welcome to the [Anyscale Academy](https://anyscale.com/academy) tutorials on [Ray](https://ray.io), the system for scaling your applications from a laptop to a cluster.

This README tells you how to set up the tutorials, decide which content is best for your interests, and find videos of previous Academy live events.

> **Tips:**
>
> 1. Anyscale is developing a free, hosted version of these tutorials. [Contact us](mailto:academy@anyscale.com) for more information.
> 2. Please report any issues or suggestions:
>    * [GitHub issues](https://github.com/anyscale/academy/issues)
>    * The [#tutorial channel](https://ray-distributed.slack.com/archives/C011ML23W5B) on the [Ray Slack](https://ray-distributed.slack.com) [Click here](https://forms.gle/9TSdDYUgxYs8SA9e8) to join.
>    * [Email](mailto:academy@anyscale.com)
> 3. If you are attending a live tutorial event, **please** follow the setup instructions provided in advance. It will take too long to do these instructions during the event.
> 4. For troubleshooting help, see the [Troubleshooting, Tips, and Tricks](reference/Troubleshooting-Tips-Tricks.ipynb) notebook.

## Dependencies

For a few of the examples here, you may need to add some additional dependencies:

  * `nodejs`
  * `holoviews`
  * `bokeh`

## Watch Sessions from Ray Summit 2021!

We had an amazing lineup of luminar keynote speakers and breakout sessions on the Ray ecosystem, third-party Ray libraries, and applications of Ray in the real world.


<a href="https://www.anyscale.com/ray-summit-2021"><img src="images/raysummit-horizontal-white-banner-full.png" alt="Ray Summit 2021"/></a>

For information about other online events, see [anyscale.com/events](https://anyscale.com/events).

## Videos of Previous Live Sessions

To see videos of live sessions covering most of this material, see the [Anyscale Academy](https://anyscale.com/academy/) page or visit the [Anyscale YouTube! channel](https://www.youtube.com/channel/UC7L1tZw52rtgmIB4fr_f40w/playlists).

## Tutorial Setup

Read the appropriate setup section that follows, then jump to [**Launching the Tutorials**](#user-content-launching-the-tutorials).

## Setup for Anyscale Academy Hosted Sessions

There is nothing you need to setup, as the hosted environment will provide everything.

However, consider cloning or downloading a release of the tutorial notebooks and supporting software from the [Academy repo](https://github.com/anyscale/academy), so you have a local copy of everything.

> **Tip:** If you modify any notebooks during the hosted session, make sure you download them to save those changes.

## Setup for a Local Machine

> **Note:** Ray support for Windows is new. See [these release notes](https://github.com/ray-project/ray/releases/tag/ray-0.8.7) for details.

Follow these instructions to use the tutorials. Note that some commands can take a while to finish.

Clone the [Academy GitHub repo](https://github.com/anyscale/academy) or [download the latest release](https://github.com/anyscale/academy/releases).

Now install the dependencies using either [Anaconda](https://www.anaconda.com/) or `pip` in your Python environment. We recommend using Anaconda.

### Which Python Version?

Python 3.7 is recommended. While Ray supports Python 3.6, there are known problem using _locales_ in that version and these tutorials. Specifically, the following code throws an error:

```python
import locale
locale.setlocale(locale.LC_ALL, locale.getlocale())
```

This tutorial doesn't manipulate _locales_ explicitly, but you may run into problems with your default locale.

While Ray supports Python 3.8, some dependencies used in `RLlib` (the Ray reinforcement library) are not yet supported for 3.8, at the time of this writing.

### Using Anaconda

If you need to install Anaconda, follow the instructions [here](https://www.anaconda.com/distribution/). If you already have Anaconda installed, consider running `conda upgrade --all`.

Run the following commands in the root directory of this project. First, use `conda` to install the other dependencies, including Ray. Then activate the newly-created environment, named `anyscale-academy`. Finally, run the provided `tools/fix-jupyter.sh` script to install a graphing library extension in Jupyter Lab and perform other tasks.

```shell
conda env create -f environment.yml
conda activate anyscale-academy
pip install typing-extensions --upgrade
tools/fix-jupyter.sh
```

If you are using Windows, see the [**Fixing Jupyter Lab on Windows**](#user-content-fixing-jupyter-lab-on-windows) below for an alternative to using `tools/fix-jupyter.sh`.

Note that Python 3.8.is used. Ignore the similar-looking `environment-docker.yml` file. It is used to build Docker images.

You can delete the environment later with the following command:

```
conda env remove --name anyscale-academy
```

### Using Pip

If you don't use Anaconda, you'll have to install these prerequisites first:

* Python 3.7:
	* See notes above about problems with 3.6 and 3.8. Don't use 3.8, but 3.6 may work for you.
    * The version of Python that comes with your operating system is probably too old. Try `python --version` to see what you have.
    * Installation instructions are at [python.org](https://www.python.org/downloads/).
* Pip: A recent version - consider upgrading if it's not the latest version.
	* Installation instructions are at [pip.pypa.io](https://pip.pypa.io/en/stable/installing/).
* Node.js: Required for some of the Jupyter Lab graphics extensions we use.
	* Installation instructions are [here](https://nodejs.org/en/).
* SWIG: Required for building dependencies.
	* Use the package manager of  your system (e.g. `apt` on Ubuntu, `brew` on MacOS) to install, or download [here](http://www.swig.org/download.html).

Next, run the following commands in the root directory of this project to complete the setup. First, run the `pip` command to install the rest of the libraries required for these tutorials, including Ray. Then, run the provided script to install a graphing library extension in Jupyter Lab and perform other tasks.

```shell
pip install -r requirements.txt
tools/fix-jupyter.sh
```

If you are using Windows, see the [**Fixing Jupyter Lab on Windows**](#user-content-fixing-jupyter-lab-on-windows) below for an alternative to using `tools/fix-jupyter.sh`.

### Fixing Jupyter Lab on Windows

The `tools/fix-jupyter.sh` shell script runs the following commands. If you are using Windows, run them yourself as shown here.

First, see if the following `pyviz` extension is installed:

```
jupyter labextension check --installed "@pyviz/jupyterlab_pyviz"
```

If not, run this command:

```
jupyter labextension install "@pyviz/jupyterlab_pyviz"
```

Finally, run these commands:

```
jupyter labextension update --all
jupyter lab build
jupyter labextension list
```

### Final Installation Notes

If you use Jupyter a lot, consider installing [Kite](https://www.kite.com/) on your machine and the Jupter Lab plugin for Kite. Installation and usage instructions are [here](https://help.kite.com/category/138-jupyterlab-plugin).

When you have finished working through the tutorials, run the script `tools/cleanup.sh`, which prints temporary files, checkpoint directories, etc. that were created during the lessons. You might want to remove these as they can add up to 100s of MBs.

> **Note:** A Windows and Mac M1 version are experimental in Ray 1.8.

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
| A developer who is new to Ray | First, [_Ray Crash Course_](ray-crash-course/00-Ray-Crash-Course-Overview.ipynb), then [_Advanced Ray_](advanced-ray/00-Advanced-Ray-Overview.ipynb) |
| A developer who is experienced with Ray | [_Advanced Ray_](advanced-ray/00-Advanced-Ray-Overview.ipynb) |
| A developer or data scientist interested in Reinforcement Learning | [_Ray RLlib_](ray-rllib/00-Ray-RLlib-Overview.ipynb) |
| A developer or data scientist interested in Hyperparameter Tuning  | [_Ray Tune_](ray-tune/00-Ray-Tune-Overview.ipynb) |
| A developer or data scientist interested in distributed training models in PyTorch or TensorFlow | [_Ray Train ](ray-tune/00-Ray-Train-Overview.ipynb)(renamed from Ray SGD)|
| A developer or data scientist interested in model serving | [_Ray Serve_](ray-serve/00-Ray-Serve-Overview.ipynb) |
| A _DevOps_ engineer interested in managing Ray clusters | _Ray Cluster Launcher_ (forthcoming) |

See the [Overview notebook](Overview.ipynb) for detailed, up-to-date descriptions for each tutorial and the lessons it contains.

## Troubleshooting and Further Information

See the [Troubleshooting, Tips, and Tricks](reference/Troubleshooting-Tips-Tricks.ipynb) notebook.

For details on the Ray API and the ML libraries, see the [Ray Docs](https://docs.ray.io/en/latest/). For other information, see [ray.io](https://ray.io), including the [Ray blog](https://medium.com/distributed-computing-with-ray).

[Ray](https://ray.io) started at [U.C. Berkeley RISELab](https://rise.cs.berkeley.edu/). It is now developed in artisanal, small batches at [Anyscale](https://anyscale.com).

## Building Docker Images

> **NOTE:** At this time, the Docker images only run on the Anyscale platform!!

Use the script `tools/make-docker-images.sh` to create two Docker images, `academy-base` and `academy-all`. Use the `--help` option to see the arguments and environment variables it uses. For example, to use a tagged GitHub release of the Academy code, `v1.2.3`:

```
$ tools/make-docker-image.sh v2.0.0-RC1 --docker-tag 2.0.0.1 --docker-tag latest
```

Using the Academy repo tagged release `v2.0.0-RC1`, this command creates two Docker images, each of which is has two "virtual" copies tagged `2.0.0.1` and `latest`. (The copies are identical, so no extra space is actually used. You specify as many as you want.) They are also uploaded to Anyscale's Docker Hub. If you omit the `--docker-tag` argument, the Git tag is used as the image tag, with the `v` removed.

One image is `anyscale/academy-base`, which has everything except the tutorials themselves. It has the required Anaconda environment setup and configured Jupyter Lab environment, etc. The `base` image takes a while to build, but it should only need rebuilding for each new Ray release. The Docker file used is `docker/Dockerfile-academy-base`. Note that a Conda environment is created in this build using `./environment-docker.yml`.

The second image is `anyscale/academy-all`, which is built upon `academy-base`. It has the tutorial materials and builds very quickly compared to `base`. The Docker file used is `docker/Dockerfile-academy-all`.

Use `all` or no arguments (the `make` targets) to build both images and push them to Docker Hub. _You must run `docker login --username ...` before building the `*-upload` targets described next._

Here are the "interesting" targets you might specify to fine tune what's done:

| Target          | Purpose |
| :-------------- | :------ |
| `all`           | Build both images and upload them to Docker Hub (default target). |
| `docker-images` | Build both images, but don't upload them. |
| `docker-upload` | Upload both images. Assumes they are already built. |
| `academy-base`  | Build and upload the `base` image. |
| `academy-all`   | Build and upload the `all` image. |

There are other options you can try to customize what happens. Use the `--help` flag to find out.

> **NOTES:**
>
> 1. When building releases, use `latest` in the list of `DOCKER_TAGS`. The `academy-live-events` repo uses this image tag by default for creating sessions!
> 2. The `make` rules are nontrival. Pass `-n` to print out the expansions of them if you are unfamiliar with `make` syntax or just want to see what commands would be executed.
> 3. If the Docker build errors out with code 137, first try cleaning old images and containers (`docker ps -a; docker rm ...` and `docker images; docker rmi ...`). Next try restarting Docker. What's most likely to work is to increase the memory allocated to the Docker process. On MacOS, use the _Preferences_ to do this. If that doesn't work, try increasing the swap and disk image sizes.

> **WARNING:** It took over a week for me to successfully create the first versions of these Docker images. JupyterLab configurations, in particular, are very fragile with regards to some of the animated graphics in _Ray Crash Course_. So, only modify the builds with great caution and test everything carefully!! Also, note that `environment-docker.yml` hard-codes Python 3.7.7. Using 3.7 causes runtime failures in the Anyscale platform!!!

<a href="https://events.linuxfoundation.org/ray-summit/?utm_source=dean&utm_medium=embed&utm_campaign=ray_summit&utm_content=anyscale_academy">
<img src="images/raysummit-horizontal-white-banner-full.png" alt="Ray Summit 2021"/>
</a>

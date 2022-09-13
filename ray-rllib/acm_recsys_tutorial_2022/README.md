# Welcome to ACM RecSys 2022 Tutorial 

© 2019-2022, Anyscale. All Rights Reserved'

Welcome to the ACM RecSys 2022 training tutorial on Ray, the system for scaling your 
Python and AI/ML applications from a laptop to a cluster.
<br>
<br>

## 📖 Outline for the tutorial

| Lesson| Notebook | Description
|:-----|:-----------|:----------------------------------------------------------|
| 0  | [Optional Intro](intro_gym_and_rllib_optional.ipynb)|Introduction to OpenAI Gym and RLlib|
| 1  | [Tutorial notebook](01_anyscale_acm_recsys_tutorial.ipynb) |Tutorial notebook|
| ex1 | [Exercises](01_anyscale_acm_recsys_tutorial_exercises.ipynb) |Tutorial notebook with exercises |

**NOTE**: Modules and materials in these tutorials have been tested with 
Ray version `2.0`, OpenAI Gym `0.21`, and supported Python `3.7, 3.8, and 3.9`.
<br>
<br>

## 👩 Set up instructions for Anyscale 

There is nothing you need to setup, as the Anyscale hosted environment will provide everything:
all notebooks, data files, and all relevant python packages will be installed on 
the cluster.

However, consider cloning or downloading a release of the tutorial notebooks and 
supporting software from the [Public github](https://github.com/anyscale/academy), 
so you have a local copy of everything.
<br>
<br>

## 💻 Setup instructions for local laptop
This is *optional* if you want to install training material on your laptop at home,
after training is over.


### Using conda
If you need to install Anaconda, follow the instructions [here](https://www.anaconda.com/products/distribution).
If you already have Anaconda installed, consider running conda `upgrade --all.`

1. `conda create -n rllib-recsys-tutorial python=3.8`
2. `conda activate rllib-recsys-tutorial`
3. `git clone https://github.com/christy/acm_recsys_tutorial.git`
4. `cd to <cloned_dir>`
5. `python3 -m pip install -r requirements.txt`
6. `python3 -m ipykernel install`
7. `jupyter lab`


#### If you are using Apple M1 🍎 follow these instructions:

1. `conda create -n rllib-recsys-tutorial python=3.8`
2. `conda activate rllib-recsys-tutorial python`
3. `conda install grpcio`
4. `git clone https://github.com/christy/acm_recsys_tutorial.git`
5. `cd to <cloned_dir>`
6. `python3 -m pip install -r requirements.txt`
7. `python3 -m ipykernel install`
8. `conda install jupyterlab`
9. `jupyter lab`


### Using only pip
1. `git clone https://github.com/christy/acm_recsys_tutorial.git`
2. `cd to <cloned_dir>`
3. `python3 -m pip install -r requirements.txt`
4. `python3 -m ipykernel install`
5. `jupyter lab`

<br>

Let's have 😜 fun @ Anyscale RLlib RecSys Tutorial 2022!

Thank you 🙏











# Welcome to the Anyscale ODSC West 2022 Workshop 

© 2019-2022, Anyscale. All Rights Reserved

![Anyscale Academy](../../images/AnyscaleAcademyLogo.png)

Welcome to the ODSC West 2022 training workshop on Ray, the system for scaling your 
Python and AI/ML applications from a laptop to a cluster.
<br>
<br>

## 📖 Workshop Lessons

## [Let's get Started Learning!](00_anyscale_acm_recsys_tutorial_table_of_contents.ipynb)

<br>

**NOTE**: Materials in these tutorials have been tested with 
Ray version `2.0`, OpenAI Gym `0.21`, and supported Python `3.7, 3.8, and 3.9`.

<br>

## 👩 Set up instructions for Anyscale 

To make the time in class run more smoothly, <b>please email us before class so we can spin up a cloud cluster for you:</b>  christy@anyscale.com. <br>

We will run the worshop on an Anyscale hosted environment which provides everything: slides, notebooks, data files, and all relevant Python packages will be installed on the cluster.  Just show up to class with your login credentials, which you will receive by email ahead of time.  <i>Make sure you email us ahead of time to get your credentials!</i>  <br>

Also consider cloning or downloading this tutorial from the [Public github](https://github.com/anyscale/academy), 
so you have a local copy of everything.
<br>
<br>

## 💻 Setup instructions for local laptop
This is <b>*optional*</b> if you want to install training material on your laptop at home,
after training is over.


### Using conda
If you need to install Anaconda, follow the instructions [here](https://www.anaconda.com/products/distribution).
If you already have Anaconda installed, consider running conda `upgrade --all.`

1. `conda create -y -n rllib-recsys-tutorial python=3.8`
2. `conda activate rllib-recsys-tutorial`
3. `cd to dir above where you want <cloned_dir>`
4. `git clone https://github.com/anyscale/academy.git`
5. `cd academy/ray-rllib/acm_recsys_tutorial_2022`
6. `python3 -m pip install -r requirements.txt`
7. `pip install recsim --no-deps`
8. `pip install git+https://github.com/google/dopamine --no-deps`
9. `python3 -m pip install ipykernel jupyterlab`
10. `jupyter lab`


#### If you are using Apple M1 🍎 follow these instructions:

1. `conda create -y -n rllib-recsys-tutorial python=3.8`
2. `conda activate rllib-recsys-tutorial`
3. `conda install -y grpcio=1.43.0`
4. `conda install -y tensorflow=2.8`
5. `cd to dir above where you want <cloned_dir>`
6. `git clone https://github.com/anyscale/academy.git`
7. `cd academy/ray-rllib/acm_recsys_tutorial_2022`
8. `python3 -m pip install -r requirements.txt`
9. `pip install recsim --no-deps`
10. `pip install git+https://github.com/google/dopamine --no-deps`
11. `python3 -m pip install ipykernel jupyterlab`
12. `jupyter lab`


### Using only pip
1. `cd to dir above where you want <cloned_dir>`
2. `git clone https://github.com/anyscale/academy.git`
3. `cd academy/ray-rllib/acm_recsys_tutorial_2022`
4. `python3 -m pip install -r requirements.txt`
5. `pip install recsim --no-deps`
6. `pip install git+https://github.com/google/dopamine --no-deps`
7. `python3 -m pip install ipykernel jupyterlab`
8. `jupyter lab`

<br>

Let's have 😜 fun @ Anyscale RLlib RecSys Tutorial 2022!

Thank you 🙏


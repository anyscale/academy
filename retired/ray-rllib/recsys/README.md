# RLlib Tutorial: A recommender system based on reinforcement learning

This shows how to build a [*recommender system*](https://en.wikipedia.org/wiki/Recommender_system) 
based on reinforcement learning using [Ray RLlib](https://rllib.io/).
The code+data+docs are intended for use as a tutorial about RLlib for
[Anyscale Academy](https://github.com/anyscale/academy).

While the clustering used for configuration can be performed *offline* 
for periodic updates, otherwise this recommender leverages *online learning*.
Benefits of this approach include:

  * personalization per user, updating based on their most recent ratings
  * scales well: memory requirements are bounded per user and per item
  * simple to adapt for changes in items and users

This approach can be generalized for other use cases which involve
*users/items/ratings*, adapting other data sources.


### Installation

```
pip install -r requirements.txt
```


### Running

Source code for the example recommender system is in `recsys.py` and
to run it with minimal settings (to exercise the code) use:

```
python recsys.py
```

To see the available command line options use:

```
python recsys.py --help
```

A full run takes about 5-10 minutes on a recent model MacBook Pro
laptop.

Alternatively, run the `recsys.ipynb` notebook in Jupyter Lab, Google
Colab, or other similar notebook hosting environments.


### Data Source

Data here comes from the [Jester](https://goldberg.berkeley.edu/jester-data/)
collaborative filtering dataset for an online joke rating system.
For further details about that research project, see:

> [Eigentaste: A Constant Time Collaborative Filtering Algorithm](http://www.ieor.berkeley.edu/~goldberg/pubs/eigentaste.pdf).  
Ken Goldberg, Theresa Roeder, Dhruv Gupta, Chris Perkins.  
*Information Retrieval*, 4(2), 133-151. (July 2001)


### Dependencies

This code was originally developed in 
`Python 3.7.4` on `macOS 0.13.6 (17G14019)`
based on using the following releases of library dependencies related
to [Ray](https://ray.io/):

```
gym >= 0.17.2
numpy >= 1.18.5
pandas >= 1.0.5
paretoset >= 1.1.2
ray >= 1.2
scikit-learn >= 0.21.3
tensorboard >= 2.3.0
tensorflow >= 2.3.0
tqdm >= 4.37.0
```


### Troubleshooting

If you are reviewing a branch of this repo to evaluate a reported
issue, the latest exception trace from the Ray worker (if any) will be
located in `error.txt` in this directory.


### Questions

Contact [@ceteri](https://github.com/ceteri)

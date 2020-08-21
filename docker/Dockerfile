FROM anyscale/ray:0.8.7
COPY environment.yml /tmp/environment.yml
RUN $HOME/anaconda3/bin/conda init bash
RUN $HOME/anaconda3/bin/conda update -n base -c defaults conda
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
	apt-get install -y nodejs
RUN $HOME/anaconda3/bin/conda env create -f /tmp/environment.yml && \
	$HOME/anaconda3/envs/anyscale-academy/bin/jupyter labextension install "@pyviz/jupyterlab_pyviz" && \
	$HOME/anaconda3/envs/anyscale-academy/bin/jupyter labextension update --all && \
	$HOME/anaconda3/envs/anyscale-academy/bin/jupyter lab build

#$HOME/anaconda3/bin/conda activate anyscale-academy &&

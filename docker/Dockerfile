FROM anyscale/ray:0.8.7
ARG VERSION

ADD academy-$VERSION /root/academy-$VERSION
# RUN $HOME/anaconda3/bin/conda init bash
RUN echo '. /root/anaconda3/etc/profile.d/conda.sh' >> $HOME/.bashrc
RUN echo 'PATH=/root/anaconda3/envs/anyscale-academy/bin:$PATH' >> $HOME/.bashrc
RUN echo 'conda deactivate; conda activate anyscale-academy' >> $HOME/.bashrc

RUN $HOME/anaconda3/bin/conda update -n base -c defaults conda
RUN $HOME/anaconda3/bin/conda install -y nodejs
RUN $HOME/anaconda3/bin/conda env create -f /root/academy-$VERSION/environment.yml
# RUN $HOME/anaconda3/bin/conda clean --all
RUN $HOME/anaconda3/envs/anyscale-academy/bin/jupyter labextension install "@pyviz/jupyterlab_pyviz"
RUN $HOME/anaconda3/envs/anyscale-academy/bin/jupyter labextension update --all
RUN $HOME/anaconda3/envs/anyscale-academy/bin/jupyter lab build


FROM anyscale/ray:0.8.7
ARG VERSION
LABEL maintainer="Anyscale Academy <academy@anyscale.com>"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ADD academy-$VERSION /root/academy-$VERSION
# RUN /root/anaconda3/bin/conda init bash
# RUN echo 'PATH=/root/anaconda3/envs/anyscale-academy/bin:$PATH' >> /root/.bashrc
RUN echo 'conda deactivate; conda activate anyscale-academy' >> /root/.bashrc

#RUN /root/anaconda3/bin/conda update -n base -c defaults conda
RUN conda install -y nodejs
RUN /root/anaconda3/bin/conda env create -f /root/academy-$VERSION/environment.yml
RUN /root/anaconda3/envs/anyscale-academy/bin/jupyter labextension install "@pyviz/jupyterlab_pyviz"
RUN /root/anaconda3/envs/anyscale-academy/bin/jupyter labextension update --all
RUN /root/anaconda3/envs/anyscale-academy/bin/jupyter lab build
RUN /root/anaconda3/bin/conda clean --all

WORKDIR /root/academy-$VERSION

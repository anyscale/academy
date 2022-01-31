FROM rayproject/ray:1.9.0
EXPOSE 8000

# pip dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

# runtime
COPY . .
CMD bash -c "ray start --head --node-ip-address 0.0.0.0; python deploy.py; cat /tmp/ray/session_latest/logs/*"

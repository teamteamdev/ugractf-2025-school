FROM imachug/kyzylborda_lib
WORKDIR /ssh
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["python", "ssh_host.py"]
FROM python:2.7
WORKDIR /app
ADD . /app

RUN apt-get update
RUN pip install -r requirements.txt
RUN apt-get install -y net-tools 
RUN apt-get install -y vim 
RUN apt-get install -y openssh-server
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN echo 'root:root' |chpasswd
#RUN service ssh start

WORKDIR /app/apps/02_otsdb_rm_outlier

CMD ["sh", "./start.sh"]
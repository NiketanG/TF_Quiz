FROM python:latest
RUN apt-get update -y && apt-get install -y python3-pip python3-dev
WORKDIR /quiz
ADD . /quiz
EXPOSE 5000
RUN pip3 install -r requirements.txt
CMD [ "flask", "run" ]
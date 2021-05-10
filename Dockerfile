FROM python:3.7.9



RUN pip install --upgrade pip



COPY ./requirements.txt .


RUN pip install -r requirements.txt



COPY ./testDevops /app



WORKDIR /app



COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]


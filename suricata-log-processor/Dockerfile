
FROM python:3.14.5-alpine3.23

WORKDIR /app
COPY requirements.txt  .
RUN pip install -r requirements.txt

COPY params.txt .
COPY *.sh .
COPY *.py .
RUN chmod -x * && chmod +x *.sh

CMD ["/app/entrypoint.sh"]
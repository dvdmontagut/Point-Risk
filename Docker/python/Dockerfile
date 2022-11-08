FROM python:3.9
WORKDIR /app
#COPY par par
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app/par
ENTRYPOINT ["python"]
CMD ["app.py"]
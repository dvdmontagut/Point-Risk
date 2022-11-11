FROM python:3.9

RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.bullseye_amd64.deb
RUN dpkg --force-all -i wkhtmltox_0.12.6.1-2.bullseye_amd64.deb
RUN apt --fix-broken -y install
RUN dpkg --force-all -i wkhtmltox_0.12.6.1-2.bullseye_amd64.deb
RUN ln -s /usr/local/bin/wwkhtmltopdf /usr/bin
RUN ln -s /usr/local/bin/wwkhtmltoimage /usr/bin
WORKDIR /app
#COPY par par
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
WORKDIR /app/par
ENTRYPOINT ["python"]
CMD ["app.py"]
# start by pulling the python image
FROM python:3

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN mkdir log
RUN mkdir data
RUN pip install pip -U && pip install -r requirements.txt
RUN pip install git+https://github.com/ssut/py-hanspell.git
RUN sed -i 's/collections/collections.abc/g' '/usr/local/lib/python3.10/site-packages/jwt/api_jwt.py'
RUN sed -i 's/collections/collections.abc/g' '/usr/local/lib/python3.10/site-packages/jwt/api_jws.py'

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "gunicorn" ]

CMD ["-c", "gunicorn.config.py"]

FROM python:3.7

ADD . /code
WORKDIR /code

RUN pip install poetry
RUN poetry install && \
    poetry run pytest tests -v

# remove configuration folder created from integration tests so they don't get built into the image
# integration tests don't delete/cleanup keys because its destructive, don't want to delete user's keypair just because they ran integration tests
RUN rm -rf ~/.smart-edge-app

RUN useradd app && mkdir /home/app && chown -R app:app /code /home/app
USER app

ENTRYPOINT [ "python", "/code/smart_edge/main.py"]


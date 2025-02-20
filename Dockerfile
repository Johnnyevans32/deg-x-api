# 
FROM python:3.10.1

# 
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV USE_DOCKER=true
# ENV PORT 8000

# 
COPY ./requirements.txt /code/requirements.txt


RUN apt-get update \
    && apt-get install -y sudo

RUN sudo apt-get install -y libsodium-dev libsecp256k1-dev libgmp-dev
# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip uninstall bson --yes
RUN pip uninstall pymongo --yes
RUN pip install pymongo
# 
COPY ./application.py /code/application.py

# 
COPY ./custom_logging.py /code/custom_logging.py
# 
COPY ./apps /code/apps
# 
COPY ./core /code/core
# 
COPY ./solidity /code/solidity

COPY ./scripts/runserver.sh /code/runserver.sh

EXPOSE 8000

# 
CMD ["python", "application.py"]

# CMD ["uvicorn", "application:_app", "--host", "0.0.0.0", "--port", "8000"]
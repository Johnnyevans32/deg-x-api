# 
FROM python:3.10.1

# 
WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV USE_DOCKER=true

# 
COPY ./requirements.txt /code/requirements.txt

# 

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt  --no-deps

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

# 
# CMD ["uvicorn", "application:_app", "--host", "0.0.0.0", "--port", $PORT]

CMD ["sh", "runserver.sh"]

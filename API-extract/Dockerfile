FROM python:3.5-stretch

COPY /whl/* /whl/
RUN pip3.5 install /whl/*

ADD *.py /code/
CMD [ "python3.5", "/code/extract_members.py" ]

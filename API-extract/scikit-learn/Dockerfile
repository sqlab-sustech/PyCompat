FROM python:3.5-stretch

COPY /whl/* /whl/
RUN pip3 install /whl/*.whl && pip3 install /whl/*

ADD *.py /code/
CMD [ "python3", "/code/extract_members.py" ]

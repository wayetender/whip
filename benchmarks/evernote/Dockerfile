FROM wayetender/whip

RUN pip install psutil paste

WORKDIR /benchmarks/evernote
RUN cp /whip/src/adapter/util/test_utils.py .
COPY . .

VOLUME /results

ENTRYPOINT ./run.sh

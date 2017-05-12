FROM wayetender/whip

RUN pip install psutil

WORKDIR /benchmarks/chess
RUN cp /whip/src/adapter/util/test_utils.py .
COPY . .

VOLUME /results

ENTRYPOINT ./run.sh

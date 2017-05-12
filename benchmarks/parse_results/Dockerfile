FROM wayetender/whip

RUN pip install numpy
RUN apt-get update && apt-get install -y gnuplot5

WORKDIR /whip/parsing
COPY parse.py .
COPY plots.sh .
COPY gen_charts.sh .

VOLUME /results

ENTRYPOINT ./gen_charts.sh

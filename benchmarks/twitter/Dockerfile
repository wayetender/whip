FROM wayetender/whip

RUN pip install requests requests-oauthlib psutil

WORKDIR /benchmarks/twitter
RUN cp /whip/src/adapter/util/test_utils.py .
COPY . .
